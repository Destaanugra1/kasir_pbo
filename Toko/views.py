from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView
from django.views import View
from .models import Product, Order, OrderItem, Customer, Cashier, UserProfile, Return
from .forms import CategoryForm, SupplierForm, UserForm, UserProfileForm, ReturnForm
from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models import Sum
from django import forms
from django.template.loader import get_template
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from xhtml2pdf import pisa
from django.db.models import F
from django.views.decorators.http import require_POST, require_GET
from django.db import transaction
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


# Base Mixins for Role-Based Access Control
class RoleRequiredMixin:
    """Base mixin for role-based access control"""
    required_roles = []
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if not hasattr(request.user, 'userprofile'):
            return HttpResponseForbidden("Profil pengguna tidak ditemukan.")
        
        user_role = request.user.userprofile.role
        if self.required_roles and user_role not in self.required_roles:
            return HttpResponseForbidden("Anda tidak memiliki akses ke halaman ini.")
        
        return super().dispatch(request, *args, **kwargs)

class AdminRequiredMixin(RoleRequiredMixin):
    """Mixin untuk akses admin saja"""
    required_roles = ['admin']

class KasirRequiredMixin(RoleRequiredMixin):
    """Mixin untuk akses kasir atau admin"""
    required_roles = ['kasir', 'admin']

# Base Views Classes
class BaseView(LoginRequiredMixin, View):
    """Base view class dengan login required"""
    login_url = 'login'

class BaseTemplateView(LoginRequiredMixin, TemplateView):
    """Base template view dengan login required"""
    login_url = 'login'

class BaseListView(LoginRequiredMixin, ListView):
    """Base list view dengan login required"""
    login_url = 'login'
    paginate_by = 10

class BaseCreateView(LoginRequiredMixin, CreateView):
    """Base create view dengan login required"""
    login_url = 'login'

class BaseUpdateView(LoginRequiredMixin, UpdateView):
    """Base update view dengan login required"""
    login_url = 'login'

class BaseDeleteView(LoginRequiredMixin, DeleteView):
    """Base delete view dengan login required"""
    login_url = 'login'

class BaseDetailView(LoginRequiredMixin, DetailView):
    """Base detail view dengan login required"""
    login_url = 'login'

# Home and Navigation Views
class HomeView(BaseTemplateView):
    """Home view"""
    template_name = 'home.html'

class BerandaView(BaseTemplateView):
    """Beranda view dengan daftar produk"""
    template_name = 'beranda.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['produk_list'] = Product.objects.all()
        return context

# Custom LoginView dengan redirect sesuai role
class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def get_success_url(self):
        user = self.request.user
        if hasattr(user, 'userprofile'):
            if user.userprofile.role == 'admin':
                return reverse_lazy('product_list')
            elif user.userprofile.role == 'kasir':
                return reverse_lazy('kasir') # Menggunakan nama URL 'kasir' sesuai yang Anda berikan
        return reverse_lazy('beranda')

# Form produk
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'cost', 'stock', 'category', 'supplier', 'image', 'barcode'] # Pastikan 'barcode' ada di sini
        
@login_required
def dashboard(request):
    from datetime import timedelta
    today = timezone.now().date()
    start_date = today - timedelta(days=29)
    orders = Order.objects.filter(order_date__date__range=[start_date, today])

    sales_data = (
        orders
        .values('order_date__date')
        .annotate(total=Sum('total'))
        .order_by('order_date__date')
    )

    labels = []
    data = []
    for i in range(30):
        day = start_date + timedelta(days=i)
        labels.append(day.strftime('%d-%m'))
        found = next((item for item in sales_data if item['order_date__date'] == day), None)
        data.append(float(found['total']) if found else 0)

    category_sales = (
        OrderItem.objects
        .filter(order__order_date__date__range=[start_date, today])
        .values(category_name=F('product__category__name'))
        .annotate(jumlah=Sum('quantity'))
        .order_by('category_name')
    )
    bar_labels = [item['category_name'] for item in category_sales]
    bar_data = [item['jumlah'] for item in category_sales]

    context = {
        'labels': labels,
        'data': data,
        'bar_labels': bar_labels,
        'bar_data': bar_data,
    }
    return render(request, 'dashboard.html', context)

@login_required
def beranda(request):
    produk_list = Product.objects.all()
    return render(request, 'beranda.html', {'produk_list': produk_list})

