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
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from xhtml2pdf import pisa
from django.db.models import F
from django.views.decorators.http import require_POST, require_GET
from django.db import transaction


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
    # View kasir ini hanya bertugas untuk menampilkan halaman awal
    # dengan data keranjang yang ada di sesi. Semua interaksi
    # penambahan/pengurangan/penghapusan produk akan via AJAX.

    keranjang = request.session.get('keranjang', {})
    keranjang_items = []
    total = 0

    for pk, qty in keranjang.items():
        try:
            produk = get_object_or_404(Product, pk=pk)
            # Pastikan kuantitas di keranjang tidak melebihi stok yang ada
            if qty > produk.stock:
                qty = produk.stock # Sesuaikan kuantitas di sesi jika lebih dari stok
                keranjang[pk] = qty
                request.session.modified = True # Penting untuk menyimpan perubahan sesi
            if qty <= 0: # Hapus jika kuantitas jadi 0
                del keranjang[pk]
                request.session.modified = True
                continue

            subtotal = produk.price * qty
            keranjang_items.append({'produk': produk, 'qty': qty, 'subtotal': subtotal})
            total += subtotal
        except Product.DoesNotExist:
            # Jika produk tidak ditemukan (mungkin sudah dihapus dari DB), hapus dari keranjang sesi
            if pk in keranjang:
                del keranjang[pk]
                request.session.modified = True
            continue # Lanjutkan ke item berikutnya

    return render(request, 'kasir.html', {
        'keranjang_items': keranjang_items,
        'total': total
    })

# Ini adalah endpoint yang akan dipanggil oleh scanner barcode.
# Fungsi ini akan menambah/mengupdate produk di sesi keranjang
# dan mengembalikan data produk yang diperlukan untuk update UI dinamis.
@require_GET
@login_required
@kasir_only
def get_product_by_barcode(request): # Nama fungsi sesuai dengan yang ada di urls.py Anda
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
        
        # Jika kuantitas saat ini di keranjang sudah mencapai stok maksimal, tolak penambahan
        if current_qty_in_cart >= product.stock:
             return JsonResponse({
                'status': 'error',
                'message': f'Stok {product.name} di keranjang sudah maksimal ({product.stock}).',
                'product_id': product.pk, # Tetap kembalikan ID untuk identifikasi di frontend
                'product_name': product.name
            })

        # Tambahkan 1 ke kuantitas di keranjang
        new_qty = current_qty_in_cart + 1
        keranjang[product_pk_str] = new_qty
        request.session['keranjang'] = keranjang
        request.session.modified = True # Penting untuk menyimpan perubahan sesi

        # Hitung ulang total dan jumlah item setelah penambahan
        total_amount = 0
        current_cart_item_count = 0
        for pk, qty in keranjang.items():
            try:
                p = Product.objects.get(pk=pk)
                total_amount += p.price * qty
                current_cart_item_count += 1 # Hitung item yang valid
            except Product.DoesNotExist:
                pass # Abaikan item yang tidak valid di keranjang sesi

        return JsonResponse({
            'status': 'success',
            'product_id': product.pk,
            'product_name': product.name,
            'product_price': float(product.price), # Menggunakan float() untuk DecimalField
            'product_stock': product.stock,
            'new_qty_in_cart': new_qty,
            'total_amount': float(total_amount),
            'total_items': current_cart_item_count
        })

    except Product.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': f'Produk dengan barcode "{barcode}" tidak ditemukan.'}, status=404)
    except Exception as e:
        print(f"Error in get_product_by_barcode: {e}")
        return JsonResponse({'status': 'error', 'message': f'Terjadi kesalahan server: {str(e)}'}, status=500)

