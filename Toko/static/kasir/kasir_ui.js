// UI Update Functions untuk manipulasi DOM
// Fungsi untuk update UI utama
function updateUI(productId, productName, newQty, productPrice, productStock, totalAmount, totalItems) {
  console.log(`updateUI called with:`, {productId, productName, newQty, productPrice, productStock, totalAmount, totalItems});

  const safeProductId = String(productId);
  const safeProductName = String(productName);
  const safeNewQty = parseInt(newQty) || 0;
  const safeProductPrice = parseFloat(productPrice) || 0;
  const safeProductStock = parseInt(productStock) || 0;
  const safeTotalAmount = parseFloat(totalAmount) || 0;
  const safeTotalItems = parseInt(totalItems) || 0;

  console.log(`Safe values:`, {safeProductId, safeProductName, safeNewQty, safeProductPrice, safeProductStock, safeTotalAmount, safeTotalItems});

  window.productPrices[safeProductId] = safeProductPrice;

  let productRowLeft = document.getElementById(`product-row-${safeProductId}`);
  const daftarProdukList = document.getElementById('daftar-produk-list');
  const emptyProductListMessage = document.getElementById('empty-product-list-message');

  if (!daftarProdukList) {
    console.error("Elemen dengan ID 'daftar-produk-list' tidak ditemukan.");
    return;
  }

  if (safeNewQty > 0) {
    if (!productRowLeft) {
      console.log(`Creating new product row for ${safeProductId}`);
      productRowLeft = document.createElement('div');
      productRowLeft.id = `product-row-${safeProductId}`;
      productRowLeft.className = `group bg-white border border-gray-200 rounded-xl p-6 hover:shadow-md transition-all duration-200`;

      const priceFormatted = new Intl.NumberFormat('id-ID').format(safeProductPrice);

      productRowLeft.innerHTML = `
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-4">
            <div class="w-14 h-14 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center group-hover:scale-105 transition-transform duration-200">
              <span class="text-white font-bold text-lg">${safeProductName.charAt(0).toUpperCase()}</span>
            </div>
            <div>
              <h3 class="text-lg font-semibold text-gray-900 group-hover:text-blue-600 transition-colors duration-200">${safeProductName}</h3>
              <div class="mt-2">
                <div class="flex items-center space-x-4">
                  <span class="text-xl font-bold text-blue-600">Rp${priceFormatted}</span>
                  <span id="stock-status-${safeProductId}" class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium">
                    <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M5 4a2 2 0 012-2h6a2 2 0 012 2v14l-5-2.5L5 18V4z" />
                    </svg>
                  </span>
                </div>
              </div>
            </div>
          </div>
          <div class="flex items-center space-x-4">
            <div class="flex items-center space-x-2 bg-gray-50 rounded-xl p-2 border border-gray-200">
              <button type="button" onclick="updateQuantityAjax('${safeProductId}', -1)"
                class="w-10 h-10 bg-red-500 hover:bg-red-600 rounded-lg text-white flex items-center justify-center transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-red-300">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4" />
                </svg>
              </button>
              <input type="number" id="qty_${safeProductId}" min="0" max="${safeProductStock}" value="${safeNewQty}"
                onchange="updateQuantityAjax('${safeProductId}', 'manual', this.value)"
                class="w-20 h-10 text-center text-lg font-semibold border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 focus:outline-none transition-all duration-200" />
              <button type="button" onclick="updateQuantityAjax('${safeProductId}', 1)"
                class="w-10 h-10 bg-green-500 hover:bg-green-600 rounded-lg text-white flex items-center justify-center transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-green-300">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
              </button>
            </div>
            <div class="text-right">
              <p class="text-sm text-gray-500">Subtotal</p>
              <p class="text-xl font-bold text-gray-900" id="subtotal_${safeProductId}"></p>
            </div>
          </div>
        </div>
      `;
      daftarProdukList.appendChild(productRowLeft);
      if (emptyProductListMessage) emptyProductListMessage.classList.add('hidden');
    } else {
      console.log(`Updating existing product row for ${safeProductId}`);
    }

    const qtyInput = document.getElementById(`qty_${safeProductId}`);
    if (qtyInput) {
      console.log(`Updating quantity input from ${qtyInput.value} to ${safeNewQty}`);
      qtyInput.value = safeNewQty;
      qtyInput.max = safeProductStock;
      validateQty(qtyInput.id, safeProductStock);
    }

    const subtotalElement = document.getElementById(`subtotal_${safeProductId}`);
    if (subtotalElement) {
      const subtotal = safeNewQty * safeProductPrice;
      console.log(`Updating subtotal: ${safeNewQty} x ${safeProductPrice} = ${subtotal}`);
      subtotalElement.textContent = formatRupiah(subtotal);
    }

    const stockStatusElement = document.getElementById(`stock-status-${safeProductId}`);
    if (stockStatusElement) {
      const remainingStock = safeProductStock - safeNewQty;
      const stockText = remainingStock > 0 ? `${remainingStock} tersisa` : 'Stok habis';
      stockStatusElement.textContent = stockText;
      stockStatusElement.className = `inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
        remainingStock > 10 ? 'bg-green-100 text-green-800' :
        remainingStock > 5 ? 'bg-yellow-100 text-yellow-800' :
        remainingStock > 0 ? 'bg-red-100 text-red-800' :
        'bg-gray-200 text-gray-500'
      }`;
    }
  } else {
    console.log(`Removing product row for ${safeProductId}`);
    if (productRowLeft) productRowLeft.remove();
  }

  updateCartUI(safeProductId, safeProductName, safeNewQty, safeProductPrice);
  updateTotalsDisplay(safeTotalAmount, safeTotalItems);
}