# Product Views
class ProductListView(BaseListView):
    """Product list view with pagination"""
    model = Product
    template_name = 'product_list.html'
    context_object_name = 'produk_list'
    paginate_by = 5
    ordering = ['-id']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        produk_list = context['produk_list']
        
        # Get order items for each product
        order_items = OrderItem.objects.filter(product__in=produk_list)
        produk_to_orderitem = {}
        for order_item in order_items:
            if order_item.product not in produk_to_orderitem:
                produk_to_orderitem[order_item.product] = order_item
        
        context['produk_to_orderitem'] = produk_to_orderitem
        return context

class ProductCreateView(AdminRequiredMixin, BaseCreateView):
    """Product create view - admin only"""
    model = Product
    form_class = ProductForm
    template_name = 'product_form.html'
    success_url = reverse_lazy('product_list')

class ProductUpdateView(AdminRequiredMixin, BaseUpdateView):
    """Product update view - admin only"""
    model = Product
    form_class = ProductForm
    template_name = 'product_form.html'
    success_url = reverse_lazy('product_list')

class ProductDeleteView(AdminRequiredMixin, BaseDeleteView):
    """Product delete view - admin only"""
    model = Product
    template_name = 'product_confirm_delete.html'
    success_url = reverse_lazy('product_list')
    context_object_name = 'produk'

# Cashier Views
class KasirView(KasirRequiredMixin, BaseTemplateView):
    """Main cashier view"""
    template_name = 'kasir.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        keranjang = self.request.session.get('keranjang', {})
        keranjang_items = []
        total = 0

        for pk, qty in keranjang.items():
            try:
                produk = get_object_or_404(Product, pk=pk)
                # Pastikan kuantitas di keranjang tidak melebihi stok yang ada
                if qty > produk.stock:
                    qty = produk.stock
                    keranjang[pk] = qty
                    self.request.session.modified = True
                if qty <= 0:
                    del keranjang[pk]
                    self.request.session.modified = True
                    continue

                subtotal = produk.price * qty
                keranjang_items.append({'produk': produk, 'qty': qty, 'subtotal': subtotal})
                total += subtotal
            except Product.DoesNotExist:
                if pk in keranjang:
                    del keranjang[pk]
                    self.request.session.modified = True
                continue

        context['keranjang_items'] = keranjang_items
        context['total'] = total
        return context

class GetProductByBarcodeView(KasirRequiredMixin, BaseView):
    """Get product by barcode for cashier"""
    
    def get(self, request, *args, **kwargs):
        barcode = request.GET.get('barcode')
        if not barcode:
            return JsonResponse({'status': 'error', 'message': 'Barcode tidak disediakan.'}, status=400)

        try:
            product = Product.objects.get(barcode=barcode)
            keranjang = request.session.get('keranjang', {})
            product_pk_str = str(product.pk)
            
            current_qty_in_cart = keranjang.get(product_pk_str, 0)
            
            # Cek stok
            if product.stock <= 0:
                return JsonResponse({'status': 'error', 'message': f'Stok {product.name} habis.'}, status=400)
            
            # Jika kuantitas saat ini di keranjang sudah mencapai stok maksimal
            if current_qty_in_cart >= product.stock:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Stok {product.name} di keranjang sudah maksimal ({product.stock}).',
                    'product_id': product.pk,
                    'product_name': product.name
                })

            # Tambahkan 1 ke kuantitas di keranjang
            new_qty = current_qty_in_cart + 1
            keranjang[product_pk_str] = new_qty
            request.session['keranjang'] = keranjang
            request.session.modified = True

            # Hitung ulang total dan jumlah item
            total_amount, current_cart_item_count = self._calculate_cart_totals(request)

            return JsonResponse({
                'status': 'success',
                'product_id': product.pk,
                'product_name': product.name,
                'product_price': float(product.price),
                'product_stock': product.stock,
                'new_qty_in_cart': new_qty,
                'total_amount': float(total_amount),
                'total_items': current_cart_item_count
            })

        except Product.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': f'Produk dengan barcode "{barcode}" tidak ditemukan.'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Terjadi kesalahan server: {str(e)}'}, status=500)
    
    def _calculate_cart_totals(self, request):
        """Calculate total amount and item count in cart"""
        keranjang = request.session.get('keranjang', {})
        total_amount = 0
        current_cart_item_count = 0
        
        for pk, qty in keranjang.items():
            try:
                p = Product.objects.get(pk=pk)
                total_amount += p.price * qty
                current_cart_item_count += qty  # Changed this line to add quantity instead of 1
            except Product.DoesNotExist:
                pass
        
        return total_amount, current_cart_item_count

