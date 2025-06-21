from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import User
from .models import Product, Order, OrderItem, Customer, Cashier, UserProfile
from .forms import CategoryForm, SupplierForm, UserForm, UserProfileForm
from django.urls import reverse_lazy
from django import forms
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa

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

# Cek role admin
def is_admin(user):
    return user.is_authenticated and hasattr(user, 'userprofile') and user.userprofile.role == 'admin'

# Cek role kasir
def is_kasir(user):
    return user.is_authenticated and hasattr(user, 'userprofile') and user.userprofile.role == 'kasir'

# Form produk
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'cost', 'stock', 'category', 'supplier', 'image']

@login_required
def beranda(request):
    produk_list = Product.objects.all()
    return render(request, 'beranda.html', {'produk_list': produk_list})

@login_required
def product_list(request):
    produk_list = Product.objects.all()
    return render(request, 'product_list.html', {'produk_list': produk_list})

@login_required
@user_passes_test(is_admin)
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
@user_passes_test(is_admin)
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
@user_passes_test(is_admin)
def product_delete(request, pk):
    produk = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        produk.delete()
        return redirect('product_list')
    return render(request, 'product_confirm_delete.html', {'produk': produk})

@login_required
@user_passes_test(is_kasir)
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
@user_passes_test(is_kasir)
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
@user_passes_test(is_kasir)
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
@user_passes_test(is_admin)
def user_list(request):
    users = User.objects.all()
    return render(request, 'user_list.html', {'users': users})

@login_required
@user_passes_test(is_admin)
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
@user_passes_test(is_admin)
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