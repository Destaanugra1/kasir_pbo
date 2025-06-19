from django.shortcuts import render
from .models import Product


def beranda(request):
    produk_list = Product.objects.all()[:6]  # tampilkan max 6 produk
    return render(request, 'beranda.html', {'produk_list': produk_list})