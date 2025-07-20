# 🏪 Sistem Kasir Toko - Dokumentasi Lengkap

## 📋 Overview

Sistem Kasir Toko adalah aplikasi web berbasis Django yang dirancang untuk mengelola transaksi penjualan dengan fitur-fitur modern seperti QR/Barcode scanner, manajemen inventory real-time, dan interface yang responsif. Sistem ini telah dimodularisasi untuk memudahkan maintenance dan pengembangan.

## 🎯 Fitur Utama

- ✅ **QR/Barcode Scanner**: Scan produk dengan kamera untuk input cepat
- ✅ **Real-time Cart Management**: Update keranjang secara real-time via AJAX
- ✅ **Inventory Tracking**: Tracking stok produk secara otomatis
- ✅ **Responsive Design**: Optimized untuk desktop dan mobile
- ✅ **Modular Architecture**: Struktur file yang terorganisir dan mudah di-maintain
- ✅ **Print Receipt**: Generate dan print struk transaksi
- ✅ **User Management**: System login dan manajemen pengguna
- ✅ **Product Management**: CRUD operasi untuk produk

## 🗂️ Struktur Proyek

```
penjualanToko/
├── manage.py                    # Django management script
├── db.sqlite3                  # Database SQLite
├── media/                      # Media files (product images, QR codes)
│   ├── product_images/
│   └── product_qr/
├── penjualanToko/              # Main Django project
│   ├── __init__.py
│   ├── settings.py             # Project settings
│   ├── urls.py                 # Main URL configuration
│   ├── wsgi.py                 # WSGI configuration
│   └── asgi.py                 # ASGI configuration
└── Toko/                       # Main Django app
    ├── models.py               # Database models
    ├── views.py                # View functions
    ├── urls.py                 # App URL configuration
    ├── forms.py                # Django forms
    ├── admin.py                # Admin configuration
    ├── middleware.py           # Custom middleware
    ├── migrations/             # Database migrations
    ├── static/                 # Static files
    │   ├── css/
    │   │   └── sidebar.css
    │   ├── js/
    │   │   └── sidebar.js
    │   └── kasir/              # Kasir-specific static files
    │       ├── kasir.css
    │       ├── kasir_functions.js
    │       ├── kasir_scanner.js
    │       ├── kasir_ajax.js
    │       ├── kasir_ui.js
    │       └── kasir_main.js
    ├── templates/              # HTML templates
    │   ├── sidebar.html        # Main sidebar template
    │   ├── kasir.html          # Main kasir page
    │   ├── kasir_backup.html   # Backup of original kasir.html
    │   └── kasir/              # Modular kasir templates
    │       ├── kasir_header.html
    │       ├── scan.html
    │       ├── product_list.html
    │       ├── cart.html
    │       └── README.md
    └── templatetags/           # Custom template tags
        ├── __init__.py
        └── dict_extras.py
```

## 🚀 Installation & Setup

### Prerequisites

- Python 3.8+
- Django 4.x
- Modern web browser with camera support
- SQLite (included with Python)

### Quick Start

1. **Clone Repository**

   ```bash
   git clone https://github.com/Destaanugra1/kasir_pbo.git
   cd kasir_pbo
   ```

2. **Setup Virtual Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # atau
   venv\Scripts\activate     # Windows
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Database Setup**

   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. **Run Development Server**

   ```bash
   python manage.py runserver
   ```

6. **Access Application**
   - Main app: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## 🏗️ Arsitektur Modular Kasir

### Template Structure

Sistem kasir telah dimodularisasi untuk memudahkan maintenance:

#### Main Template

- **`kasir.html`** - Template utama yang mengintegrasikan semua komponen

#### Component Templates (dalam folder `templates/kasir/`)

- **`kasir_header.html`** - Header dan judul sistem kasir
- **`scan.html`** - Komponen QR/Barcode scanner
- **`product_list.html`** - Daftar produk dalam keranjang
- **`cart.html`** - Keranjang belanja dan checkout

#### JavaScript Modules (dalam folder `static/kasir/`)

- **`kasir_functions.js`** - Utility functions dan helper
- **`kasir_scanner.js`** - QR/Barcode scanner functionality
- **`kasir_ajax.js`** - AJAX communications dengan server
- **`kasir_ui.js`** - UI updates dan DOM manipulation
- **`kasir_main.js`** - Initialization dan event handlers

## 📱 Kasir System Features

### QR/Barcode Scanner

- **Real-time scanning** menggunakan device camera
- **Auto-detection** untuk berbagai format barcode
- **Cooldown system** untuk mencegah duplicate scan
- **Visual feedback** dengan overlay dan animation
- **Error handling** untuk device compatibility

