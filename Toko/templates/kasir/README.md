# Struktur File Kasir - Modular

File `kasir.html` telah dipecah menjadi beberapa file untuk memudahkan maintenance dan pengembangan.

## Struktur File Baru

### Template Files (dalam folder `templates/kasir/`)

- `kasir_header.html` - Header dan judul sistem kasir
- `scan.html` - Komponen scanner QR/barcode (sudah ada)
- `product_list.html` - Daftar produk (sudah ada)
- `cart.html` - Keranjang belanja (sudah ada)

### JavaScript Files (dalam folder `static/kasir/`)

- `kasir_functions.js` - Utility functions (formatRupiah, validateQty, getCookie, dll)
- `kasir_scanner.js` - Fungsi-fungsi untuk QR/barcode scanner
- `kasir_ajax.js` - Fungsi AJAX untuk komunikasi dengan server
- `kasir_ui.js` - Fungsi update UI dan manipulasi DOM
- `kasir_main.js` - Inisialisasi dan event handlers utama

### File Utama

- `kasir.html` - Template utama yang mengintegrasikan semua komponen

## Keuntungan Struktur Baru

1. **Modular**: Setiap fungsi dipisah berdasarkan tanggung jawabnya
2. **Maintainable**: Mudah untuk debug dan mengembangkan fitur baru
3. **Readable**: Kode lebih mudah dibaca dan dipahami
4. **Reusable**: Komponen dapat digunakan kembali di tempat lain
5. **Scalable**: Mudah untuk menambah fitur baru tanpa mengubah file utama

## Cara Menggunakan

File `kasir.html` akan secara otomatis memuat semua komponen yang diperlukan:

- Template components melalui `{% include %}`
- JavaScript files melalui `<script src="{% static %}">`

## Backup

File asli disimpan sebagai `kasir_backup.html` untuk referensi jika diperlukan.

## Pengembangan Selanjutnya

Untuk menambah fitur baru:

1. Buat file JavaScript baru di `static/kasir/`
2. Include di `kasir.html`
3. Atau modifikasi file yang sudah ada sesuai fungsinya

Untuk menambah komponen UI baru:

1. Buat file template baru di `templates/kasir/`
2. Include di `kasir.html` atau file template lainnya
