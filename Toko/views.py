from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import User
from .models import Product, Order, OrderItem, Customer, Cashier, UserProfile, Return
from .forms import CategoryForm, SupplierForm, UserForm, UserProfileForm, ReturnForm
from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models import Sum
from django import forms
from django.template.loader import get_template
from django.http import HttpResponse, HttpResponseForbidden
from xhtml2pdf import pisa
from django.db.models import F
from django.http import JsonResponse


# Custom decorator: hanya kasir yang bisa akses, admin tidak bisa

def home(request):
    return render(request, 'home.html')

def kasir_only(view_func):
    def _wrapped_view(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return redirect('login')
        # Jika user adalah kasir atau admin, izinkan akses
        if hasattr(user, 'userprofile') and (user.userprofile.role == 'kasir' or user.userprofile.role == 'admin'):
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("Anda tidak memiliki akses ke halaman ini.")
    return _wrapped_view

# Custom decorator: hanya admin yang bisa akses, kasir tidak bisa
def admin_only(view_func):
    def _wrapped_view(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return redirect('login')
        if hasattr(user, 'userprofile') and user.userprofile.role == 'admin':
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("Anda tidak memiliki akses ke halaman ini.")
    return _wrapped_view

# Custom LoginView dengan redirect sesuai role
class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def get_success_url(self):
        user = self.request.user
        if hasattr(user, 'userprofile'):
            if user.userprofile.role == 'admin':
                return reverse_lazy('product_list')
            elif user.userprofile.role == 'kasir':
                return reverse_lazy('kasir')
        return reverse_lazy('beranda')

# Form produk
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'cost', 'stock', 'category', 'supplier', 'image']
        
@login_required
def dashboard(request):
    from datetime import timedelta
    today = timezone.now().date()
    start_date = today - timedelta(days=29)
    orders = Order.objects.filter(order_date__date__range=[start_date, today])
    print(list(orders))

    sales_data = (
        orders
        .values('order_date__date')
        .annotate(total=Sum('total'))
        .order_by('order_date__date')
    )
    print(list(sales_data))

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

@login_required
def product_list(request):
    produk_list = Product.objects.all()
    order_items = OrderItem.objects.filter(product__in=produk_list)
    produk_to_orderitem = {}
    for order_item in order_items:
        if order_item.product not in produk_to_orderitem:
            produk_to_orderitem[order_item.product] = order_item
    return render(request, 'product_list.html', {
        'produk_list': produk_list,
        'produk_to_orderitem': produk_to_orderitem,
    })
    
    
@login_required
@admin_only
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'product_form.html', {'form': form})

@login_required
@admin_only
def product_update(request, pk):
    produk = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=produk)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm(instance=produk)
    return render(request, 'product_form.html', {'form': form})

@login_required
@admin_only
def product_delete(request, pk):
    produk = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        produk.delete()
        return redirect('product_list')
    return render(request, 'product_confirm_delete.html', {'produk': produk})

@login_required
@kasir_only
def kasir(request):
    produk_list = Product.objects.all()
    keranjang = request.session.get('keranjang', {})
    keranjang_items = []
    total = 0
    if request.method == 'POST':
        for produk in produk_list:
            qty = int(request.POST.get(f'qty_{produk.pk}', 0))
            if qty > 0:
                keranjang[str(produk.pk)] = qty
            elif str(produk.pk) in keranjang:
                del keranjang[str(produk.pk)]
        request.session['keranjang'] = keranjang

    for pk, qty in keranjang.items():
        produk = get_object_or_404(Product, pk=pk)
        subtotal = produk.price * qty
        keranjang_items.append({'produk': produk, 'qty': qty, 'subtotal': subtotal})
        total += subtotal

    return render(request, 'kasir.html', {
        'produk_list': produk_list,
        'keranjang_items': keranjang_items,
        'total': total
    })