### Cart Management

- **Real-time updates** via AJAX tanpa page reload
- **Quantity validation** berdasarkan stock availability
- **Auto-calculation** untuk subtotal dan total
- **Visual feedback** untuk setiap action
- **Undo functionality** untuk remove items

### Product Management

- **Dynamic product display** berdasarkan cart contents
- **Stock tracking** dan validation
- **Price formatting** dalam Rupiah
- **Product search** dan filtering
- **Image management** dengan placeholder

### User Interface

- **Responsive design** untuk semua device sizes
- **Modern styling** dengan Tailwind CSS
- **Smooth animations** dan transitions
- **Accessibility compliance** dengan ARIA labels
- **Keyboard shortcuts** support

## 🔧 JavaScript API Documentation

### Core Functions (kasir_functions.js)

```javascript
// Format currency dalam Rupiah
formatRupiah(amount);
// Returns: "Rp 50.000"

// Validate quantity input
validateQty(inputId, maxStock);
// Enables/disables buttons based on stock

// Get CSRF token for AJAX requests
getCookie(name);
// Returns: CSRF token string

// Update totals and item counts
updateTotalsAndCounts();
// Recalculates cart totals
```

### Scanner Functions (kasir_scanner.js)

```javascript
// Start QR/Barcode scanner
window.startScan();
// Initializes camera and scanning

// Stop scanner
window.stopScan();
// Stops camera and cleans up

// Handle scanned barcode
handleScannedBarcode(barcode);
// Processes scanned barcode
```

### AJAX Functions (kasir_ajax.js)

```javascript
// Update product quantity
updateQuantityAjax(productId, change, manualValue);
// Sends quantity update to server

// Remove item from cart
removeItemAjax(productId);
// Removes product from cart

// Handle barcode scan result
handleScannedBarcode(barcode);
// Processes scanned barcode via AJAX
```

### UI Functions (kasir_ui.js)

```javascript
// Update main UI elements
updateUI(
  productId,
  productName,
  newQty,
  productPrice,
  productStock,
  totalAmount,
  totalItems
);
// Updates product list and totals

// Update cart UI
updateCartUI(productId, productName, newQty, productPrice);
// Updates cart display
```

## 🎨 CSS Classes & Styling

### Layout Classes

- `.min-h-screen` - Full viewport height
- `.bg-gray-50` - Background color
- `.max-w-7xl` - Maximum container width
- `.mx-auto` - Center alignment
- `.grid` - CSS Grid layout

### Component Classes

- `.rounded-xl` - Rounded corners
- `.shadow-sm` - Subtle shadows
- `.border` - Border styling
- `.transition-all` - Smooth transitions
- `.hover:shadow-md` - Hover effects

### Interactive Classes

- `.group` - Group hover effects
- `.focus:outline-none` - Focus management
- `.disabled:opacity-50` - Disabled states
- `.cursor-not-allowed` - Cursor indication

## 📊 Database Models

### Product Model

```python
class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    barcode = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='product_images/')
    qr_image = models.ImageField(upload_to='product_qr/')
```

### Cart Model

```python
class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    session_key = models.CharField(max_length=40)
```

## 🔐 Security Features

### CSRF Protection

- CSRF tokens dalam semua AJAX requests
- Automatic token extraction dari cookies
- Server-side validation untuk semua forms

### Input Validation

- Client-side quantity validation
- Server-side stock validation
- SQL injection prevention via Django ORM

### Session Management

- Secure session handling
- Cart persistence per session
- Automatic cleanup untuk expired sessions

## 🌐 URL Configuration

### Main URLs (penjualanToko/urls.py)

```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Toko.urls')),
]
```

### App URLs (Toko/urls.py)

```python
urlpatterns = [
    path('', views.home, name='home'),
    path('kasir/', views.kasir, name='kasir'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('products/', views.product_list, name='product_list'),
    path('api/update-cart-quantity/', views.update_cart_quantity, name='update_cart_quantity'),
    path('api/remove-item/', views.remove_item_from_cart, name='remove_item_from_cart'),
    path('api/get-product-barcode/', views.get_product_by_barcode, name='get_product_by_barcode'),
]
```

## 🔄 AJAX Endpoints

### Update Cart Quantity

```javascript
POST /api/update-cart-quantity/
Content-Type: application/x-www-form-urlencoded
Body: product_id=123&new_qty=5

Response:
{
  "status": "success",
  "message": "Kuantitas berhasil diperbarui",
  "product_id": "123",
  "product_name": "Nama Produk",
  "new_qty_in_cart": 5,
  "product_price": 15000,
  "product_stock": 50,
  "total_amount": 150000,
  "total_items": 10
}
```