# Karena di urls.py Anda ada `kasir/add-barcode/`, saya akan definisikan ini
# agar tidak ada AttributeError. Namun, fungsi ini mungkin tidak terpakai
# jika semua penambahan ditangani oleh `get_product_by_barcode`.
# Jika Anda berencana menggunakan ini untuk menambah 1 per klik,
# maka logika di dalamnya perlu ditambahkan. Saat ini, saya akan membuatnya
# mengembalikan pesan sederhana atau redirect ke kasir.
@login_required
@kasir_only
def add_by_barcode(request): # Nama fungsi sesuai dengan yang ada di urls.py Anda
    # Ini mungkin tidak akan terpanggil jika scanner langsung memanggil get_product_by_barcode
    # dan Anda tidak memiliki tombol lain yang mengarah ke sini.
    # Namun, saya tetap definisikan untuk menghindari AttributeError.
    
    # Anda bisa tambahkan logika di sini jika fungsi ini memang ingin digunakan
    # Misalnya, jika ada input manual barcode dan tombol "Tambah"
    if request.method == 'POST':
        barcode = request.POST.get('barcode')
        if barcode:
            try:
                product = Product.objects.get(barcode=barcode)
                keranjang = request.session.get('keranjang', {})
                product_pk_str = str(product.pk)
                
                # Tambah 1 ke keranjang, mirip dengan logika di get_product_by_barcode
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
        return JsonResponse({'status': 'error', 'message': 'Barcode tidak disediakan.'})
    return JsonResponse({'status': 'error', 'message': 'Metode tidak diizinkan.'}, status=405)


# >>> View untuk update kuantitas via AJAX (increase/decrease) <<<
# URL untuk ini adalah 'api/update-cart-quantity/' yang mungkin perlu di-include secara terpisah.
@require_POST
@login_required
@kasir_only
def update_cart_quantity(request):
    product_id = request.POST.get('product_id')
    new_qty = int(request.POST.get('new_qty', 0))

    if not product_id:
        return JsonResponse({'status': 'error', 'message': 'ID Produk tidak disediakan.'}, status=400)

    try:
        product = get_object_or_404(Product, pk=product_id)
        keranjang = request.session.get('keranjang', {})
        product_pk_str = str(product.pk)

        if new_qty < 0:
            new_qty = 0 # Kuantitas tidak boleh negatif
        if new_qty > product.stock:
            new_qty = product.stock # Kuantitas tidak boleh melebihi stok

        if new_qty == 0:
            if product_pk_str in keranjang:
                del keranjang[product_pk_str]
        else:
            keranjang[product_pk_str] = new_qty

        request.session['keranjang'] = keranjang
        request.session.modified = True

        # Hitung ulang total dan jumlah item
        total_amount = 0
        current_cart_item_count = 0
        for pk, qty in keranjang.items():
            try:
                p = Product.objects.get(pk=pk)
                total_amount += p.price * qty
                current_cart_item_count += 1
            except Product.DoesNotExist:
                pass

        return JsonResponse({
            'status': 'success',
            'product_id': product.pk,
            'product_name': product.name,
            'new_qty_in_cart': new_qty,
            'subtotal': float(product.price * new_qty),
            'total_amount': float(total_amount),
            'total_items': current_cart_item_count,
            'message': f'Kuantitas {product.name} diperbarui menjadi {new_qty}.'
        })

    except Product.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Produk tidak ditemukan.'}, status=404)
    except Exception as e:
        print(f"Error in update_cart_quantity: {e}")
        return JsonResponse({'status': 'error', 'message': f'Terjadi kesalahan server: {str(e)}'}, status=500)