class AddByBarcodeView(KasirRequiredMixin, BaseView):
    """Add product by barcode"""
    
    def post(self, request, *args, **kwargs):
        barcode = request.POST.get('barcode')
        if not barcode:
            return JsonResponse({'status': 'error', 'message': 'Barcode tidak disediakan.'})
        
        try:
            product = Product.objects.get(barcode=barcode)
            keranjang = request.session.get('keranjang', {})
            product_pk_str = str(product.pk)
            
            current_qty_in_cart = keranjang.get(product_pk_str, 0)
            if current_qty_in_cart < product.stock:
                keranjang[product_pk_str] = current_qty_in_cart + 1
                request.session['keranjang'] = keranjang
                request.session.modified = True
                return JsonResponse({'status': 'success', 'message': f'Produk "{product.name}" ditambahkan.'})
            else:
                return JsonResponse({'status': 'error', 'message': f'Stok {product.name} habis atau tidak cukup.'})
                
        except Product.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': f'Produk dengan barcode "{barcode}" tidak ditemukan.'})
        
        return JsonResponse({'status': 'error', 'message': 'Metode tidak diizinkan.'}, status=405)

class UpdateCartQuantityView(KasirRequiredMixin, BaseView):
    """Update cart quantity via AJAX"""
    
    def post(self, request, *args, **kwargs):
        product_id = request.POST.get('product_id')
        new_qty = int(request.POST.get('new_qty', 0))

        if not product_id:
            return JsonResponse({'status': 'error', 'message': 'ID Produk tidak disediakan.'}, status=400)

        try:
            product = get_object_or_404(Product, pk=product_id)
            keranjang = request.session.get('keranjang', {})
            product_pk_str = str(product.pk)

            if new_qty < 0:
                new_qty = 0
            if new_qty > product.stock:
                new_qty = product.stock

            if new_qty == 0:
                if product_pk_str in keranjang:
                    del keranjang[product_pk_str]
            else:
                keranjang[product_pk_str] = new_qty

            request.session['keranjang'] = keranjang
            request.session.modified = True

            # Hitung ulang total dan jumlah item
            total_amount, current_cart_item_count = self._calculate_cart_totals(request)

            return JsonResponse({
                'status': 'success',
                'product_id': product.pk,
                'product_name': product.name,
                'new_qty_in_cart': new_qty,
                'product_price': float(product.price),
                'product_stock': product.stock,
                'subtotal': float(product.price * new_qty),
                'total_amount': float(total_amount),
                'total_items': current_cart_item_count,
                'message': f'Kuantitas {product.name} diperbarui menjadi {new_qty}.'
            })

        except Product.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Produk tidak ditemukan.'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Terjadi kesalahan server: {str(e)}'}, status=500)
    
    def _calculate_cart_totals(self, request):
        """Calculate total amount and item count in cart"""
        keranjang = request.session.get('keranjang', {})
        total_amount = 0
        current_cart_item_count = 0
        
        for pk, qty in keranjang.items():
            try:
                p = Product.objects.get(pk=pk)
                total_amount += p.price * qty
                current_cart_item_count += qty  # Changed this line to add quantity instead of 1
            except Product.DoesNotExist:
                pass
        
        return total_amount, current_cart_item_count

