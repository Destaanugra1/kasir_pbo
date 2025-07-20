// Kasir JavaScript Functions
// Utility Functions dan Helper Functions

// Mendapatkan CSRF token dari cookie
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.startsWith(name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// Fungsi untuk memformat angka menjadi format Rupiah
function formatRupiah(amount) {
  const numAmount = typeof amount === 'string' ? parseFloat(amount.replace(/[^\d.-]/g, '')) : parseFloat(amount);
  if (isNaN(numAmount)) {
    return 'Rp 0';
  }
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(numAmount);
}

// Fungsi untuk memvalidasi input kuantitas
function validateQty(inputId, maxStock) {
  const input = document.getElementById(inputId);
  if (!input) return;

  const currentQty = parseInt(input.value) || 0;
  const minusButton = input.previousElementSibling;
  const plusButton = input.nextElementSibling;

  if (minusButton && minusButton.tagName === 'BUTTON') {
    minusButton.disabled = currentQty <= 0;
    minusButton.classList.toggle('opacity-50', currentQty <= 0);
    minusButton.classList.toggle('cursor-not-allowed', currentQty <= 0);
  }
  if (plusButton && plusButton.tagName === 'BUTTON') {
    plusButton.disabled = currentQty >= maxStock;
    plusButton.classList.toggle('opacity-50', currentQty >= maxStock);
    plusButton.classList.toggle('cursor-not-allowed', currentQty >= maxStock);
  }
}

// Fungsi untuk update totals dan counts
function updateTotalsAndCounts() {
  let totalAmount = 0;
  let totalItemsInCart = 0;

  const daftarProdukList = document.getElementById('daftar-produk-list');
  if (!daftarProdukList) {
    console.warn("Element 'daftar-produk-list' not found when updating totals.");
    return;
  }

  daftarProdukList.querySelectorAll('input[id^="qty_"]').forEach(input => {
    const productId = input.id.replace('qty_', '');
    const quantity = parseInt(input.value) || 0;
    const price = window.productPrices[productId] || 0;

    if (quantity > 0) {
      totalAmount += quantity * price;
      totalItemsInCart += quantity;
    }
    validateQty(input.id, parseInt(input.max));
  });

  const totalPembayaranElement = document.getElementById('total-pembayaran');
  const cartItemCountElement = document.getElementById('cart-item-count');
  const daftarProdukCountElement = document.getElementById('daftar-produk-count');
  const emptyCartMessage = document.getElementById('empty-cart-message');
  const checkoutSection = document.getElementById('checkout-section');
  const emptyProductListMessage = document.getElementById('empty-product-list-message');

  if (totalPembayaranElement) totalPembayaranElement.textContent = formatRupiah(totalAmount);
  if (cartItemCountElement) cartItemCountElement.textContent = totalItemsInCart;
  if (daftarProdukCountElement) daftarProdukCountElement.textContent = totalItemsInCart;

  if (totalItemsInCart === 0) {
    if (emptyCartMessage) emptyCartMessage.classList.remove('hidden');
    if (checkoutSection) checkoutSection.classList.add('hidden');
    if (emptyProductListMessage) emptyProductListMessage.classList.remove('hidden');
  } else {
    if (emptyCartMessage) emptyCartMessage.classList.add('hidden');
    if (checkoutSection) checkoutSection.classList.remove('hidden');
    if (emptyProductListMessage) emptyProductListMessage.classList.add('hidden');
  }
}

// Fungsi untuk update display totals
function updateTotalsDisplay(totalAmount, totalItems) {
  const totalPembayaranElement = document.getElementById('total-pembayaran');
  const cartItemCountElement = document.getElementById('cart-item-count');
  const daftarProdukCountElement = document.getElementById('daftar-produk-count');
  const emptyCartMessage = document.getElementById('empty-cart-message');
  const checkoutSection = document.getElementById('checkout-section');
  const emptyProductListMessage = document.getElementById('empty-product-list-message');

  if (totalPembayaranElement) totalPembayaranElement.textContent = formatRupiah(totalAmount);
  if (cartItemCountElement) cartItemCountElement.textContent = totalItems;
  if (daftarProdukCountElement) daftarProdukCountElement.textContent = totalItems;

  if (totalItems === 0) {
    if (emptyCartMessage) emptyCartMessage.classList.remove('hidden');
    if (checkoutSection) checkoutSection.classList.add('hidden');
    if (emptyProductListMessage) emptyProductListMessage.classList.remove('hidden');
  } else {
    if (emptyCartMessage) emptyCartMessage.classList.add('hidden');
    if (checkoutSection) checkoutSection.classList.remove('hidden');
    if (emptyProductListMessage) emptyProductListMessage.classList.add('hidden');
  }
}