// Fungsi untuk update UI cart
function updateCartUI(productId, productName, newQty, productPrice) {
  console.log(`updateCartUI called with:`, {productId, productName, newQty, productPrice});

  let cartItemDiv = document.getElementById(`cart-item-${productId}`);
  const keranjangItemsList = document.getElementById('keranjang-items-list');

  if (!keranjangItemsList) {
    console.error("Elemen dengan ID 'keranjang-items-list' tidak ditemukan.");
    return;
  }

  if (newQty > 0) {
    if (!cartItemDiv) {
      console.log(`Creating new cart item for ${productId}`);
      cartItemDiv = document.createElement('div');
      cartItemDiv.id = `cart-item-${productId}`;
      cartItemDiv.className = `flex items-center justify-between p-4 bg-gradient-to-r from-gray-50 to-gray-100 border border-gray-200 rounded-xl hover:shadow-md hover:border-blue-300 transition-all duration-300 transform hover:scale-105`;

      const priceFormatted = new Intl.NumberFormat('id-ID').format(productPrice);

      cartItemDiv.innerHTML = `
        <div class="flex items-center space-x-3">
          <div class="w-12 h-12 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-xl flex items-center justify-center shadow-sm">
            <span class="text-blue-700 font-bold text-sm">${productName.charAt(0).toUpperCase()}</span>
          </div>
          <div>
            <h4 class="font-semibold text-gray-900 text-sm leading-tight">${productName}</h4>
            <p class="text-xs text-gray-600 mt-1">
              <span id="cart-qty-${productId}" class="font-medium text-blue-600">${newQty}</span>
              <span class="mx-1">×</span>
              <span class="font-medium" id="cart-price-${productId}">Rp${priceFormatted}</span>
            </p>
          </div>
        </div>
        <div class="flex items-center space-x-3">
          <div class="text-right">
            <p class="font-bold text-gray-900 text-sm" id="cart-subtotal-${productId}"></p>
          </div>
          <button type="button" onclick="removeItemAjax('${productId}')"
            class="w-8 h-8 bg-red-500 hover:bg-red-600 rounded-lg text-white flex items-center justify-center shadow-md transition-all duration-200 hover:scale-110"
            title="Hapus dari keranjang">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      `;
      keranjangItemsList.appendChild(cartItemDiv);
    } else {
      console.log(`Updating existing cart item for ${productId}`);
      const cartQtyElement = document.getElementById(`cart-qty-${productId}`);
      const cartPriceElement = document.getElementById(`cart-price-${productId}`);

      if (cartQtyElement) {
        console.log(`Updating cart quantity from ${cartQtyElement.textContent} to ${newQty}`);
        cartQtyElement.textContent = newQty;
      }
      if (cartPriceElement) {
        const priceFormatted = new Intl.NumberFormat('id-ID').format(productPrice);
        console.log(`Updating cart price to Rp${priceFormatted}`);
        cartPriceElement.textContent = `Rp${priceFormatted}`;
      }
    }

    const cartSubtotalElement = document.getElementById(`cart-subtotal-${productId}`);
    if (cartSubtotalElement) {
      const subtotal = newQty * productPrice;
      console.log(`Updating cart subtotal: ${newQty} x ${productPrice} = ${subtotal}`);
      cartSubtotalElement.textContent = formatRupiah(subtotal);
    }
  } else {
    console.log(`Removing cart item for ${productId}`);
    if (cartItemDiv) cartItemDiv.remove();
  }
}
