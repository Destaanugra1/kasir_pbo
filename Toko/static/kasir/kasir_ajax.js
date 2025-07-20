// AJAX Functions untuk komunikasi dengan server
// Fungsi untuk update quantity via AJAX
async function updateQuantityAjax(productId, change, manualValue = null) {
  console.log(`updateQuantityAjax called with productId: ${productId}, change: ${change}, manualValue: ${manualValue}`);

  let currentQtyInput = document.getElementById(`qty_${productId}`);
  if (!currentQtyInput) {
    console.error(`Input element qty_${productId} not found`);
    return;
  }

  let newQty;
  if (manualValue !== null && change === 'manual') {
    newQty = parseInt(manualValue) || 0;
  } else {
    const currentValue = parseInt(currentQtyInput.value) || 0;
    newQty = currentValue + parseInt(change);
  }

  console.log(`Current qty: ${currentQtyInput.value}, New qty: ${newQty}`);

  const maxStock = parseInt(currentQtyInput.max) || 999999;
  if (newQty < 0) newQty = 0;
  if (newQty > maxStock) {
    alert(`Stok tidak mencukupi! Maksimal ${maxStock} item.`);
    newQty = maxStock;
  }

  const currentInputValue = parseInt(currentQtyInput.value) || 0;
  if (currentInputValue === newQty && manualValue === null) {
    console.log('No change needed, skipping update');
    return;
  }

  try {
    console.log('Sending AJAX request...');
    const response = await fetch(window.updateCartQuantityUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-CSRFToken": getCookie('csrftoken'),
        "X-Requested-With": "XMLHttpRequest",
      },
      body: `product_id=${productId}&new_qty=${newQty}`,
    });

    const data = await response.json();
    console.log('AJAX response:', data);

    if (data.status === "success") {
      console.log(data.message);
      document.getElementById("qr-reader-result").textContent = data.message;

      updateUI(
        data.product_id,
        data.product_name,
        parseInt(data.new_qty_in_cart),
        parseFloat(data.product_price),
        parseInt(data.product_stock),
        parseFloat(data.total_amount),
        parseInt(data.total_items)
      );
    } else {
      alert("Gagal memperbarui kuantitas: " + data.message);
      document.getElementById("qr-reader-result").textContent = `Gagal: ${data.message}`;
      currentQtyInput.value = currentInputValue;
    }
  } catch (error) {
    console.error("Error saat memperbarui kuantitas:", error);
    alert("Terjadi kesalahan saat berkomunikasi dengan server.");
    document.getElementById("qr-reader-result").textContent = `Error: ${error.message}`;
    currentQtyInput.value = currentInputValue;
  }
}

// Fungsi untuk remove item via AJAX
async function removeItemAjax(productId) {
  try {
    const response = await fetch(window.removeItemFromCartUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-CSRFToken": getCookie('csrftoken'),
        "X-Requested-With": "XMLHttpRequest",
      },
      body: `product_id=${productId}`,
    });

    const data = await response.json();

    if (data.status === "success") {
      console.log(data.message);
      document.getElementById("qr-reader-result").textContent = data.message;
      updateUI(productId, "", 0, 0, 0, data.total_amount, data.total_items);
    } else {
      alert("Gagal menghapus produk: " + data.message);
      document.getElementById("qr-reader-result").textContent = `Gagal: ${data.message}`;
    }
  } catch (error) {
    console.error("Error saat menghapus produk:", error);
    alert("Terjadi kesalahan saat berkomunikasi dengan server.");
    document.getElementById("qr-reader-result").textContent = `Error: ${error.message}`;
  }
}

// Fungsi untuk handle scanned barcode
async function handleScannedBarcode(barcode) {
  document.getElementById("qr-reader-result").textContent = "Memproses barcode...";

  try {
    const response = await fetch(
      `${window.getProductByBarcodeUrl}?barcode=${encodeURIComponent(barcode)}`,
      {
        headers: {
          "X-Requested-With": "XMLHttpRequest",
        }
      }
    );
    const data = await response.json();

    if (data.status === "success") {
      const productId = data.product_id;
      const productName = data.product_name;
      const productPrice = data.product_price;
      const productStock = data.product_stock;
      const newQtyInCart = data.new_qty_in_cart;

      window.productPrices[productId] = productPrice;

      updateUI(productId, productName, newQtyInCart, productPrice, productStock, data.total_amount, data.total_items);
      document.getElementById("qr-reader-result").textContent = `✅ ${productName} ditambahkan! Jumlah: ${newQtyInCart}`;

    } else {
      document.getElementById("qr-reader-result").textContent = `❌ ${data.message}`;
      console.error("Respons tidak berhasil:", data.message);
    }
  } catch (err) {
    console.error("Error memproses barcode atau mengambil produk:", err);
    document.getElementById("qr-reader-result").textContent = `❌ ${err.message || "Terjadi kesalahan yang tidak terduga."}`;
  }
}
