// ===== KONFIGURASI =====
const API_BASE_URL = 'https://picking-scholar-defensive-charged.trycloudflare.com/api';
const SLUG = 'PlushPepe-1';

// ===== DOM ELEMENTS =====
const elements = {
  tgsPlayer: document.getElementById('tgs-player'),
  loadingIndicator: document.getElementById('loadingIndicator'),
  errorMessage: document.getElementById('errorMessage'),
  giftInfoPanel: document.getElementById('giftInfoPanel'),
  giftAttributes: document.getElementById('giftAttributes'),
  giftAvailability: document.getElementById('giftAvailability'),
  refreshBtn: document.getElementById('refreshBtn')
};

// ===== TELEGRAM WEB APP =====
let tg = null;

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', async () => {
  initializeTelegramApp();
  await loadGiftInfo();
  loadTGSSticker();
  setupEventListeners();
});

function initializeTelegramApp() {
  if (window.Telegram && window.Telegram.WebApp) {
    tg = window.Telegram.WebApp;
    tg.expand();
    tg.ready();

    // Set background transparan
    if (tg.setBackgroundColor) {
      tg.setBackgroundColor('#00000000');
    }

    // Sembunyikan back button
    try {
      tg.BackButton?.hide();
    } catch (e) {
      console.log('BackButton not supported');
    }

    console.log('✅ Telegram Web App initialized');
  }
}

// ===== LOAD GIFT INFO =====
async function loadGiftInfo() {
  try {
    // Tampilkan skeleton loading
    showAttributeSkeletons();

    const response = await fetch(`${API_BASE_URL}/info/${SLUG}`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();

    // Sembunyikan skeleton
    hideAttributeSkeletons();

    // Render gift info
    renderGiftInfo(data);

  } catch (error) {
    console.error('Error loading gift info:', error);
    hideAttributeSkeletons();
    showError('Gagal memuat informasi gift');
  }
}

function showAttributeSkeletons() {
  if (elements.giftAttributes) {
    elements.giftAttributes.innerHTML = `
            <div class="attribute-skeleton"></div>
            <div class="attribute-skeleton"></div>
            <div class="attribute-skeleton"></div>
        `;
  }
}

function hideAttributeSkeletons() {
  // Akan diisi oleh renderGiftInfo
}

function renderGiftInfo(info) {
  // Tentukan class rarity berdasarkan nilai
  const getRarityClass = (rarity) => {
    const num = parseInt(rarity) || 0;
    if (num >= 10) return 'legendary';
    if (num >= 5) return 'epic';
    return 'rare';
  };

  // Format availability
  const availabilityText = `${info.availability_issued || 0} / ${info.availability_total || '∞'}`;

  // Render attributes
  elements.giftAttributes.innerHTML = `
        <div class="attribute-item">
            <span class="attribute-label">Model</span>
            <div class="attribute-value">
                <span class="attribute-name">${info.model || '-'}</span>
                <span class="attribute-rarity ${getRarityClass(info.model_rarity)}">${info.model_rarity || 'N/A'}</span>
            </div>
        </div>
        <div class="attribute-item">
            <span class="attribute-label">Background</span>
            <div class="attribute-value">
                <span class="attribute-name">${info.background || '-'}</span>
                <span class="attribute-rarity ${getRarityClass(info.background_rarity)}">${info.background_rarity || 'N/A'}</span>
            </div>
        </div>
        <div class="attribute-item">
            <span class="attribute-label">Symbol</span>
            <div class="attribute-value">
                <span class="attribute-name">${info.symbol || '-'}</span>
                <span class="attribute-rarity ${getRarityClass(info.symbol_rarity)}">${info.symbol_rarity || 'N/A'}</span>
            </div>
        </div>
    `;

  // Render availability
  elements.giftAvailability.innerHTML = `
        <span class="availability-label">Availability</span>
        <span class="availability-value">${availabilityText}</span>
    `;
}

// ===== LOAD TGS STICKER =====
function loadTGSSticker() {
  if (!elements.tgsPlayer) return;

  // Set src ke API endpoint
  const tgsUrl = `${API_BASE_URL}/tgs/${SLUG}`;
  elements.tgsPlayer.setAttribute('src', tgsUrl);

  // Event listener untuk loading
  elements.tgsPlayer.addEventListener('load', () => {
    hideLoading();
    console.log('✅ TGS sticker loaded');
  });

  elements.tgsPlayer.addEventListener('error', (error) => {
    console.error('❌ Error loading TGS:', error);
    hideLoading();
    showError('Gagal memuat sticker');
  });

  // Timeout untuk loading
  setTimeout(() => {
    if (elements.loadingIndicator && !elements.loadingIndicator.classList.contains('hidden')) {
      hideLoading();
      showError('Timeout: Gagal memuat sticker');
    }
  }, 10000);
}

function hideLoading() {
  if (elements.loadingIndicator) {
    elements.loadingIndicator.classList.add('hidden');
  }
}

function showError(message) {
  if (elements.errorMessage) {
    const errorDiv = elements.errorMessage.querySelector('div:last-child');
    if (errorDiv) {
      errorDiv.textContent = message;
    }
    elements.errorMessage.style.display = 'flex';

    // Sembunyikan setelah 5 detik
    setTimeout(() => {
      elements.errorMessage.style.display = 'none';
    }, 5000);
  }
}

// ===== EVENT LISTENERS =====
function setupEventListeners() {
  // Refresh button
  if (elements.refreshBtn) {
    elements.refreshBtn.addEventListener('click', () => {
      // Tampilkan loading
      if (elements.loadingIndicator) {
        elements.loadingIndicator.classList.remove('hidden');
      }

      // Sembunyikan error
      if (elements.errorMessage) {
        elements.errorMessage.style.display = 'none';
      }

      // Reload TGS dengan menghapus dan menambah src
      if (elements.tgsPlayer) {
        const currentSrc = elements.tgsPlayer.getAttribute('src');
        elements.tgsPlayer.setAttribute('src', '');
        setTimeout(() => {
          elements.tgsPlayer.setAttribute('src', currentSrc);
        }, 100);
      }

      // Reload info
      loadGiftInfo();
    });
  }
}

// ===== EXPORT FUNCTIONS =====
window.refreshSticker = function() {
  if (elements.refreshBtn) {
    elements.refreshBtn.click();
  }
};