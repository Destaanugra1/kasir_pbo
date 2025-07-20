// Main Kasir JavaScript - Initialization dan Event Handlers
// Global variables
window.productPrices = {};
window.updateCartQuantityUrl = '';
window.removeItemFromCartUrl = '';
window.getProductByBarcodeUrl = '';

// Document ready function
document.addEventListener('DOMContentLoaded', function() {
  const emptyProductListMessage = document.getElementById('empty-product-list-message');
  const emptyCartMessage = document.getElementById('empty-cart-message');
  const checkoutSection = document.getElementById('checkout-section');
  const initialItemCount = parseInt(document.getElementById('cart-item-count').textContent);

  if (initialItemCount > 0) {
    if (emptyProductListMessage) emptyProductListMessage.classList.add('hidden');
    if (emptyCartMessage) emptyCartMessage.classList.add('hidden');
    if (checkoutSection) checkoutSection.classList.remove('hidden');
  } else {
    if (emptyProductListMessage) emptyProductListMessage.classList.remove('hidden');
    if (emptyCartMessage) emptyCartMessage.classList.remove('hidden');
    if (checkoutSection) checkoutSection.classList.add('hidden');
  }

  // Setup event listeners untuk quantity inputs
  document.querySelectorAll('#daftar-produk-list input[id^="qty_"]').forEach(input => {
    const productId = input.id.replace('qty_', '');
    const initialStock = parseInt(input.max) || 0;
    validateQty(input.id, initialStock);

    input.removeEventListener('change', function(){});
    input.removeEventListener('input', function(){});

    input.addEventListener('change', function() {
      updateQuantityAjax(productId, 'manual', this.value);
    });
    input.addEventListener('input', function() {
      validateQty(this.id, parseInt(this.max));
    });
  });

  updateTotalsAndCounts();
});

// Global function registration
window.updateQuantityAjax = updateQuantityAjax;
window.removeItemAjax = removeItemAjax;
window.formatRupiah = formatRupiah;
window.validateQty = validateQty;
