// Scanner Functions untuk QR Code
// Global variables untuk scanner
let html5QrCode;
let isScanning = false;
let scanCooldown = false;
const COOLDOWN_DURATION = 3000;
const qrCodeRegionId = 'qr-reader';
const qrCodeResultElement = document.getElementById('qr-reader-result');
const startButton = document.getElementById('startButton');
const stopButton = document.getElementById('stopButton');
const initialMessage = document.getElementById('initialMessage');
const scannerFrame = document.getElementById('qr-scanner-frame');
const scannerOverlay = document.getElementById('qr-scanner-overlay');
const scannerBox = document.getElementById('qr-scanner-box');
const scannerCorners = document.getElementById('qr-scanner-corners');
const scannerLine = document.getElementById('qr-scanner-line');

// Fungsi scanner overlay
function showScannerOverlayElements() {
  if (scannerFrame) scannerFrame.classList.add('qr-scanner-active');
  if (scannerOverlay) scannerOverlay.style.display = 'block';
  if (scannerBox) scannerBox.style.display = 'block';
  if (scannerCorners) scannerCorners.style.display = 'block';
  if (scannerLine) scannerLine.style.display = 'block';
}

function hideScannerOverlayElements() {
  if (scannerFrame) scannerFrame.classList.remove('qr-scanner-active');
  if (scannerOverlay) scannerOverlay.style.display = 'none';
  if (scannerBox) scannerBox.style.display = 'none';
  if (scannerCorners) scannerCorners.style.display = 'none';
  if (scannerLine) scannerLine.style.display = 'none';
}

// Fungsi untuk memulai scan
window.startScan = function () {
  if (isScanning) {
    console.log('Scanner sudah berjalan.');
    qrCodeResultElement.textContent = 'Scanner sudah berjalan.';
    return;
  }

  if (html5QrCode) {
    html5QrCode
      .stop()
      .catch((e) =>
        console.warn(
          'Mencoba menghentikan scanner yang tidak berjalan atau error:',
          e
        )
      );
  }

  html5QrCode = new Html5Qrcode(qrCodeRegionId);
  isScanning = true;
  scanCooldown = false;
  qrCodeResultElement.textContent =
    'Meminta akses kamera dan memulai pemindaian...';
  initialMessage.classList.add('hidden');
  startButton.classList.add('hidden');
  stopButton.classList.remove('hidden');

  Html5Qrcode.getCameras()
    .then((devices) => {
      if (devices && devices.length) {
        const rearCamera = devices.find(
          (device) =>
            device.label.toLowerCase().includes('back') ||
            device.label.toLowerCase().includes('belakang') ||
            device.label.toLowerCase().includes('environment')
        );
        const cameraId = rearCamera ? rearCamera.id : devices[0].id;

        html5QrCode
          .start(
            { deviceId: { exact: cameraId } },
            {
              fps: 10,
              qrbox: { width: 300, height: 300 },
              disableFlip: true,
            },
            (decodedText, decodedResult) => {
              if (!scanCooldown) {
                qrCodeResultElement.textContent = `Barcode terdeteksi: ${decodedText}`;
                scanCooldown = true;
                hideScannerOverlayElements();
                setTimeout(() => {
                  scanCooldown = false;
                  qrCodeResultElement.textContent =
                    'Kamera aktif. Siap untuk scan berikutnya.';
                  showScannerOverlayElements();
                }, COOLDOWN_DURATION);
                handleScannedBarcode(decodedText);
              }
            },
            (errorMessage) => {
              // Error handling
            }
          )
          .catch((err) => {
            console.error('Gagal memulai scanner:', err);
            qrCodeResultElement.textContent = `Gagal memulai kamera: ${
              err.message || 'Error tidak diketahui'
            }`;
            isScanning = false;
            startButton.classList.remove('hidden');
            stopButton.classList.add('hidden');
            initialMessage.classList.remove('hidden');
            hideScannerOverlayElements();
          });

        setTimeout(() => {
          if (isScanning) {
            showScannerOverlayElements();
          }
        }, 1000);
      } else {
        qrCodeResultElement.textContent =
          'Tidak ada kamera terdeteksi di perangkat ini.';
        isScanning = false;
        startButton.classList.remove('hidden');
        stopButton.classList.add('hidden');
        initialMessage.classList.remove('hidden');
        hideScannerOverlayElements();
      }
    })
    .catch((err) => {
      console.error('Gagal mendapatkan daftar kamera:', err);
      qrCodeResultElement.textContent =
        'Error saat mencoba mengakses daftar kamera.';
      isScanning = false;
      startButton.classList.remove('hidden');
      stopButton.classList.add('hidden');
      initialMessage.classList.remove('hidden');
      hideScannerOverlayElements();
    });
};

// Fungsi untuk menghentikan scan
window.stopScan = function () {
  if (html5QrCode && isScanning) {
    html5QrCode
      .stop()
      .then(() => {
        isScanning = false;
        scanCooldown = false;
        qrCodeResultElement.textContent = 'Scanner telah dihentikan.';
        initialMessage.classList.remove('hidden');
        startButton.classList.remove('hidden');
        stopButton.classList.add('hidden');
        hideScannerOverlayElements();
      })
      .catch((err) => {
        qrCodeResultElement.textContent =
          'Gagal menghentikan scanner. Silakan refresh halaman.';
        isScanning = false;
        startButton.classList.remove('hidden');
        stopButton.classList.add('hidden');
        initialMessage.classList.remove('hidden');
        hideScannerOverlayElements();
      });
  } else {
    qrCodeResultElement.textContent = 'Scanner tidak aktif.';
    hideScannerOverlayElements();
  }
};
