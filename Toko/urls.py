from django.urls import path
from . import views
from django.contrib.auth import views as auth_views 
from .views import CustomLoginView
from django.contrib import admin


urlpatterns = [
    path('', views.home, name='home'),
    path('beranda/', views.beranda, name='beranda'),
    path('produk/', views.product_list, name='product_list'),
    path('produk/tambah/', views.product_create, name='product_create'),
    path('produk/<int:pk>/edit/', views.product_update, name='product_update'),
    path('produk/<int:pk>/hapus/', views.product_delete, name='product_delete'),
    path('kasir/', views.kasir, name='kasir'),
    path('kasir/add-barcode/', views.add_by_barcode, name='add-by-barcode'),
    path('kasir/checkout/', views.kasir_checkout, name='kasir_checkout'),
    path('users/', views.user_list, name='user_list'),
    path('users/tambah/', views.user_create, name='user_create'),
    path('users/<int:pk>/edit/', views.user_update, name='user_update'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLoginView.as_view(), name='logout'),
    path('kasir/struk/<int:order_id>/', views.cetak_struk, name='cetak_struk'),
    path('retur/<int:product_id>/', views.create_return, name='create_return'),
    path('pesanan/<int:pk>/', views.order_detail, name='order_detail'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('get-product-by-barcode/', views.get_product_by_barcode, name='get_product_by_barcode'),
]