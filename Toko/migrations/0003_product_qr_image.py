# Generated by Django 5.2.3 on 2025-07-06 06:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Toko', '0002_product_barcode'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='qr_image',
            field=models.ImageField(blank=True, null=True, upload_to='product_qr/', verbose_name='QR Code'),
        ),
    ]
