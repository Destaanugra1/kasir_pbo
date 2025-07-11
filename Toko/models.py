from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import qrcode
from io import BytesIO
from django.core.files import File

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        if not hasattr(instance, 'userprofile'):
            UserProfile.objects.create(user=instance)
        else:
            instance.userprofile.save()

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('kasir', 'Kasir'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"
    
    
    
    

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Nama Kategori"))
    description = models.TextField(blank=True, verbose_name=_("Deskripsi"))
    image = models.ImageField(upload_to='category_images/', blank=True, null=True, verbose_name=_("Gambar"))

    class Meta:
        verbose_name = _("Kategori")
        verbose_name_plural = _("Kategori")

    def __str__(self):
        return self.name

class Supplier(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Nama Supplier"))
    contact = models.CharField(max_length=50, verbose_name=_("Kontak"))
    address = models.TextField(verbose_name=_("Alamat"))

    class Meta:
        verbose_name = _("Supplier")
        verbose_name_plural = _("Supplier")

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Nama Produk"))
    barcode = models.CharField(max_length=100, blank=True, null=True, unique=True, verbose_name=_("Barcode"))  # Tambahkan ini
    description = models.TextField(verbose_name=_("Deskripsi"))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Harga Jual"))
    cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Harga Modal"), default=0)
    stock = models.PositiveIntegerField(verbose_name=_("Stok"))
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products", verbose_name=_("Kategori"))
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Supplier"))
    image = models.ImageField(upload_to='product_images/', blank=True, null=True, verbose_name=_("Gambar Produk"))
    qr_image = models.ImageField(upload_to='product_qr/', blank=True, null=True, verbose_name=_("QR Code"))

    class Meta:
        verbose_name = _("Produk")
        verbose_name_plural = _("Produk")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Generate barcode otomatis jika belum ada
        if not self.barcode:
            # Contoh: barcode diisi dengan ID produk setelah disimpan pertama kali
            super().save(*args, **kwargs)
            self.barcode = f'PRD{self.id:06d}'
        # Generate QR code otomatis jika belum ada atau barcode berubah
        if self.barcode and (not self.qr_image or not self.qr_image.name or self._state.adding):
            import qrcode
            from io import BytesIO
            from django.core.files import File
            qr = qrcode.make(self.barcode)
            buffer = BytesIO()
            qr.save(buffer, format='PNG')
            filename = f'qr_{self.barcode}.png'
            self.qr_image.save(filename, File(buffer), save=False)
        super().save(*args, **kwargs)

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_("Pengguna"))
    phone = models.CharField(max_length=20, verbose_name=_("Nomor Telepon"))
    address = models.TextField(verbose_name=_("Alamat"))

    class Meta:
        verbose_name = _("Pelanggan")
        verbose_name_plural = _("Pelanggan")

    def __str__(self):
        return self.user.get_full_name()

class Cashier(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_("Pegawai"))
    employee_id = models.CharField(max_length=20, verbose_name=_("ID Pegawai"))

    class Meta:
        verbose_name = _("Kasir")
        verbose_name_plural = _("Kasir")

    def __str__(self):
        return self.user.get_full_name()

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name=_("Pelanggan"))
    cashier = models.ForeignKey(Cashier, on_delete=models.SET_NULL, null=True, verbose_name=_("Kasir"))
    order_date = models.DateTimeField(auto_now_add=True, verbose_name=_("Tanggal Transaksi"))
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Subtotal"))
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_("Pajak"))
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_("Diskon"))
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Total Bayar"))
    is_paid = models.BooleanField(default=False, verbose_name=_("Sudah Dibayar"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Pesanan")
        verbose_name_plural = _("Pesanan")

    def __str__(self):
        return f"Order #{self.id} - {self.customer.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name=_("Pesanan"))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_("Produk"))
    quantity = models.PositiveIntegerField(verbose_name=_("Jumlah"))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Harga Satuan"))

    class Meta:
        verbose_name = _("Item Pesanan")
        verbose_name_plural = _("Item Pesanan")

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def get_total_price(self):
        return self.quantity * self.price

class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, verbose_name=_("Pesanan"))
    method = models.CharField(max_length=50, choices=[
        ('cash', _("Tunai")),
        ('card', _("Kartu")),
        ('qris', _("QRIS")),
        ('transfer', _("Transfer Bank"))
    ], verbose_name=_("Metode Pembayaran"))
    paid_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Waktu Pembayaran"))

    class Meta:
        verbose_name = _("Pembayaran")
        verbose_name_plural = _("Pembayaran")

    def __str__(self):
        return f"{self.method} - {self.order.id}"

class Purchase(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, verbose_name=_("Supplier"))
    date = models.DateTimeField(auto_now_add=True, verbose_name=_("Tanggal Pembelian"))

    class Meta:
        verbose_name = _("Pembelian Stok")
        verbose_name_plural = _("Pembelian Stok")

    def __str__(self):
        return f"Pembelian #{self.id} - {self.supplier.name}"

class PurchaseItem(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='items', verbose_name=_("Pembelian"))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_("Produk"))
    quantity = models.PositiveIntegerField(verbose_name=_("Jumlah"))
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Harga Beli"))

    class Meta:
        verbose_name = _("Item Pembelian")
        verbose_name_plural = _("Item Pembelian")

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

class Return(models.Model):
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, verbose_name=_("Item Pesanan"))
    reason = models.TextField(verbose_name=_("Alasan Retur"))
    return_date = models.DateTimeField(auto_now_add=True, verbose_name=_("Tanggal Retur"))
    quantity = models.PositiveIntegerField(verbose_name=_("Jumlah Retur"))

    class Meta:
        verbose_name = _("Retur")
        verbose_name_plural = _("Retur")

    def __str__(self):
        return f"Retur #{self.id} - {self.order_item.product.name}"
