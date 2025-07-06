from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Category, Product, Customer, Order, OrderItem, Payment,
    Supplier, Purchase, PurchaseItem, Return, Cashier, UserProfile
)

admin.site.register(UserProfile)
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')
    search_fields = ('name',)
    list_filter = ('name',)

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'phone', 'address')
    search_fields = ('user__username', 'phone')
    list_filter = ('user__username',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'cashier', 'order_date', 'total', 'is_paid')
    search_fields = ('customer__user__username', 'cashier__user__username')
    list_filter = ('is_paid',)
    date_hierarchy = 'order_date'

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price', 'get_total_price')
    search_fields = ('order__id', 'product__name')
    list_filter = ('order', 'product')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'method', 'paid_at')
    search_fields = ('order__id',)
    list_filter = ('method',)

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'contact', 'address')
    search_fields = ('name',)
    list_filter = ('name',)

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'supplier', 'date')
    search_fields = ('supplier__name',)
    list_filter = ('supplier',)

@admin.register(PurchaseItem)
class PurchaseItemAdmin(admin.ModelAdmin):
    list_display = ('purchase', 'product', 'quantity', 'cost_price')
    search_fields = ('product__name',)
    list_filter = ('purchase', 'product')

@admin.register(Return)
class ReturnAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_item', 'reason', 'return_date')
    search_fields = ('order_item__product__name',)
    list_filter = ('return_date',)

@admin.register(Cashier)
class CashierAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'employee_id')
    search_fields = ('user__username', 'employee_id')
    
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'barcode', 'show_qr_image', 'price', 'stock', 'category', 'supplier')
    search_fields = ('name', 'barcode')
    list_filter = ('category', 'supplier')
    readonly_fields = ('barcode', 'qr_image', 'show_qr_image')
    fields = ('name', 'description', 'price', 'cost', 'stock', 'category', 'supplier', 'image', 'barcode', 'qr_image', 'show_qr_image')
    list_editable = ('price', 'stock', 'name')

    def show_qr_image(self, obj):
        if obj.qr_image:
            return format_html('<img src="{}" width="60" height="60" />', obj.qr_image.url)
        return "-"
    show_qr_image.short_description = 'QR Code'