### Remove Item from Cart

```javascript
POST /api/remove-item/
Content-Type: application/x-www-form-urlencoded
Body: product_id=123

Response:
{
  "status": "success",
  "message": "Produk berhasil dihapus",
  "total_amount": 135000,
  "total_items": 8
}
```

### Get Product by Barcode

```javascript
GET /api/get-product-barcode/?barcode=1234567890

Response:
{
  "status": "success",
  "product_id": "123",
  "product_name": "Nama Produk",
  "product_price": 15000,
  "product_stock": 50,
  "new_qty_in_cart": 1,
  "total_amount": 15000,
  "total_items": 1
}
```

## 📋 Form Handling

### Product Form

```python
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'stock', 'barcode', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'barcode': forms.TextInput(attrs={'class': 'form-control'}),
        }
```

## 🎯 Event System

### Custom Events

```javascript
// Sidebar toggle event
window.addEventListener('sidebarToggle', (e) => {
  console.log('Sidebar collapsed:', e.detail.isCollapsed);
});

// Cart update event
window.addEventListener('cartUpdate', (e) => {
  console.log('Cart updated:', e.detail);
});

// Scanner event
window.addEventListener('barcodeScanned', (e) => {
  console.log('Barcode scanned:', e.detail.barcode);
});
```

## 🔧 Development Guidelines

### Adding New Features

1. **Create Feature Branch**

   ```bash
   git checkout -b feature/new-feature
   ```

2. **Follow Module Structure**

   - Templates → `templates/kasir/`
   - JavaScript → `static/kasir/`
   - CSS → `static/kasir/kasir.css`

3. **Update Documentation**
   - Update README.md
   - Add comments in code
   - Update API documentation

### Code Style

- **JavaScript**: Use ES6+ features
- **CSS**: Follow BEM methodology
- **Python**: Follow PEP 8
- **HTML**: Semantic markup

### Testing

```bash
# Run Django tests
python manage.py test

# Check code style
flake8 .

# Run JavaScript tests (if available)
npm test
```

## 📱 Mobile Optimization

### Responsive Breakpoints

- **Mobile**: < 640px
- **Tablet**: 640px - 1024px
- **Desktop**: > 1024px

### Touch Interactions

- **Tap targets**: Minimum 44px
- **Swipe gestures**: For mobile navigation
- **Pinch zoom**: Disabled untuk better UX

### Performance

- **Image optimization**: WebP format untuk modern browsers
- **Code splitting**: Modular JavaScript loading
- **Caching**: Static files caching

## 🚨 Troubleshooting

### Common Issues

1. **Scanner tidak berfungsi**

   ```
   Solusi:
   - Pastikan HTTPS atau localhost
   - Check camera permissions
   - Verifikasi browser compatibility
   ```

2. **AJAX requests gagal**

   ```
   Solusi:
   - Check CSRF token
   - Verifikasi URL endpoints
   - Check network connectivity
   ```

3. **Static files tidak load**
   ```
   Solusi:
   - Run: python manage.py collectstatic
   - Check STATIC_URL settings
   - Verifikasi file paths
   ```

### Debug Mode

```python
# settings.py
DEBUG = True
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}
```

## 📈 Performance Optimization

### Database Optimization

- **Indexing**: Pada fields yang sering di-query
- **Query optimization**: Use select_related dan prefetch_related
- **Connection pooling**: Untuk production

### Frontend Optimization

- **Asset compression**: Minify CSS/JS
- **Image optimization**: Lazy loading
- **Caching**: Browser dan server-side caching

### Server Optimization

- **Gunicorn**: WSGI server untuk production
- **Nginx**: Reverse proxy dan static file serving
- **Redis**: Session storage dan caching

## 🔒 Security Best Practices

### Django Security

- **SECRET_KEY**: Use environment variables
- **ALLOWED_HOSTS**: Configure untuk production
- **HTTPS**: Force SSL dalam production
- **Security middleware**: Enable semua security features

## 🚀 Deployment

### Production Setup

1. **Environment Variables**

   ```bash
   # .env file
   SECRET_KEY=your-secret-key-here
   DEBUG=False
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   DATABASE_URL=postgres://user:pass@localhost/dbname
   ```

2. **Static Files**

   ```bash
   python manage.py collectstatic --noinput
   ```

3. **Database Migration**

   ```bash
   python manage.py migrate --run-syncdb
   ```