class RemoveItemFromCartView(KasirRequiredMixin, BaseView):
    """Remove item from cart via AJAX"""
    
    def post(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            product_id = request.POST.get('product_id')
            if product_id:
                keranjang = request.session.get('keranjang', {})
                if product_id in keranjang:
                    del keranjang[product_id]
                    request.session['keranjang'] = keranjang
                    request.session.modified = True
                    
                    # Hitung ulang total dan jumlah item
                    total_amount, current_cart_item_count = self._calculate_cart_totals(request)

                    return JsonResponse({
                        'status': 'success',
                        'message': 'Produk berhasil dihapus dari keranjang.',
                        'total_items': current_cart_item_count,
                        'total_amount': float(total_amount)
                    })
                else:
                    return JsonResponse({'status': 'error', 'message': 'Produk tidak ada di keranjang.'}, status=404)
            return JsonResponse({'status': 'error', 'message': 'ID produk tidak disediakan.'}, status=400)
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
    
    def _calculate_cart_totals(self, request):
        """Calculate total amount and item count in cart"""
        keranjang = request.session.get('keranjang', {})
        total_amount = 0
        current_cart_item_count = 0
        
        for pk, qty in keranjang.items():
            try:
                produk = Product.objects.get(pk=pk)
                total_amount += produk.price * qty
                current_cart_item_count += qty  # Changed this line to add quantity instead of 1
            except Product.DoesNotExist:
                pass
        
        return total_amount, current_cart_item_count


# Checkout and Order Views
class KasirCheckoutView(KasirRequiredMixin, BaseView):
    """Kasir checkout view"""
    
    def post(self, request, *args, **kwargs):
        keranjang = request.session.get('keranjang', {})
        if not keranjang:
            return redirect('kasir')

        try:
            with transaction.atomic():
                # Get or create customer
                customer = self._get_or_create_customer()
                
                # Get or create cashier
                cashier = self._get_or_create_cashier(request.user)
                
                # Create order
                order = Order.objects.create(
                    customer=customer,
                    cashier=cashier,
                    subtotal=0,
                    tax=0,
                    discount=0,
                    total=0,
                    is_paid=True
                )

                total_checkout = 0
                order_items_for_template = []
                products_to_update_stock = []

                # Process cart items
                for pk_str, qty in keranjang.items():
                    try:
                        produk = get_object_or_404(Product, pk=pk_str)
                        
                        # Check stock
                        if produk.stock < qty:
                            transaction.set_rollback(True)
                            return self._render_kasir_with_error(
                                request, 
                                f"Stok {produk.name} tidak cukup! Sisa stok: {produk.stock}"
                            )
                        
                        # Create order item
                        subtotal_item = produk.price * qty
                        OrderItem.objects.create(
                            order=order, 
                            product=produk, 
                            quantity=qty, 
                            price=produk.price
                        )
                        
                        # Update stock
                        produk.stock -= qty
                        products_to_update_stock.append(produk)

                        order_items_for_template.append({
                            'produk': produk, 
                            'qty': qty, 
                            'subtotal': subtotal_item
                        })
                        total_checkout += subtotal_item

                    except Product.DoesNotExist:
                        transaction.set_rollback(True)
                        return self._render_kasir_with_error(
                            request, 
                            f"Produk dengan ID {pk_str} tidak ditemukan."
                        )
                    except Exception as e:
                        transaction.set_rollback(True)
                        return self._render_kasir_with_error(
                            request, 
                            f"Terjadi kesalahan saat memproses produk {pk_str}: {e}"
                        )
                
                # Save product stock updates
                for p_to_update in products_to_update_stock:
                    p_to_update.save()

                # Update order total
                order.subtotal = total_checkout
                order.total = total_checkout
                order.save()

                # Clear cart
                request.session['keranjang'] = {}
                request.session.modified = True

                return render(request, 'kasir_sukses.html', {
                    'order': order,
                    'order_items': order_items_for_template,
                    'customer': customer,
                    'cashier': cashier,
                    'total': total_checkout
                })

        except Exception as e:
            return self._render_kasir_with_error(request, f"Terjadi kesalahan sistem: {e}")
    
    def get(self, request, *args, **kwargs):
        return redirect('kasir')
    
    def _get_or_create_customer(self):
        """Get or create default customer"""
        customer = Customer.objects.first()
        if not customer:
            user_customer, created = User.objects.get_or_create(
                username='customer_umum',
                defaults={'first_name': 'Umum', 'last_name': '', 'email': ''}
            )
            customer = Customer.objects.create(
                user=user_customer,
                phone='-',
                address='-'
            )
        return customer
    
    def _get_or_create_cashier(self, user):
        """Get or create cashier for user"""
        cashier = Cashier.objects.filter(user=user).first()
        if not cashier:
            cashier = Cashier.objects.create(user=user)
        return cashier
    
    def _render_kasir_with_error(self, request, error_message):
        """Render kasir page with error message"""
        keranjang = request.session.get('keranjang', {})
        keranjang_items_error, total_error = [], 0
        
        for p, q in keranjang.items():
            try:
                prod_obj = Product.objects.get(pk=p)
                keranjang_items_error.append({
                    'produk': prod_obj, 
                    'qty': q, 
                    'subtotal': prod_obj.price * q
                })
                total_error += prod_obj.price * q
            except Product.DoesNotExist:
                pass
        
        return render(request, 'kasir.html', {
            'keranjang_items': keranjang_items_error,
            'total': total_error,
            'error_message': error_message
        })

class CetakStrukView(KasirRequiredMixin, BaseView):
    """Print receipt view"""
    
    def get(self, request, order_id, *args, **kwargs):
        order = get_object_or_404(Order, pk=order_id)
        order_items = OrderItem.objects.filter(order=order)
        customer = order.customer
        cashier = order.cashier

        template = get_template('struk_pdf.html')
        html = template.render({
            'order': order,
            'order_items': order_items,
            'customer': customer,
            'cashier': cashier,
            'total': order.total
        })

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="struk_{order.id}.pdf"'
        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse('PDF generation failed')
        return response

class OrderDetailView(BaseDetailView):
    """Order detail view"""
    model = Order
    template_name = 'order_detail.html'
    context_object_name = 'order'

# User Management Views
class UserListView(AdminRequiredMixin, BaseListView):
    """User list view - admin only"""
    model = User
    template_name = 'user_list.html'
    context_object_name = 'users'

class UserCreateView(AdminRequiredMixin, BaseView):
    """User create view - admin only"""
    
    def get(self, request, *args, **kwargs):
        user_form = UserForm()
        profile_form = UserProfileForm()
        return render(request, 'user_form.html', {
            'user_form': user_form, 
            'profile_form': profile_form
        })
    
    def post(self, request, *args, **kwargs):
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            if user_form.cleaned_data['password']:
                user.set_password(user_form.cleaned_data['password'])
            user.save()
            
            # Get UserProfile created by signal
            profile = user.userprofile
            profile.role = profile_form.cleaned_data['role']
            profile.save()
            
            return redirect('user_list')
        
        return render(request, 'user_form.html', {
            'user_form': user_form, 
            'profile_form': profile_form
        })

class UserUpdateView(AdminRequiredMixin, BaseView):
    """User update view - admin only"""
    
    def get(self, request, pk, *args, **kwargs):
        user = get_object_or_404(User, pk=pk)
        try:
            profile = user.userprofile
        except UserProfile.DoesNotExist:
            profile = UserProfile(user=user)
        
        user_form = UserForm(instance=user)
        profile_form = UserProfileForm(instance=profile)
        
        return render(request, 'user_form.html', {
            'user_form': user_form, 
            'profile_form': profile_form
        })
    
    def post(self, request, pk, *args, **kwargs):
        user = get_object_or_404(User, pk=pk)
        try:
            profile = user.userprofile
        except UserProfile.DoesNotExist:
            profile = UserProfile(user=user)
        
        user_form = UserForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            if user_form.cleaned_data['password']:
                user.set_password(user_form.cleaned_data['password'])
            user.save()
            profile_form.save()
            return redirect('user_list')
        
        return render(request, 'user_form.html', {
            'user_form': user_form, 
            'profile_form': profile_form
        })

# Return Management Views
class CreateReturnView(BaseView):
    """Create return view"""
    
    def get(self, request, product_id, *args, **kwargs):
        produk = get_object_or_404(Product, pk=product_id)
        form = ReturnForm()
        return render(request, 'create_return.html', {
            'form': form, 
            'produk': produk
        })
    
    def post(self, request, product_id, *args, **kwargs):
        produk = get_object_or_404(Product, pk=product_id)
        form = ReturnForm(request.POST)
        
        if form.is_valid():
            order_item = OrderItem.objects.filter(product=produk).first()
            if not order_item:
                return redirect('product_list')
            
            return_obj = form.save(commit=False)
            return_obj.order_item = order_item
            return_obj.save()
            
            # Add stock when return
            produk.stock += form.cleaned_data['quantity']
            produk.save()
            
            return redirect('product_list')
        
        return render(request, 'create_return.html', {
            'form': form, 
            'produk': produk
        })

# Dashboard View
class DashboardView(BaseTemplateView):
    """Dashboard view with sales analytics"""
    template_name = 'dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Sales data for last 30 days
        from datetime import timedelta
        today = timezone.now().date()
        start_date = today - timedelta(days=29)
        orders = Order.objects.filter(order_date__date__range=[start_date, today])

        sales_data = (
            orders
            .values('order_date__date')
            .annotate(total=Sum('total'))
            .order_by('order_date__date')
        )

        # Prepare chart data
        labels = []
        data = []
        for i in range(30):
            day = start_date + timedelta(days=i)
            labels.append(day.strftime('%d-%m'))
            found = next((item for item in sales_data if item['order_date__date'] == day), None)
            data.append(float(found['total']) if found else 0)

        # Category sales data
        category_sales = (
            OrderItem.objects
            .filter(order__order_date__date__range=[start_date, today])
            .values(category_name=F('product__category__name'))
            .annotate(jumlah=Sum('quantity'))
            .order_by('category_name')
        )
        
        bar_labels = [item['category_name'] for item in category_sales]
        bar_data = [item['jumlah'] for item in category_sales]

        context.update({
            'labels': labels,
            'data': data,
            'bar_labels': bar_labels,
            'bar_data': bar_data,
        })
        
        return context

# Decorator functions for backward compatibility
def kasir_only(view_func):
    """Decorator for kasir only access"""
    def _wrapped_view(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return redirect('login')
        if hasattr(user, 'userprofile') and (user.userprofile.role == 'kasir' or user.userprofile.role == 'admin'):
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("Anda tidak memiliki akses ke halaman ini.")
    return _wrapped_view

def admin_only(view_func):
    """Decorator for admin only access"""
    def _wrapped_view(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return redirect('login')
        if hasattr(user, 'userprofile') and user.userprofile.role == 'admin':
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("Anda tidak memiliki akses ke halaman ini.")
    return _wrapped_view

# Legacy function-based views (keeping for backward compatibility)
def home(request):
    """Legacy home view"""
    return render(request, 'home.html')

@login_required
def beranda(request):
    """Legacy beranda view"""
    produk_list = Product.objects.all()
    return render(request, 'beranda.html', {'produk_list': produk_list})

@login_required
def dashboard(request):
    """Legacy dashboard view"""
    view = DashboardView()
    view.request = request
    return view.get(request)

@login_required
def product_list(request):
    """Legacy product list view"""
    view = ProductListView()
    view.request = request
    return view.get(request)

@login_required
@admin_only
def product_create(request):
    """Legacy product create view"""
    view = ProductCreateView()
    view.request = request
    if request.method == 'POST':
        return view.post(request)
    return view.get(request)

@login_required
@admin_only
def product_update(request, pk):
    """Legacy product update view"""
    view = ProductUpdateView()
    view.request = request
    view.kwargs = {'pk': pk}
    if request.method == 'POST':
        return view.post(request, pk)
    return view.get(request, pk)

@login_required
@admin_only
def product_delete(request, pk):
    """Legacy product delete view"""
    view = ProductDeleteView()
    view.request = request
    view.kwargs = {'pk': pk}
    if request.method == 'POST':
        return view.post(request, pk)
    return view.get(request, pk)

@login_required
@kasir_only
def kasir(request):
    """Legacy kasir view"""
    view = KasirView()
    view.request = request
    return view.get(request)

@require_GET
@login_required
@kasir_only
def get_product_by_barcode(request):
    """Legacy get product by barcode view"""
    view = GetProductByBarcodeView()
    view.request = request
    return view.get(request)

@login_required
@kasir_only
def add_by_barcode(request):
    """Legacy add by barcode view"""
    view = AddByBarcodeView()
    view.request = request
    return view.post(request)

@require_POST
@login_required
@kasir_only
def update_cart_quantity(request):
    """Legacy update cart quantity view"""
    view = UpdateCartQuantityView()
    view.request = request
    return view.post(request)

@require_POST
@login_required
@kasir_only
def remove_item_from_cart(request):
    """Legacy remove item from cart view"""
    view = RemoveItemFromCartView()
    view.request = request
    return view.post(request)

@login_required
@kasir_only
def kasir_checkout(request):
    """Legacy kasir checkout view"""
    view = KasirCheckoutView()
    view.request = request
    return view.post(request)

@login_required
@kasir_only
def cetak_struk(request, order_id):
    """Legacy cetak struk view"""
    view = CetakStrukView()
    view.request = request
    return view.get(request, order_id)

@login_required
@admin_only
def user_list(request):
    """Legacy user list view"""
    view = UserListView()
    view.request = request
    return view.get(request)

@login_required
@admin_only
def user_create(request):
    """Legacy user create view"""
    view = UserCreateView()
    view.request = request
    if request.method == 'POST':
        return view.post(request)
    return view.get(request)

@login_required
@admin_only
def user_update(request, pk):
    """Legacy user update view"""
    view = UserUpdateView()
    view.request = request
    if request.method == 'POST':
        return view.post(request, pk)
    return view.get(request, pk)

@login_required
def create_return(request, product_id):
    """Legacy create return view"""
    view = CreateReturnView()
    view.request = request
    if request.method == 'POST':
        return view.post(request, product_id)
    return view.get(request, product_id)

@login_required
def order_detail(request, pk):
    """Legacy order detail view"""
    view = OrderDetailView()
    view.request = request
    view.kwargs = {'pk': pk}
    return view.get(request, pk)