@login_required
@kasir_only
def kasir_checkout(request):
    keranjang = request.session.get('keranjang', {})
    if not keranjang:
        return redirect('kasir')

    # Ambil customer, jika belum ada buat default
    customer = Customer.objects.first()
    if not customer:
        # Buat user default untuk customer umum
        user_customer, created = User.objects.get_or_create(
            username='customer_umum',
            defaults={'first_name': 'Umum', 'last_name': '', 'email': ''} 
        )
        customer = Customer.objects.create(
            user=user_customer,
            phone='-',
            address='-'
        )

    cashier = Cashier.objects.filter(user=request.user).first()
    order = Order.objects.create(
        customer=customer,
        cashier=cashier,
        subtotal=0,
        tax=0,
        discount=0,
        total=0,
        is_paid=True
    )

    total = 0
    order_items = []
    for pk, qty in keranjang.items():
        produk = get_object_or_404(Product, pk=pk)
        subtotal = produk.price * qty
        OrderItem.objects.create(order=order, product=produk, quantity=qty, price=produk.price)
        produk.stock -= qty
        produk.save()
        order_items.append({'produk': produk, 'qty': qty, 'subtotal': subtotal})
        total += subtotal

    order.subtotal = total
    order.total = total
    order.save()

    request.session['keranjang'] = {}

    return render(request, 'kasir_sukses.html', {
        'order': order,
        'order_items': order_items,
        'customer': customer,
        'cashier': cashier,
        'total': total
    })

@login_required
@kasir_only
def cetak_struk(request, order_id):
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

# Manajemen user (admin)
@login_required
@admin_only
def user_list(request):
    users = User.objects.all()
    return render(request, 'user_list.html', {'users': users})

@login_required
@admin_only
def user_create(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            if user_form.cleaned_data['password']:
                user.set_password(user_form.cleaned_data['password'])
            user.save()
            # Ambil UserProfile yang otomatis dibuat oleh signal
            profile = user.userprofile
            profile.role = profile_form.cleaned_data['role']
            profile.save()
            return redirect('user_list')
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    return render(request, 'user_form.html', {'user_form': user_form, 'profile_form': profile_form})

@login_required
@admin_only
def user_update(request, pk):
    user = get_object_or_404(User, pk=pk)
    try:
        profile = user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile(user=user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            if user_form.cleaned_data['password']:
                user.set_password(user_form.cleaned_data['password'])
            user.save()
            profile_form.save()
            return redirect('user_list')
    else:
        user_form = UserForm(instance=user)
        profile_form = UserProfileForm(instance=profile)
    return render(request, 'user_form.html', {'user_form': user_form, 'profile_form': profile_form})

@login_required
def create_return(request, product_id):
    produk = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = ReturnForm(request.POST)
        if form.is_valid():
            order_item = OrderItem.objects.filter(product=produk).first()
            if not order_item:
                return redirect('product_list')
            return_obj = form.save(commit=False)
            return_obj.order_item = order_item
            return_obj.save()
            # Tambah stok saat retur
            produk.stock += form.cleaned_data['quantity']
            produk.save()
            return redirect('product_list')
    else:
        form = ReturnForm()
    return render(request, 'create_return.html', {'form': form, 'produk': produk})

@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)  # Ambil pesanan berdasarkan ID
    return render(request, 'order_detail.html', {'order': order})

@login_required
@kasir_only
def add_by_barcode(request):
    barcode = request.GET.get('barcode')
    if not barcode:
        return JsonResponse({'status': 'error', 'message': 'Barcode tidak ditemukan.'}, status=400)

    try:
        product = Product.objects.get(barcode=barcode)
    except Product.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Produk dengan barcode tersebut tidak ditemukan.'}, status=404)
    
    keranjang = request.session.get('keranjang', {})
    product_pk_str = str(product.pk)

    # Periksa stok sebelum menambahkan
    current_qty_in_cart = keranjang.get(product_pk_str, 0)
    if product.stock <= current_qty_in_cart:
        return JsonResponse({'status': 'error', 'message': f'Stok {product.name} habis atau tidak cukup.'}, status=400)

    keranjang[product_pk_str] = keranjang.get(product_pk_str, 0) + 1
    request.session['keranjang'] = keranjang
    
    # Perbarui session agar perubahan segera disimpan
    request.session.modified = True 

    return JsonResponse({'status': 'success', 'message': 'Produk berhasil ditambahkan ke keranjang.'})

