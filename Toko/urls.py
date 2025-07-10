from django.urls import path
from . import views
from django.contrib.auth import views as auth_views 
from .views import (
    CustomLoginView, HomeView, BerandaView, ProductListView, 
    ProductCreateView, ProductUpdateView, ProductDeleteView,
    KasirView, GetProductByBarcodeView, AddByBarcodeView,
    UpdateCartQuantityView, RemoveItemFromCartView, KasirCheckoutView,
    CetakStrukView, UserListView, UserCreateView, UserUpdateView,
    CreateReturnView, OrderDetailView, DashboardView
)
from django.contrib import admin

urlpatterns = [
    # Home and navigation
    path('', views.BerandaView.as_view(), name='beranda'),
    path('home/', views.HomeView.as_view(), name='home'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    
    # Product management
    path('produk/', views.ProductListView.as_view(), name='product_list'),
    path('produk/tambah/', views.ProductCreateView.as_view(), name='product_create'),
    path('produk/<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product_update'),
    path('produk/<int:pk>/hapus/', views.ProductDeleteView.as_view(), name='product_delete'),
    
    # Cashier operations
    path('kasir/', views.KasirView.as_view(), name='kasir'),
    path('kasir/add-barcode/', views.AddByBarcodeView.as_view(), name='add-by-barcode'),
    path('kasir/checkout/', views.KasirCheckoutView.as_view(), name='kasir_checkout'),
    path('kasir/struk/<int:order_id>/', views.CetakStrukView.as_view(), name='cetak_struk'),
    
    # User management
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/tambah/', views.UserCreateView.as_view(), name='user_create'),
    path('users/<int:pk>/edit/', views.UserUpdateView.as_view(), name='user_update'),
    
    # Authentication
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLoginView.as_view(), name='logout'),
    
    # Returns and orders
    path('retur/<int:product_id>/', views.CreateReturnView.as_view(), name='create_return'),
    path('pesanan/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    
    # API endpoints
    path('get-product-by-barcode/', views.GetProductByBarcodeView.as_view(), name='get_product_by_barcode'),
    path('api/update-cart-quantity/', views.UpdateCartQuantityView.as_view(), name='update_cart_quantity'),
    path('api/remove-item-from-cart/', views.RemoveItemFromCartView.as_view(), name='remove_item_from_cart'),
]