4. **Gunicorn Setup**
   ```bash
   gunicorn penjualanToko.wsgi:application --bind 0.0.0.0:8000
   ```

### Docker Deployment

```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn", "penjualanToko.wsgi:application", "--bind", "0.0.0.0:8000"]
```

## 📊 Monitoring & Analytics

### Performance Metrics

- **Page load time**: < 2 seconds
- **AJAX response time**: < 500ms
- **Scanner activation**: < 1 second
- **Database queries**: Optimized dengan indexing

### Error Logging

```python
import logging

logger = logging.getLogger(__name__)

def kasir_view(request):
    try:
        # View logic
        pass
    except Exception as e:
        logger.error(f'Kasir error: {str(e)}')
        return JsonResponse({'status': 'error', 'message': 'Server error'})
```

## 🎓 Learning Resources

### Technologies Used

- **Django 4.x**: Web framework
- **JavaScript ES6+**: Frontend functionality
- **Tailwind CSS**: Styling framework
- **HTML5 QR Code**: Scanner library
- **SQLite**: Development database
- **AJAX**: Asynchronous communication

### Recommended Reading

- [Django Documentation](https://docs.djangoproject.com/)
- [JavaScript MDN](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Web API - MediaDevices](https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices)

## 🤝 Contributing

### Getting Started

1. Fork repository
2. Create feature branch
3. Make changes
4. Write tests
5. Submit pull request

### Code Review Process

- All changes require review
- Tests harus pass
- Documentation harus updated
- Code style harus consistent

### Branch Naming

- `feature/` - New features
- `bugfix/` - Bug fixes
- `hotfix/` - Critical fixes
- `docs/` - Documentation updates

## 📝 License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## 👥 Team

- **Developer**: Desta Anugra
- **Repository**: [kasir_pbo](https://github.com/Destaanugra1/kasir_pbo)
- **Contact**: [GitHub Profile](https://github.com/Destaanugra1)

## 🔄 Changelog

### v2.0.0 (Current - Modular Version)

- ✅ Modularized kasir.html into separate components
- ✅ Separated JavaScript into focused modules
- ✅ Improved code organization and maintainability
- ✅ Enhanced documentation
- ✅ Better error handling
- ✅ Performance optimizations

### v1.0.0 (Legacy)

- ✅ Initial monolithic kasir system
- ✅ Basic QR scanner functionality
- ✅ Cart management
- ✅ Product management
- ✅ User authentication

## 🎯 Future Roadmap

### Short Term (1-3 months)

- [ ] Dark mode theme
- [ ] PWA (Progressive Web App) support
- [ ] Offline functionality
- [ ] Enhanced reporting
- [ ] Multi-language support

### Medium Term (3-6 months)

- [ ] Mobile app (React Native/Flutter)
- [ ] Advanced analytics dashboard
- [ ] Inventory forecasting
- [ ] Supplier management
- [ ] Integration dengan payment gateways

### Long Term (6-12 months)

- [ ] Multi-store support
- [ ] Cloud deployment
- [ ] Advanced reporting & BI
- [ ] Machine learning untuk demand prediction
- [ ] API untuk third-party integrations

## 🆘 Support & Help

### Documentation

- **Main docs**: README.md (this file)
- **API docs**: `/docs/api/`
- **Component docs**: `/templates/kasir/README.md`

### Getting Help

1. Check dokumentasi terlebih dahulu
2. Search existing issues di GitHub
3. Create new issue dengan template yang sesuai
4. Join community discussions

### Bug Reports

Gunakan template berikut untuk bug reports:

```
**Bug Description:**
Describe the bug clearly

**Steps to Reproduce:**
1. Go to '...'
2. Click on '....'
3. See error

**Expected Behavior:**
What you expected to happen

**Screenshots:**
If applicable, add screenshots

**Environment:**
- OS: [e.g. Windows 10]
- Browser: [e.g. Chrome 91]
- Version: [e.g. v2.0.0]
```

---

## 📚 Quick Reference

### Essential Commands

```bash
# Start development server
python manage.py runserver

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Run tests
python manage.py test
```

### Important Files

- `kasir.html` - Main kasir template
- `kasir_main.js` - JavaScript initialization
- `models.py` - Database models
- `views.py` - Business logic
- `urls.py` - URL routing
- `settings.py` - Configuration

### Key URLs

- `/kasir/` - Main kasir page
- `/admin/` - Admin panel
- `/api/update-cart-quantity/` - Update cart via AJAX
- `/api/get-product-barcode/` - Get product by barcode

---

**Happy coding! 🚀**

_Last updated: July 20, 2025_
