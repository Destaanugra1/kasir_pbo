from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, Category, Supplier, Return, Product


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'image']

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact', 'address']


class UserForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent transition-all duration-200 hover:border-red-400 pr-12',
            'placeholder': 'Masukkan password'
        }), 
        required=True  # Pastikan wajib diisi saat tambah user
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 hover:border-blue-400',
                'placeholder': 'Masukkan username'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all duration-200 hover:border-green-400',
                'placeholder': 'Masukkan nama depan'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200 hover:border-purple-400',
                'placeholder': 'Masukkan nama belakang'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all duration-200 hover:border-orange-400',
                'placeholder': 'nama@email.com'
            }),
        }
        labels = {
            'username': 'Username',
            'first_name': 'Nama Depan',
            'last_name': 'Nama Belakang',
            'email': 'Email',
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['role']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'image']

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact', 'address']
        
class ReturnForm(forms.ModelForm):
    quantity = forms.IntegerField(min_value=1, label="Jumlah Retur", required=True)

    class Meta:
        model = Return
        fields = ['reason', 'quantity']  # Hanya alasan retur yang dibutuhkan

    def clean_reason(self):
        reason = self.cleaned_data.get('reason')
        if len(reason) < 10:
            raise forms.ValidationError("Alasan retur harus lebih dari 10 karakter.")
        return reason
    
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'cost', 'stock', 'category', 'supplier', 'image']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:  # Jika instance baru (tidak disimpan ke DB)
            self.fields['cost'].initial = 0
