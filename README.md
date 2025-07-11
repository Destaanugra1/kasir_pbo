# Sidebar Component Documentation

## Overview

Komponen sidebar yang responsif dan dapat di-collapse untuk Sistem Kasir Toko. Sidebar ini mendukung mode desktop dan mobile dengan transisi yang smooth dan state persistence.

## File Structure

```
Toko/
├── static/
│   ├── css/
│   │   └── sidebar.css          # Styling untuk sidebar
│   └── js/
│       └── sidebar.js           # JavaScript functionality
└── templates/
    └── sidebar.html             # Template HTML sidebar
    
    
```

## Features

- ✅ **Responsive Design**: Otomatis beradaptasi untuk desktop dan mobile
- ✅ **Collapsible Sidebar**: Toggle untuk mengecilkan/memperbesar sidebar
- ✅ **State Persistence**: Menyimpan status collapsed menggunakan localStorage
- ✅ **Hover Expansion**: Sidebar yang collapsed akan expand saat di-hover
- ✅ **Keyboard Shortcuts**: Ctrl+B untuk toggle, Escape untuk tutup mobile sidebar
- ✅ **Smooth Animations**: Transisi yang halus dengan cubic-bezier easing
- ✅ **Accessibility**: Dukungan screen reader dan keyboard navigation
- ✅ **Custom Events**: Event system untuk integrasi dengan komponen lain

## CSS Classes

### Main Classes

- `.sidebar-collapsed` - Applied when sidebar is in collapsed state
- `.sidebar-text` - Text elements that hide/show during collapse
- `.nav-link` - Navigation link styling
- `.nav-icon` - Icon styling within navigation
- `.toggle-button` - Collapse/expand button
- `.main-content` - Main content area that adjusts to sidebar state

### State Classes

- `.active` - Active navigation item
- `.pulse` - Pulse animation for toggle button
- `.sidebar-glow` - Glow effect on hover

## JavaScript API

### Public Methods

```javascript
// Toggle sidebar collapse state
SidebarManager.toggle();

// Force collapse sidebar
SidebarManager.collapse();

// Force expand sidebar
SidebarManager.expand();

// Check if sidebar is collapsed
const isCollapsed = SidebarManager.isCollapsed();

// Close mobile sidebar
SidebarManager.closeMobile();
```

### Custom Events

```javascript
// Listen for sidebar toggle events
window.addEventListener('sidebarToggle', (e) => {
  console.log('Sidebar collapsed:', e.detail.isCollapsed);
});
```

## Usage

### Basic Implementation

```html
<!-- Include the CSS -->
{% load static %}
<link rel="stylesheet" type="text/css" href="{% static 'css/sidebar.css' %}" />

<!-- Include the HTML structure -->
{% include 'sidebar.html' %}

<!-- Include the JavaScript -->
<script src="{% static 'js/sidebar.js' %}"></script>
```

### Customization

#### CSS Variables (Optional Enhancement)

```css
:root {
  --sidebar-width: 18rem;
  --sidebar-collapsed-width: 4.5rem;
  --sidebar-transition: 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  --sidebar-bg: linear-gradient(to bottom, #4f46e5, #3b82f6, #7c3aed);
}
```

#### Adding New Navigation Items

```html
<a
  href="{% url 'your_view' %}"
  class="nav-link group flex items-center space-x-3 hover:bg-white/20 px-4 py-3 rounded-xl transition-all duration-300"
  title="Your Page">
  <i class="nav-icon fas fa-your-icon text-blue-200 group-hover:text-white"></i>
  <span class="sidebar-text">Your Page</span>
</a>
```

## Keyboard Shortcuts

- `Ctrl + B` - Toggle sidebar collapse (desktop only)
- `Escape` - Close mobile sidebar

## Browser Support

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

## Performance Considerations

- CSS transitions menggunakan `transform` dan `opacity` untuk performa optimal
- JavaScript menggunakan event delegation untuk efisiensi
- LocalStorage digunakan untuk persistence tanpa server requests

## Accessibility Features

- ARIA labels dan roles untuk screen readers
- Keyboard navigation support
- High contrast mode support
- Reduced motion support untuk users dengan preference tersebut

## Troubleshooting

### Common Issues

1. **Sidebar tidak muncul**

   - Pastikan Tailwind CSS sudah loaded
   - Check console untuk JavaScript errors
   - Verifikasi file static path

2. **Toggle button tidak berfungsi**

   - Pastikan ID elements sudah benar
   - Check z-index conflicts
   - Verifikasi JavaScript loaded

3. **State tidak persist**
   - Check localStorage permissions
   - Verifikasi domain consistency

### Debug Mode

```javascript
// Enable debug logging
localStorage.setItem('sidebarDebug', 'true');
```

## Future Enhancements

- [ ] Theme switching (dark/light mode)
- [ ] Multiple sidebar layouts
- [ ] Drag-to-resize functionality
- [ ] Custom animation presets
- [ ] Integration dengan Vue.js/React

## Changelog

### v1.0.0 (Current)

- Initial release dengan full functionality
- Responsive design
- State persistence
- Accessibility support
- Custom events system

## Support

Untuk issues atau pertanyaan, silakan hubungi tim development atau buat issue di repository.