# >>> View untuk menghapus item dari keranjang via AJAX <<<
# URL untuk ini adalah 'api/remove-item-from-cart/' yang mungkin perlu di-include secara terpisah.
@require_POST
@login_required
@kasir_only
def remove_item_from_cart(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest': # Pastikan ini AJAX request
        product_id = request.POST.get('product_id')
        if product_id:
            keranjang = request.session.get('keranjang', {})
            if product_id in keranjang:
                del keranjang[product_id]
                request.session['keranjang'] = keranjang
                request.session.modified = True
                
                # Hitung ulang total dan jumlah item setelah penghapusan
                total_amount = 0
                current_cart_item_count = 0
                for pk, qty in keranjang.items():
                    try:
                        produk = Product.objects.get(pk=pk) 
                        total_amount += produk.price * qty
                        current_cart_item_count += 1
                    except Product.DoesNotExist:
                        pass 

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


@login_required
@kasir_only
def kasir_checkout(request):
    keranjang = request.session.get('keranjang', {})
    if not keranjang:
        return redirect('kasir') # Menggunakan nama URL 'kasir' sesuai yang Anda berikan

    with transaction.atomic(): # Pastikan operasi ini bersifat atomik
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

        cashier = Cashier.objects.filter(user=request.user).first()
        if not cashier:
             # Ciptakan Cashier jika tidak ada
            cashier = Cashier.objects.create(user=request.user) 

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

        for pk_str, qty in keranjang.items():
            try:
                produk = get_object_or_404(Product, pk=pk_str)
                if produk.stock < qty:
                    transaction.set_rollback(True)
                    # Kembali ke halaman kasir dengan pesan error
                    # Untuk render ulang halaman kasir dengan data terkini
                    keranjang_items_error, total_error = [], 0
                    for p, q in keranjang.items():
                        try:
                            prod_obj = Product.objects.get(pk=p)
                            keranjang_items_error.append({'produk': prod_obj, 'qty': q, 'subtotal': prod_obj.price * q})
                            total_error += prod_obj.price * q
                        except Product.DoesNotExist:
                            pass
                    return render(request, 'kasir.html', {
                        'keranjang_items': keranjang_items_error,
                        'total': total_error,
                        'error_message': f"Stok {produk.name} tidak cukup! Sisa stok: {produk.stock}"
                    })
                
                subtotal_item = produk.price * qty
                OrderItem.objects.create(order=order, product=produk, quantity=qty, price=produk.price)
                
                produk.stock -= qty
                products_to_update_stock.append(produk)

                order_items_for_template.append({'produk': produk, 'qty': qty, 'subtotal': subtotal_item})
                total_checkout += subtotal_item

            except Product.DoesNotExist:
                transaction.set_rollback(True)
                # handle jika produk dihapus dari DB setelah ditambahkan ke keranjang
                keranjang_items_error, total_error = [], 0
                for p, q in keranjang.items():
                    try:
                        prod_obj = Product.objects.get(pk=p)
                        keranjang_items_error.append({'produk': prod_obj, 'qty': q, 'subtotal': prod_obj.price * q})
                        total_error += prod_obj.price * q
                    except Product.DoesNotExist:
                        pass
                return render(request, 'kasir.html', {
                    'keranjang_items': keranjang_items_error,
                    'total': total_error,
                    'error_message': f"Produk dengan ID {pk_str} tidak ditemukan."
                })
            except Exception as e:
                transaction.set_rollback(True)
                keranjang_items_error, total_error = [], 0
                for p, q in keranjang.items():
                    try:
                        prod_obj = Product.objects.get(pk=p)
                        keranjang_items_error.append({'produk': prod_obj, 'qty': q, 'subtotal': prod_obj.price * q})
                        total_error += prod_obj.price * q
                    except Product.DoesNotExist:
                        pass
                return render(request, 'kasir.html', {
                    'keranjang_items': keranjang_items_error,
                    'total': total_error,
                    'error_message': f"Terjadi kesalahan saat memproses produk {pk_str}: {e}"
                })
        
        for p_to_update in products_to_update_stock:
            p_to_update.save()

        order.subtotal = total_checkout
        order.total = total_checkout
        order.save()

        request.session['keranjang'] = {}
        request.session.modified = True

    return render(request, 'kasir_sukses.html', {
        'order': order,
        'order_items': order_items_for_template,
        'customer': customer,
        'cashier': cashier,
        'total': total_checkout
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

@require_POST
@login_required
def update_cart_quantity(request):
    product_id = request.POST.get('product_id')
    new_qty = int(request.POST.get('new_qty', 0))
    keranjang = request.session.get('keranjang', {})
    if new_qty > 0:
        keranjang[product_id] = new_qty
    elif product_id in keranjang:
        del keranjang[product_id]
    request.session['keranjang'] = keranjang
    request.session.modified = True
    # Anda bisa return info produk, total, dsb sesuai kebutuhan frontend
    return JsonResponse({'status': 'success', 'message': 'Kuantitas diperbarui', 'product_id': product_id, 'new_qty_in_cart': new_qty})