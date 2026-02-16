// ===== FUNGSI UTILITY =====
function formatGiftName(name) {
    // Format nama gift: JellyBunny -> Jelly Bunny, PlushPepe -> Plush Pepe
    return name.replace(/([A-Z])/g, ' $1').trim();
}

function extractIdFromSlug(slug) {
    // Extract ID dari slug: JellyBunny-1234 -> 1234
    const parts = slug.split('-');
    return parts.length > 1 ? parts[1] : '';
}

function formatRupiah(amount) {
    const numAmount = Number(amount) || 0;
    return 'Rp ' + numAmount.toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
}

function formatPriceRupiah(price) {
    return 'Rp' + price.toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
}

function formatPrice(price) {
    return formatPriceRupiah(price);
}

// ===== STATE VARIABLES =====
let currentDepositAmount = 0;
let currentQRData = null;
let depositCheckInterval = null;

// Global state
let gifts = [];
let filteredGifts = [];

// Filter state
let activeFilters = {
    id: '',
    gift: [],      // Array of selected gift names
    model: [],     // Array of selected models
    symbol: [],    // Array of selected symbols
    bg: [],        // Array of selected backdrops
    sort: 'price-asc'  // Default sort
};

// Available filter options
let filterOptions = {
    gifts: [],
    models: [],
    symbols: [],
    bgs: []
};

let userDepositHistory = [];
let userWithdrawHistory = [];

// Current active popup
let currentPopupFilter = null;

// Lottie cache
const lottieCache = new Map();

// Telegram Web App
let tg = null;
let telegramUser = null;
let userBalance = 0; // Menyimpan saldo user

// ===== BOTTOM NAVIGATION =====
let currentPage = 'store'; // store, stats, profile
let userGifts = []; // Untuk menyimpan gift user
let userProfileData = null; // Untuk menyimpan data profil user

// DOM Elements
const elements = {
    cardsGrid: document.getElementById('cardsGrid'),
    idSearchInput: document.getElementById('idSearchInput'),
    idSearchClear: document.getElementById('idSearchClear'),
    filterToggle: document.getElementById('filterToggle'),
    filterPanel: document.getElementById('filterPanel'),
    filterBubbles: document.querySelectorAll('.filter-bubble'),
    modelBubble: document.getElementById('modelBubble'),
    symbolBubble: document.getElementById('symbolBubble'),
    bgBubble: document.getElementById('bgBubble'),
    giftCount: document.getElementById('giftCount'),
    modelCount: document.getElementById('modelCount'),
    symbolCount: document.getElementById('symbolCount'),
    bgCount: document.getElementById('bgCount'),
    sortValue: document.getElementById('sortValue'),
    clearAllFiltersBtn: document.getElementById('clearAllFiltersBtn'),
    applyFiltersBtn: document.getElementById('applyFiltersBtn'),
    activeFilters: document.getElementById('activeFilters'),
    filterPopupOverlay: document.getElementById('filterPopupOverlay'),
    filterPopup: document.getElementById('filterPopup'),
    filterPopupTitle: document.getElementById('filterPopupTitle'),
    filterPopupClose: document.getElementById('filterPopupClose'),
    selectAllBtn: document.getElementById('selectAllBtn'),
    clearAllBtn: document.getElementById('clearAllBtn'),
    popupSearchInput: document.getElementById('popupSearchInput'),
    filterPopupList: document.getElementById('filterPopupList'),
    totalItems: document.getElementById('total-items'),
    floorPrice: document.getElementById('floor-price'),
    loadingState: document.getElementById('loadingState'),
    bottomSheetOverlay: document.getElementById('bottomSheetOverlay'),
    bottomSheet: document.getElementById('bottomSheet'),
    sheetContent: document.getElementById('sheetContent'),
    scrollTopBtn: document.getElementById('scrollTopBtn'),
    activeFiltersPopupOverlay: document.getElementById('activeFiltersPopupOverlay'),
    activeFiltersPopup: document.getElementById('activeFiltersPopup'),
    activeFiltersPopupContent: document.getElementById('activeFiltersPopupContent'),
    activeFiltersPopupClose: document.getElementById('activeFiltersPopupClose'),
    viewActiveFiltersBtn: document.getElementById('viewActiveFiltersBtn'),
    shareFilterBtn: document.getElementById('shareFilterBtn'),
    userAvatar: document.getElementById('userAvatar'),
    userBalance: document.getElementById('userBalance'),
    userProfile: document.getElementById('userProfile'),
    activeFiltersContainer: document.getElementById('activeFiltersContainer'),
    activeFiltersContent: document.getElementById('activeFiltersContent'),
    activeFiltersScroll: document.getElementById('activeFiltersScroll'),
    sheetCloseBtn: document.getElementById('sheetCloseBtn'),
    sheetHandle: document.querySelector('.sheet-handle')
};

// Bottom navigation elements
const navStore = document.getElementById('navStore');
const navStats = document.getElementById('navStats');
const navProfile = document.getElementById('navProfile');

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', async () => {
    await initializeTelegramApp();
    await loadGifts();
    setupEventListeners();
    setupNavigationListeners();
    updateFilterCounts();
    renderGifts();
    setupScrollToTop();
    checkForUrlParameters();
    checkForGiftIdInUrl();
    updateSearchClearButton();
    updateShareButtonVisibility();
});

// ===== FUNGSI TELEGRAM =====
async function initializeTelegramApp() {
    if (window.Telegram && window.Telegram.WebApp) {
        tg = window.Telegram.WebApp;
        tg.expand();
        tg.ready();
        
        if (tg.initDataUnsafe && tg.initDataUnsafe.user) {
            telegramUser = tg.initDataUnsafe.user;
            console.log('Telegram User Data:', telegramUser);
            
            await fetchUserBalance(telegramUser.id);
            displayUserInfo(telegramUser);
            fetchTelegramUserPhoto(telegramUser.id);
        } else {
            console.log('User data tidak tersedia');
            setGuestUser();
        }
        
        applyTelegramTheme();
        setupTelegramBackButton();
    } else {
        console.log('Tidak terdeteksi sebagai Telegram Mini App');
        setGuestUser();
    }
}

async function fetchUserBalance(userId) {
    try {
        const API_BASE_URL = 'https://involved-sue-tan-hundreds.trycloudflare.com';
        const response = await fetch(`${API_BASE_URL}/api/user/balance/${userId}`);

        if (!response.ok) {
            throw new Error(`Gagal mengambil balance: ${response.status}`);
        }

        const data = await response.json();

        if (data.success) {
            userBalance = data.balance;
            console.log('Balance berhasil diambil:', userBalance);
        } else {
            userBalance = 0;
            console.warn('Balance tidak ditemukan, default 0');
        }

        updateUserBalanceDisplay();
    } catch (error) {
        console.error('Error fetching user balance:', error);
        userBalance = 0;
        updateUserBalanceDisplay();
    }
}

function updateUserBalanceDisplay() {
    if (elements.userBalance) {
        const formattedBalance = formatRupiah(userBalance);
        elements.userBalance.textContent = formattedBalance;
    }
}

async function fetchTelegramUserPhoto(userId) {
    try {
        if (telegramUser) {
            // Gunakan foto profil asli dari Telegram jika tersedia
            if (tg && tg.initDataUnsafe && tg.initDataUnsafe.user && tg.initDataUnsafe.user.photo_url) {
                const img = document.createElement('img');
                img.src = tg.initDataUnsafe.user.photo_url;
                img.alt = 'Profile';
                img.className = 'avatar-image';
                img.onload = () => {
                    const initialSpan = elements.userAvatar.querySelector('.avatar-initial');
                    if (initialSpan) {
                        initialSpan.style.display = 'none';
                    }
                    elements.userAvatar.appendChild(img);
                };
            } else {
                // Fallback ke UI Avatars
                const name = telegramUser.first_name || 'User';
                const avatarUrl = `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=8774E1&color=fff&size=128&bold=true&length=1`;
                
                const img = document.createElement('img');
                img.src = avatarUrl;
                img.alt = 'Profile';
                img.className = 'avatar-image';
                img.onload = () => {
                    const initialSpan = elements.userAvatar.querySelector('.avatar-initial');
                    if (initialSpan) {
                        initialSpan.style.display = 'none';
                    }
                    elements.userAvatar.appendChild(img);
                };
            }
        }
    } catch (error) {
        console.error('Error fetching user photo:', error);
    }
}

function displayUserInfo(user) {
    if (!user) return;
    
    const initialSpan = elements.userAvatar.querySelector('.avatar-initial');
    if (initialSpan) {
        const initial = user.first_name ? user.first_name.charAt(0).toUpperCase() : '?';
        initialSpan.textContent = initial;
    }
    
    if (user.is_premium && elements.userProfile) {
        elements.userProfile.classList.add('premium');
    }
}

function setGuestUser() {
    userBalance = 0;
    updateUserBalanceDisplay();
    
    const initialSpan = elements.userAvatar?.querySelector('.avatar-initial');
    if (initialSpan) {
        initialSpan.textContent = '?';
    }
}

function applyTelegramTheme() {
    if (!tg) return;
    
    const themeParams = tg.themeParams;
    if (themeParams) {
        if (themeParams.bg_color) {
            document.documentElement.style.setProperty('--tg-theme-bg-color', themeParams.bg_color);
        }
        if (themeParams.text_color) {
            document.documentElement.style.setProperty('--tg-theme-text-color', themeParams.text_color);
        }
        if (themeParams.button_color) {
            document.documentElement.style.setProperty('--tg-theme-button-color', themeParams.button_color);
        }
        if (themeParams.button_text_color) {
            document.documentElement.style.setProperty('--tg-theme-button-text-color', themeParams.button_text_color);
        }
    }
}

function setupTelegramBackButton() {
    if (!tg || !tg.BackButton) return;
    
    tg.BackButton.hide();
    
    document.addEventListener('popupOpened', () => {
        tg.BackButton.show();
        tg.BackButton.onClick(() => {
            closeAllPopups();
            tg.BackButton.hide();
        });
    });
    
    document.addEventListener('popupClosed', () => {
        tg.BackButton.hide();
    });
}

function closeAllPopups() {
    closeFilterPopup();
    closeBottomSheet();
    closeActiveFiltersPopup();
}

// ===== FUNGSI LOAD GIFTS =====
async function loadGifts() {
    try {
        elements.loadingState.style.display = 'flex';

        const API_BASE_URL = 'https://involved-sue-tan-hundreds.trycloudflare.com';
        const response = await fetch(`${API_BASE_URL}/api/gifts?limit=1000`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        gifts = await response.json();

        if (!Array.isArray(gifts)) {
            throw new Error('Data yang diterima bukan array');
        }

        console.log(`✅ ${gifts.length} gift berhasil dimuat`);

        const giftSet = new Set();
        const modelSet = new Set();
        const symbolSet = new Set();
        const bgSet = new Set();

        gifts.forEach(gift => {
            const giftName = gift.nama || (gift.name ? gift.name.split('#')[0].trim() : gift.slug.split('-')[0]);
            giftSet.add(giftName);
            modelSet.add(gift.model);
            symbolSet.add(gift.symbol);
            bgSet.add(gift.bg);
        });

        filterOptions.gifts = Array.from(giftSet).sort();
        filterOptions.models = Array.from(modelSet).sort();
        filterOptions.symbols = Array.from(symbolSet).sort();
        filterOptions.bgs = Array.from(bgSet).sort();

        elements.loadingState.style.display = 'none';
        filterAndSortGifts();
    } catch (error) {
        console.error('Error loading gifts:', error);
        showError();
    }
}

// ===== FUNGSI NAVIGASI =====
function setupNavigationListeners() {
    if (navStore) navStore.addEventListener('click', () => switchPage('store'));
    if (navStats) navStats.addEventListener('click', () => switchPage('stats'));
    if (navProfile) navProfile.addEventListener('click', () => switchPage('profile'));
}

function switchPage(page) {
    currentPage = page;
    
    [navStore, navStats, navProfile].forEach(btn => {
        if (btn) btn.classList.remove('active');
    });
    
    if (page === 'store' && navStore) navStore.classList.add('active');
    else if (page === 'stats' && navStats) navStats.classList.add('active');
    else if (page === 'profile' && navProfile) navProfile.classList.add('active');
    
    if (page === 'store') {
        showStorePage();
    } else if (page === 'stats') {
        showStatsPage();
    } else if (page === 'profile') {
        showProfilePage();
    }
}

function showStorePage() {
    const filterSection = document.querySelector('.filter-section');
    if (filterSection) filterSection.style.display = 'block';
    
    const marketplaceHeader = document.querySelector('.marketplace-header');
    if (marketplaceHeader) marketplaceHeader.style.display = 'flex';
    
    filterAndSortGifts();
}

function showStatsPage() {
    const filterSection = document.querySelector('.filter-section');
    if (filterSection) filterSection.style.display = 'none';
    
    const marketplaceHeader = document.querySelector('.marketplace-header');
    if (marketplaceHeader) marketplaceHeader.style.display = 'none';
    
    elements.cardsGrid.innerHTML = `
        <div class="empty-state" style="grid-column: 1 / -1;">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" style="margin-bottom: 16px; opacity: 0.5;">
                <path d="M21 12V18C21 19.1046 20.1046 20 19 20H5C3.89543 20 3 19.1046 3 18V6C3 4.89543 3.89543 4 5 4H9" stroke-width="1.5"/>
                <path d="M15 4H21V10" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M21 4L12 13" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                <circle cx="12" cy="16" r="1" fill="currentColor"/>
                <circle cx="16" cy="12" r="1" fill="currentColor"/>
                <circle cx="8" cy="12" r="1" fill="currentColor"/>
            </svg>
            <h3>Stats Page</h3>
            <p style="margin-top: 8px;">Coming soon...</p>
        </div>
    `;
}

// ===== FUNGSI PROFILE PAGE =====
async function showProfilePage() {
    const filterSection = document.querySelector('.filter-section');
    if (filterSection) filterSection.style.display = 'none';

    const marketplaceHeader = document.querySelector('.marketplace-header');
    if (marketplaceHeader) marketplaceHeader.style.display = 'none';

    if (!telegramUser) {
        elements.cardsGrid.innerHTML = `
            <div class="profile-page">
                <div class="empty-state">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" style="margin-bottom: 16px; opacity: 0.5;">
                        <circle cx="12" cy="8" r="4" stroke-width="1.5"/>
                        <path d="M5 20V19C5 15.1 8.1 12 12 12C15.9 12 19 15.1 19 19V20" stroke-width="1.5" stroke-linecap="round"/>
                    </svg>
                    <h3>Please login first</h3>
                    <p>Open this app from Telegram</p>
                </div>
            </div>
        `;
        return;
    }

    elements.loadingState.style.display = 'flex';

    try {
        const API_BASE_URL = 'https://involved-sue-tan-hundreds.trycloudflare.com';
        
        // Fetch data user gifts
        const userResponse = await fetch(`${API_BASE_URL}/api/users/${telegramUser.id}`);

        if (!userResponse.ok) {
            throw new Error(`HTTP error! status: ${userResponse.status}`);
        }

        const userData = await userResponse.json();

        if (!userData.success) {
            throw new Error(userData.error || 'Unknown error');
        }

        userProfileData = userData.user.profile || {};
        userGifts = userData.user.added_gifts || [];

        // Fetch deposit history
        await fetchDepositHistory(telegramUser.id);
        
        // Fetch withdraw history
        await fetchWithdrawHistory(telegramUser.id);

        // Fetch all gifts from marketplace
        const giftsResponse = await fetch(`${API_BASE_URL}/api/gifts?limit=1000`);

        if (!giftsResponse.ok) {
            throw new Error(`HTTP error! status: ${giftsResponse.status}`);
        }

        const allMarketGifts = await giftsResponse.json();

        // Buat map untuk mencari posting berdasarkan slug
        const postingMap = {};
        allMarketGifts.forEach(gift => {
            if (gift.slug && gift.posting) {
                postingMap[gift.slug] = gift.posting;
            }
        });

        // Hitung total gifts berdasarkan status
        const listedGifts = userGifts.filter(gift => gift.is_listed === 1).length;
        const unlistedGifts = userGifts.filter(gift => gift.is_listed === 0 && gift.is_sold !== 1).length;
        const soldGiftsCount = userGifts.filter(gift => gift.is_sold === 1).length;

        // Gabungkan data userGifts dengan posting dari marketplace
        const allGifts = userGifts.map(gift => {
            if (gift.is_listed === 0) {
                return {
                    ...gift,
                    price: 0,
                    posting: gift.posting || postingMap[gift.slug] || 'https://t.me/market_wine/57/None'
                };
            }
            return {
                ...gift,
                posting: gift.posting || postingMap[gift.slug] || 'https://t.me/market_wine/57/None'
            };
        });

        elements.loadingState.style.display = 'none';

        // Render profile page dengan balance cards
        renderProfilePageWithBalance(allGifts, listedGifts, unlistedGifts, soldGiftsCount);

    } catch (error) {
        console.error('Error loading user gifts:', error);
        elements.loadingState.style.display = 'none';
        showProfileError(error.message);
    }
}

async function fetchDepositHistory(userId) {
  try {
    const API_BASE_URL = 'https://involved-sue-tan-hundreds.trycloudflare.com';
    const response = await fetch(`${API_BASE_URL}/api/deposit-history?user_id=${userId}`);

    if (response.ok) {
      const data = await response.json();
      if (data.success) {
        userDepositHistory = data.data || [];
        console.log('✅ Deposit history refreshed:', userDepositHistory.length, 'records');

        // Debug: hitung status
        const counts = {
          pending: userDepositHistory.filter(d => d.status === 'pending').length,
          paid: userDepositHistory.filter(d => d.status === 'paid').length,
          expired: userDepositHistory.filter(d => d.status === 'expired').length
        };
        console.log('📊 Deposit status counts:', counts);

        const historyPopup = document.getElementById('historyPopupOverlay');
        if (historyPopup && historyPopup.classList.contains('active')) {
          const activeTab = document.querySelector('.history-tab.active')?.textContent.toLowerCase() || 'deposit';
          updateHistoryPopupContent(historyPopup, activeTab);
        }
      }
    }
  } catch (error) {
    console.error('Error fetching deposit history:', error);
    userDepositHistory = [];
  }
}

async function fetchWithdrawHistory(userId) {
    try {
        const API_BASE_URL = 'https://involved-sue-tan-hundreds.trycloudflare.com';
        const response = await fetch(`${API_BASE_URL}/api/withdraw-history?user_id=${userId}`);
        
        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                userWithdrawHistory = data.data || [];
            }
        }
    } catch (error) {
        console.error('Error fetching withdraw history:', error);
        userWithdrawHistory = [];
    }
}

function renderProfilePageWithBalance(gifts, listedCount, unlistedCount, soldCount) {
    const firstName = telegramUser.first_name || '';
    const lastName = telegramUser.last_name || '';
    const fullName = `${firstName} ${lastName}`.trim() || 'User';
    const username = telegramUser.username ? `@${telegramUser.username}` : '-';
    const isPremium = telegramUser.is_premium;
    
    // Format balance
    const saldoFormatted = formatRupiah(userBalance);
    const wicashBalance = userProfileData.wicash || 0;
    const wicashFormatted = formatRupiah(wicashBalance);
    
    // Avatar HTML
    const avatarInitial = firstName.charAt(0).toUpperCase() || '?';
    
    const profileHTML = `
        <div class="profile-page">
            <!-- Profile Header -->
            <div class="profile-header glass-panel">
                <div class="profile-avatar-wrapper">
                    <div class="profile-avatar" id="profilePageAvatar">
                        <span class="avatar-initial">${avatarInitial}</span>
                    </div>
                    <div class="profile-premium-badge ${isPremium ? '' : 'free'}">
                        ${isPremium ? '⭐' : '🔹'}
                    </div>
                </div>
                
                <div class="profile-info">
                    <h3 class="profile-name">${fullName}</h3>
                    <p class="profile-username">${username}</p>
                </div>
                
                <!-- Combined Balance Card -->
                <div class="profile-balance-card" onclick="openFinancePopup()">
                    <div class="balances">
                        <div class="balance-item saldo">
                            <div class="balance-icon">💰</div>
                            <span class="balance-text">Saldo</span>
                            <span class="balance-amount">${saldoFormatted}</span>
                        </div>
                        <div class="balance-item wicash">
                            <div class="balance-icon">💎</div>
                            <span class="balance-text">Wicash</span>
                            <span class="balance-amount">${wicashFormatted}</span>
                        </div>
                    </div>
                    
                    <button class="finance-button" onclick="event.stopPropagation(); openFinancePopup()">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <rect x="2" y="6" width="20" height="12" rx="2" stroke-width="1.5"/>
                            <path d="M16 12C16 13.1046 15.1046 14 14 14H10C8.89543 14 8 13.1046 8 12C8 10.8954 8.89543 10 10 10H14C15.1046 10 16 10.8954 16 12Z" stroke-width="1.5"/>
                            <path d="M18 10H20" stroke-width="1.5" stroke-linecap="round"/>
                            <path d="M4 10H6" stroke-width="1.5" stroke-linecap="round"/>
                        </svg>
                    </button>
                </div>
            </div>
            
            <!-- Stats Container -->
            <div class="stats-container">
                <div class="stat-item">
                    <div class="stat-value">${listedCount}</div>
                    <div class="stat-label listed">LISTED</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${unlistedCount}</div>
                    <div class="stat-label unlisted">UNLISTED</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${soldCount}</div>
                    <div class="stat-label sold">SOLD</div>
                </div>
            </div>
            
            <!-- Section Title -->
            <div class="section-title">My Gifts</div>
    `;
    
    if (gifts.length === 0) {
        elements.cardsGrid.innerHTML = profileHTML + `
            <div class="empty-state">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" style="margin-bottom: 16px; opacity: 0.5;">
                    <rect x="3" y="4" width="18" height="16" rx="2" stroke-width="1.5"/>
                    <path d="M8 10H16M8 14H12" stroke-width="1.5" stroke-linecap="round"/>
                </svg>
                <h3>No gifts found</h3>
                <p style="margin-top: 8px;">You don't have any gifts yet</p>
            </div>
        `;
        return;
    }
    
    const giftsHtml = gifts.map(gift => {
        const cleanName = gift.nama || gift.slug.split('-')[0];
        const formattedName = formatGiftName(cleanName);
        const giftId = extractIdFromSlug(gift.slug);
        
        let statusClass = '';
        let statusText = '';
        if (gift.is_sold === 1) {
            statusClass = 'sold';
            statusText = 'SOLD';
        } else if (gift.is_listed === 0) {
            statusClass = 'unlisted';
            statusText = 'UNLISTED';
        } else {
            statusClass = 'listed';
            statusText = 'LISTED';
        }
        
        return `
        <div class="profile-gift-card ${statusClass}" onclick="openUserGiftSheet(${JSON.stringify({
            ...gift,
            formattedName,
            giftId
        }).replace(/"/g, '&quot;')})">
            <div class="profile-card-image-wrapper">
                <img class="profile-card-image" src="https://nft.fragment.com/gift/${gift.slug}.medium.jpg" 
                     alt="${gift.name}" 
                     onerror="this.src='https://via.placeholder.com/400?text=NFT+Gift'">
                <div class="profile-card-status ${statusClass}">${statusText}</div>
            </div>
            <div class="profile-card-content">
                <div class="profile-card-name">${formattedName}</div>
                <div class="profile-card-id">#${giftId}</div>
                <div class="profile-card-price">💰 ${gift.is_listed === 1 ? formatPrice(gift.price) : '0'}</div>
            </div>
        </div>
    `}).join('');
    
    elements.cardsGrid.innerHTML = profileHTML + `
        <div class="profile-gifts-grid">
            ${giftsHtml}
        </div>
    `;
    
    // Copy foto profil jika sudah ada dari sebelumnya
    const existingAvatar = document.querySelector('#userAvatar .avatar-image');
    if (existingAvatar) {
        const profileAvatar = document.querySelector('#profilePageAvatar');
        if (profileAvatar) {
            profileAvatar.innerHTML = '';
            const imgClone = existingAvatar.cloneNode(true);
            profileAvatar.appendChild(imgClone);
        }
    }
}

function showProfileError(message) {
    elements.cardsGrid.innerHTML = `
        <div class="profile-page">
            <div class="empty-state">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" style="margin-bottom: 16px; opacity: 0.5;">
                    <circle cx="12" cy="12" r="10" stroke-width="1.5"/>
                    <path d="M12 8V12M12 16H12.01" stroke-width="1.5" stroke-linecap="round"/>
                </svg>
                <h3>Failed to load your gifts</h3>
                <p style="margin-top: 8px;">${message}</p>
                <button onclick="showProfilePage()" style="margin-top: 16px; padding: 12px 24px; background: var(--tg-primary); border: none; border-radius: var(--radius-md); color: white; font-weight: 600; cursor: pointer;">Try Again</button>
            </div>
        </div>
    `;
}

// ===== FUNGSI FINANCE POPUP =====
function openFinancePopup() {
    let overlay = document.getElementById('financePopupOverlay');
    
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'financePopupOverlay';
        overlay.className = 'finance-popup-overlay';
        
        document.body.appendChild(overlay);
    }
    
    updateFinancePopupContent(overlay);
    
    overlay.classList.add('active');
    setTimeout(() => {
        const popup = overlay.querySelector('.finance-popup');
        if (popup) popup.classList.add('active');
    }, 10);
    
    document.dispatchEvent(new Event('popupOpened'));
}

function updateFinancePopupContent(overlay) {
  const saldoFormatted = formatRupiah(userBalance);
  const wicashBalance = userProfileData?.wicash || 0;
  const wicashFormatted = formatRupiah(wicashBalance);

  overlay.innerHTML = `
        <div class="finance-popup" id="financePopup">
            <div class="finance-popup-header">
                <h3 class="finance-popup-title">Financial</h3>
                <button class="finance-popup-close" onclick="closeFinancePopup()">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M18 6L6 18M6 6L18 18" stroke-linecap="round"/>
                    </svg>
                </button>
            </div>
            
            <div class="finance-popup-content">
                <div class="finance-balance-display">
                    <div class="finance-balance-row">
                        <span class="finance-balance-label">
                            <span class="finance-balance-icon saldo">💰</span>
                            Saldo
                        </span>
                        <span class="finance-balance-amount">${saldoFormatted}</span>
                    </div>
                    <div class="finance-balance-row">
                        <span class="finance-balance-label">
                            <span class="finance-balance-icon wicash">💎</span>
                            Wicash
                        </span>
                        <span class="finance-balance-amount">${wicashFormatted}</span>
                    </div>
                </div>
                
                <div class="finance-action-buttons">
                    <button class="finance-action-btn deposit" onclick="openDepositModal()">
                        <span class="finance-action-icon">💰</span>
                        <span class="finance-action-label">Deposit</span>
                        <span class="finance-action-desc">Add funds</span>
                    </button>
                    
                    <button class="finance-action-btn withdraw" onclick="openWithdrawModal()">
                        <span class="finance-action-icon">📤</span>
                        <span class="finance-action-label">Withdraw</span>
                        <span class="finance-action-desc">Cash out</span>
                    </button>
                    
                    <button class="finance-action-btn history" onclick="openHistoryPopup()">
                        <span class="finance-action-icon">📋</span>
                        <span class="finance-action-label">History</span>
                        <span class="finance-action-desc">View transactions</span>
                    </button>
                </div>
            </div>
        </div>
    `;
}

function closeFinancePopup() {
    const overlay = document.getElementById('financePopupOverlay');
    const popup = document.getElementById('financePopup');
    
    if (popup) popup.classList.remove('active');
    if (overlay) {
        setTimeout(() => {
            overlay.classList.remove('active');
            document.dispatchEvent(new Event('popupClosed'));
        }, 300);
    }
}

// ===== FUNGSI WALLET POPUP (UNTUK KOMPATIBILITAS) =====
function openWalletPopup() {
    openFinancePopup();
}

function closeWalletPopup() {
    closeFinancePopup();
}

// ===== FUNGSI HISTORY POPUP =====
function openHistoryPopup() {
    closeFinancePopup();
    
    let overlay = document.getElementById('historyPopupOverlay');
    
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'historyPopupOverlay';
        overlay.className = 'history-popup-overlay';
        
        document.body.appendChild(overlay);
    }
    
    updateHistoryPopupContent(overlay, 'deposit');
    
    overlay.classList.add('active');
    setTimeout(() => {
        const popup = overlay.querySelector('.history-popup');
        if (popup) popup.classList.add('active');
    }, 10);
    
    document.dispatchEvent(new Event('popupOpened'));
}

function updateHistoryPopupContent(overlay, tab = 'deposit') {
  overlay.innerHTML = `
        <div class="history-popup" id="historyPopup">
            <div class="history-popup-header">
                <h3 class="history-popup-title">Transaction History</h3>
                <div style="display: flex; gap: 8px;">
                    <button class="history-popup-refresh" onclick="refreshHistory()" title="Refresh">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path d="M23 4v6h-6M1 20v-6h6" stroke-width="1.5" stroke-linecap="round"/>
                            <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15" stroke-width="1.5" stroke-linecap="round"/>
                        </svg>
                    </button>
                    <button class="history-popup-close" onclick="closeHistoryPopup()">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path d="M18 6L6 18M6 6L18 18" stroke-width="2" stroke-linecap="round"/>
                        </svg>
                    </button>
                </div>
            </div>
            
            <div class="history-popup-content">
                <div class="history-tabs">
                    <button class="history-tab ${tab === 'deposit' ? 'active' : ''}" onclick="switchHistoryTab('deposit')">Deposit</button>
                    <button class="history-tab ${tab === 'withdraw' ? 'active' : ''}" onclick="switchHistoryTab('withdraw')">Withdraw</button>
                </div>
                
                <div class="history-list" id="historyList">
                    ${renderHistoryList(tab)}
                </div>
            </div>
        </div>
    `;
}

// Fungsi refresh
window.refreshHistory = async function() {
  if (telegramUser) {
    showToast('Refreshing history...');
    await fetchDepositHistory(telegramUser.id);
    await fetchWithdrawHistory(telegramUser.id);

    const overlay = document.getElementById('historyPopupOverlay');
    if (overlay && overlay.classList.contains('active')) {
      const activeTab = document.querySelector('.history-tab.active')?.textContent.toLowerCase() || 'deposit';
      updateHistoryPopupContent(overlay, activeTab);
    }

    showToast('History refreshed!');
  }
};

function switchHistoryTab(tab) {
    const overlay = document.getElementById('historyPopupOverlay');
    if (overlay) {
        updateHistoryPopupContent(overlay, tab);
    }
}

function renderHistoryList(type) {
    const history = type === 'deposit' ? userDepositHistory : userWithdrawHistory;
    
    if (history.length === 0) {
        return `
            <div class="history-empty">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" style="margin-bottom: 16px; opacity: 0.3;">
                    <circle cx="12" cy="12" r="10" stroke-width="1.5"/>
                    <path d="M12 8V12M12 16H12.01" stroke-width="1.5" stroke-linecap="round"/>
                </svg>
                <p>No ${type} history found</p>
            </div>
        `;
    }
    
    return history.map(item => {
        const status = item.status || 'pending';
        const statusIcon = {
            'pending': '⏳',
            'paid': '✅',
            'expired': '❌'
        }[status] || '⏳';
        
        const statusColor = {
            'pending': '#FF9800',
            'paid': '#4CAF50',
            'expired': '#F44336'
        }[status];
        
        const date = new Date(item.created_at * 1000).toLocaleDateString('id-ID');
        const time = new Date(item.created_at * 1000).toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' });
        
        // 🔥 UBAH: Untuk status pending, langsung buka deposit modal tanpa popup lagi
        const onClick = type === 'deposit' && status === 'pending' 
            ? `openDepositModalWithHistory('${item.transaction_id}')` 
            : '';
        
        return `
        <div class="history-item ${status}" onclick="${onClick}">
            <div class="history-item-header">
                <span class="history-item-status ${status}">
                    <span class="history-status-icon" style="background: ${statusColor}20; color: ${statusColor}">${statusIcon}</span>
                    ${status.toUpperCase()}
                </span>
                <span class="history-item-amount">${formatRupiah(item.amount)}</span>
            </div>
            <div class="history-item-detail">
                <span class="history-item-id">${item.transaction_id?.substring(0, 8)}...</span>
                <span>${date} ${time}</span>
            </div>
        </div>
    `}).join('');
}

// 🔥 FUNGSI BARU: Buka deposit modal langsung dari history tanpa popup
async function openDepositModalWithHistory(transactionId) {
    try {
        const API_BASE_URL = 'https://involved-sue-tan-hundreds.trycloudflare.com';
        const response = await fetch(`${API_BASE_URL}/api/deposit-status?transaction_id=${transactionId}`);
        const data = await response.json();

        if (data.success) {
            // Cek apakah status masih pending
            if (data.data.status === 'pending') {
                // Hitung sisa waktu expired
                const now = Math.floor(Date.now() / 1000);
                const expiredAt = data.data.expired_at || (now + 300); // Default 5 menit

                const qrData = {
                    transaction_id: transactionId,
                    amount: data.data.amount,
                    qr_url: data.data.qr_url,
                    expired_at: expiredAt
                };

                // Tutup history popup dulu
                closeHistoryPopup();
                
                // Buka deposit modal dengan QR code
                openDepositModalWithQR(qrData);
            } else {
                showToast(`Deposit status: ${data.data.status.toUpperCase()}`);
            }
        }
    } catch (error) {
        console.error('Error fetching deposit status:', error);
        showToast('Failed to load deposit details');
    }
}

function closeHistoryPopup() {
    const overlay = document.getElementById('historyPopupOverlay');
    const popup = document.getElementById('historyPopup');
    
    if (popup) popup.classList.remove('active');
    if (overlay) {
        setTimeout(() => {
            overlay.classList.remove('active');
            document.dispatchEvent(new Event('popupClosed'));
        }, 300);
    }
}

// ===== FUNGSI DEPOSIT =====
function openDepositModal() {
    closeFinancePopup();

    // Cek apakah modal sudah ada
    let modal = document.getElementById('depositModal');

    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'depositModal';
        modal.className = 'deposit-modal';

        modal.innerHTML = `
            <div class="deposit-modal-content" id="depositModalContent">
                <div class="deposit-modal-header">
                    <h3 class="deposit-modal-title">Deposit</h3>
                    <button class="deposit-modal-close" onclick="closeDepositModal()">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path d="M18 6L6 18M6 6L18 18" stroke-width="2" stroke-linecap="round"/>
                        </svg>
                    </button>
                </div>
                
                <div class="deposit-content" id="depositContent">
                    <!-- Content will be dynamically loaded -->
                    <div class="deposit-loading">
                        <div class="spinner"></div>
                        <p>Preparing deposit...</p>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
    }

    modal.classList.add('active');
    setTimeout(() => {
        const content = document.getElementById('depositModalContent');
        if (content) content.classList.add('active');
    }, 10);

    // Load deposit form
    showDepositForm();

    document.dispatchEvent(new Event('popupOpened'));
}

function closeDepositModal() {
    const modal = document.getElementById('depositModal');
    const content = document.getElementById('depositModalContent');

    if (content) content.classList.remove('active');
    if (modal) {
        setTimeout(() => {
            modal.classList.remove('active');
            document.dispatchEvent(new Event('popupClosed'));

            // Stop checking interval jika ada
            if (depositCheckInterval) {
                clearInterval(depositCheckInterval);
                depositCheckInterval = null;
            }
        }, 300);
    }
}

// ===== FUNGSI DEPOSIT - PERBAIKI BAGIAN INI =====
function showDepositForm() {
  const content = document.getElementById('depositContent');
  if (!content) return;

  content.innerHTML = `
        <div>
            <p style="margin-bottom: 16px; color: rgba(255,255,255,0.6);">Enter amount to deposit (IDR)</p>
            
            <input type="number" id="depositAmount" class="deposit-amount-input" placeholder="10000" min="1000" max="10000000" step="1000">
            
            <div class="deposit-quick-amounts">
                <button class="quick-amount-btn" onclick="setDepositAmount(10000)">10K</button>
                <button class="quick-amount-btn" onclick="setDepositAmount(25000)">25K</button>
                <button class="quick-amount-btn" onclick="setDepositAmount(50000)">50K</button>
                <button class="quick-amount-btn" onclick="setDepositAmount(100000)">100K</button>
                <button class="quick-amount-btn" onclick="setDepositAmount(250000)">250K</button>
                <button class="quick-amount-btn" onclick="setDepositAmount(500000)">500K</button>
                <button class="quick-amount-btn" onclick="setDepositAmount(1000000)">1M</button>
                <button class="quick-amount-btn" onclick="setDepositAmount(2500000)">2.5M</button>
                <button class="quick-amount-btn" onclick="setDepositAmount(5000000)">5M</button>
            </div>
            
            <button class="finance-action-btn deposit" onclick="processDeposit()">
                <span class="finance-action-icon">💰</span>
                <span class="finance-action-label">Generate QRIS</span>
            </button>
        </div>
    `;
}

async function processDeposit() {
  const input = document.getElementById('depositAmount');
  const amount = parseInt(input.value);

  if (isNaN(amount) || amount < 1000) {
    showToast('Minimum deposit is Rp 1.000');
    return;
  }

  if (amount > 10000000) {
    showToast('Maximum deposit is Rp 10.000.000');
    return;
  }

  const content = document.getElementById('depositContent');
  content.innerHTML = `
        <div class="deposit-loading">
            <div class="spinner"></div>
            <p>Generating QRIS...</p>
        </div>
    `;

  try {
    const API_BASE_URL = 'https://involved-sue-tan-hundreds.trycloudflare.com';

    const response = await fetch(`${API_BASE_URL}/api/deposit-request`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: telegramUser.id,
        amount: amount
      })
    });

    const data = await response.json();

    if (data.success) {
      currentQRData = data.data;
      showQRCode(data.data);
      startDepositMonitoring(data.data.transaction_id, data.data.expired_at);

      setTimeout(() => {
        if (currentPage === 'profile') {
          fetchDepositHistory(telegramUser.id);
        }
      }, 1000);

    } else {
      showToast(`Error: ${data.error || 'Failed to generate QRIS'}`);
      showDepositForm();
    }

  } catch (error) {
    console.error('Error processing deposit:', error);
    showToast('Failed to process deposit. Please try again.');
    showDepositForm();
  }
}

function setDepositAmount(amount) {
    const input = document.getElementById('depositAmount');
    if (input) {
        input.value = amount;
        currentDepositAmount = amount;
    }
}

function showQRCode(qrData) {
  const content = document.getElementById('depositContent');
  if (!content) return;

  const amountFormatted = formatRupiah(qrData.amount);
  const expiryTimestamp = qrData.expired_at * 1000;

  content.innerHTML = `
        <div>
            <div class="qr-code-container">
                <img src="${qrData.qr_url}" class="qr-code-image" alt="QRIS">
                <div class="qr-transaction-id">ID: ${qrData.transaction_id}</div>
                <div class="qr-expiry active">
                    <span class="expiry-label">⏰</span>
                    <span class="countdown-timer" id="countdownTimer" data-expiry="${expiryTimestamp}">05:00</span>
                </div>
            </div>
            
            <div style="text-align: center; margin-bottom: 16px;">
                <div style="font-size: 20px; font-weight: 700; color: var(--tg-primary);">${amountFormatted}</div>
            </div>
            
            <div style="background: rgba(0,0,0,0.03); border-radius: 12px; padding: 12px; margin-bottom: 16px;">
                <p style="margin-bottom: 8px;">📱 Scan with:</p>
                <div style="display: flex; gap: 8px; justify-content: center;">
                    <span style="padding: 4px 8px; background: #00B3FF; color: white; border-radius: 4px;">DANA</span>
                    <span style="padding: 4px 8px; background: #01A75B; color: white; border-radius: 4px;">OVO</span>
                    <span style="padding: 4px 8px; background: #0054B2; color: white; border-radius: 4px;">GoPay</span>
                    <span style="padding: 4px 8px; background: #D32F2F; color: white; border-radius: 4px;">ShopeePay</span>
                </div>
            </div>
            
            <p style="font-size: 12px; color: var(--tg-text-hint); text-align: center;">
                Scan QRIS above using your e-wallet.<br>
                Do not change the amount when paying.<br>
                Balance will be added automatically.
            </p>
            
            <button class="finance-action-btn deposit" onclick="closeDepositModal()" style="width: 100%; margin-top: 16px;">
                <span class="finance-action-label">Close</span>
            </button>
        </div>
    `;

  // Mulai hitung mundur
  startCountdown(expiryTimestamp);
}

// 🔥 FUNGSI BARU: Hitung mundur countdown dengan class
function startCountdown(expiryTimestamp) {
  const timerElement = document.getElementById('countdownTimer');
  if (!timerElement) return;

  // Hapus interval sebelumnya jika ada
  if (window.countdownInterval) {
    clearInterval(window.countdownInterval);
  }

  function updateCountdown() {
    const now = Date.now();
    const distance = expiryTimestamp - now;

    if (distance <= 0) {
      // Waktu habis
      timerElement.textContent = '00:00';
      timerElement.classList.remove('danger');
      timerElement.classList.add('expired');

      // Hentikan interval
      if (window.countdownInterval) {
        clearInterval(window.countdownInterval);
        window.countdownInterval = null;
      }

      // Update tampilan expired
      const expiryElement = timerElement.closest('.qr-expiry');
      if (expiryElement) {
        expiryElement.innerHTML = '<span class="expiry-label">⏰</span> <span class="countdown-timer expired">EXPIRED</span>';
      }
      return;
    }

    // Hitung menit dan detik
    const minutes = Math.floor(distance / (1000 * 60));
    let seconds = Math.floor((distance % (1000 * 60)) / 1000);

    // Format 2 digit
    const minutesStr = minutes.toString().padStart(2, '0');
    const secondsStr = seconds.toString().padStart(2, '0');

    timerElement.textContent = `${minutesStr}:${secondsStr}`;

    // Tambah/remove class berdasarkan sisa waktu
    if (distance < 60000) { // < 1 menit
      timerElement.classList.add('danger');
      timerElement.classList.remove('expired');
    } else {
      timerElement.classList.remove('danger', 'expired');
    }
  }

  // Update setiap detik
  updateCountdown(); // Jalankan langsung
  window.countdownInterval = setInterval(updateCountdown, 1000);
}

function startDepositMonitoring(transactionId, expiredAt) {
    // Stop existing interval
    if (depositCheckInterval) {
        clearInterval(depositCheckInterval);
    }

    // Check every 3 seconds
    depositCheckInterval = setInterval(async () => {
        const now = Math.floor(Date.now() / 1000);

        // Check if expired
        if (now > expiredAt) {
            clearInterval(depositCheckInterval);
            depositCheckInterval = null;

            showToast('Deposit expired. Please try again.');
            closeDepositModal();
            return;
        }

        try {
            const API_BASE_URL = 'https://involved-sue-tan-hundreds.trycloudflare.com';
            const response = await fetch(`${API_BASE_URL}/api/deposit-status?transaction_id=${transactionId}`);
            const data = await response.json();

            if (data.success && data.data.status === 'paid') {
                clearInterval(depositCheckInterval);
                depositCheckInterval = null;

                // Update user balance
                userBalance = data.data.new_balance;

                showToast('✅ Deposit successful! Balance added.');

                // Update display
                updateUserBalanceDisplay();

                // Close modal after 2 seconds
                setTimeout(() => {
                    closeDepositModal();

                    // Refresh profile to show new balance
                    if (currentPage === 'profile') {
                        showProfilePage();
                    }
                }, 2000);
            }
        } catch (error) {
            console.error('Error checking deposit status:', error);
        }
    }, 3000);
}

// ===== FUNGSI OPEN DEPOSIT MODAL DENGAN QR (untuk history) =====
function openDepositModalWithQR(qrData) {
    closeHistoryPopup();

    let modal = document.getElementById('depositModal');

    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'depositModal';
        modal.className = 'deposit-modal';

        document.body.appendChild(modal);
    }

    modal.classList.add('active');
    setTimeout(() => {
        const content = document.getElementById('depositModalContent');
        if (content) content.classList.add('active');
    }, 10);

    showQRCode(qrData);
    startDepositMonitoring(qrData.transaction_id, qrData.expired_at);

    document.dispatchEvent(new Event('popupOpened'));
}

// ===== FUNGSI WITHDRAW =====
function openWithdrawModal() {
    closeFinancePopup();

    // Redirect ke bot untuk withdraw
    if (confirm('Withdraw will be processed via bot. Open Telegram?')) {
        window.open('https://t.me/marketaldibot', '_blank');
    }
}

// ===== FUNGSI OPEN BOTTOM SHEET UNTUK GIFT USER =====
window.openUserGiftSheet = function(gift) {
    const cleanName = gift.formattedName || formatGiftName(gift.nama || gift.slug.split('-')[0]);
    const formattedPrice = gift.is_listed === 1 ? formatPriceRupiah(gift.price) : 'UNLISTED';
    const giftId = gift.giftId || extractIdFromSlug(gift.slug);
    
    // Gunakan display yang sudah diformat atau format langsung
    const modelValue = gift.modelDisplay || (gift.model && gift.model_rarity 
        ? `${gift.model} (${gift.model_rarity})` 
        : (gift.model || '-'));
    
    const symbolValue = gift.symbolDisplay || (gift.symbol && gift.symbol_rarity 
        ? `${gift.symbol} (${gift.symbol_rarity})` 
        : (gift.symbol || '-'));
    
    const bgValue = gift.bgDisplay || (gift.background && gift.background_rarity 
        ? `${gift.background} (${gift.background_rarity})` 
        : (gift.background || '-'));
    
    const slugId = gift.slug_id || generateSlugId(gift);
    
    // Tentukan teks tombol berdasarkan status is_listed
    const buttonText = gift.is_listed === 1 ? 'UNLISTED' : 'LISTED';
    
    // Ambil posting link dari gift
    const postedLink = gift.posting || 'https://t.me/market_wine/57/None';
    
    // Price row hanya ditampilkan jika listed
    const priceRow = gift.is_listed === 1 ? `
        <div class="sheet-price-row">
            <span class="sheet-price-label">Price</span>
            <span class="sheet-price-value">💰 ${formattedPrice}</span>
        </div>
    ` : '';
    
    const content = `
        <div class="sheet-item-detail">
            <div class="sheet-lottie-wrapper">
                <div class="sheet-lottie-container">
                    <lottie-player
                        src="https://nft.fragment.com/gift/${gift.slug}.lottie.json"
                        background="transparent"
                        speed="1"
                        style="width: 100%; height: 100%;"
                        loop="false"
                        count="1"
                        autoplay>
                    </lottie-player>
                </div>
            </div>
            <div class="sheet-info">
                <div class="sheet-name-container">
                    <span class="sheet-name">${cleanName}</span>
                    <span class="sheet-id">${giftId}</span>
                </div>
                
                <div class="sheet-data-container">
                    <div class="sheet-data-row">
                        <span class="sheet-data-label">Model</span>
                        <span class="sheet-data-value">${modelValue}</span>
                    </div>
                    <div class="sheet-data-row">
                        <span class="sheet-data-label">Symbol</span>
                        <span class="sheet-data-value">${symbolValue}</span>
                    </div>
                    <div class="sheet-data-row">
                        <span class="sheet-data-label">Backdrop</span>
                        <span class="sheet-data-value">${bgValue}</span>
                    </div>
                </div>
                
                ${priceRow}
            </div>
        </div>
        <div class="sheet-actions" style="grid-template-columns: 1fr 1fr 1fr;">
            <button class="btn btn-nego" onclick="toggleListingStatus('${gift.slug}')">${buttonText}</button>
            <a href="${postedLink}" class="btn btn-gift-share" target="_blank" title="View Post" style="width: 48px; height: 48px; border-radius: 50%; display: flex; align-items: center; justify-content: center; background: rgba(135, 116, 225, 0.15); border: 1px solid rgba(135, 116, 225, 0.3); color: var(--tg-primary-light);">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path d="M4 4v16h16V4H4z" stroke-width="1.5"/>
                    <path d="M8 8h8M8 12h6M8 16h4" stroke-width="1.5" stroke-linecap="round"/>
                </svg>
            </a>
            <button class="btn btn-buy" onclick="editPrice('${gift.slug}')">EDIT PRICE</button>
        </div>
        <div class="sheet-share">
            <button class="btn btn-gift-share" onclick="shareGift('${slugId}', event)" style="width: 100%; padding: 12px;">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" style="margin-right: 8px;">
                    <path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8" stroke-width="1.5"/>
                    <polyline points="16 6 12 2 8 6" stroke-width="1.5"/>
                    <line x1="12" y1="2" x2="12" y2="15" stroke-width="1.5"/>
                </svg>
                SHARE GIFT
            </button>
        </div>
    `;
    
    elements.sheetContent.innerHTML = content;
    
    document.body.classList.add('sheet-open');
    elements.bottomSheetOverlay.classList.add('active');
    setTimeout(() => elements.bottomSheet.classList.add('active'), 10);
    document.dispatchEvent(new Event('popupOpened'));
};

// Fungsi sementara untuk unlist (sekarang menggunakan toggleListingStatus)
window.unlistGift = function(slug) {
    toggleListingStatus(slug);
};

// Update fungsi editPrice
window.editPrice = async function(slug) {
    closeBottomSheet();

    const newPrice = prompt("Enter new price (in Rupiah):", "");

    if (!newPrice) return;

    const priceNumber = parseInt(newPrice.replace(/[^0-9]/g, ''));
    if (isNaN(priceNumber) || priceNumber <= 0) {
        showToast('Invalid price!');
        return;
    }

    showToast('Updating price...', 0);

    try {
        const API_BASE_URL = 'https://involved-sue-tan-hundreds.trycloudflare.com';

        const response = await fetch(`${API_BASE_URL}/api/gift/edit-price`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                slug: slug,
                price: priceNumber,
                user_id: telegramUser ? telegramUser.id : null
            })
        });

        const data = await response.json();

        if (data.success) {
            showToast('Price updated successfully! ✅');

            // Refresh halaman profil untuk menampilkan harga baru
            if (currentPage === 'profile') {
                setTimeout(() => showProfilePage(), 1500);
            }
        } else {
            showToast(`Error: ${data.error || 'Failed to update price'}`);
        }

    } catch (error) {
        console.error('Error updating price:', error);
        showToast('Failed to update price. Check console for details.');
    }
};

// ===== FUNGSI LOTTIE =====
function getLottieUrl(slug) {
    return `https://nft.fragment.com/gift/${slug}.lottie.json`;
}

window.toggleLottie = function(button, slug, event) {
    if (event) {
        event.stopPropagation();
    }
    
    const card = button.closest('.gift-card');
    const imageWrapper = card.querySelector('.card-image-wrapper');
    const lottieContainer = imageWrapper.querySelector('.lottie-container');
    const fallbackImage = imageWrapper.querySelector('.fallback-image');
    const skeleton = lottieContainer.querySelector('.lottie-skeleton');
    
    button.classList.toggle('active');
    
    if (button.classList.contains('active')) {
        lottieContainer.classList.add('active');
        if (fallbackImage) {
            fallbackImage.style.display = 'none';
        }
        
        if (skeleton) {
            skeleton.classList.add('active');
        } else {
            const newSkeleton = document.createElement('div');
            newSkeleton.className = 'lottie-skeleton active';
            lottieContainer.appendChild(newSkeleton);
        }
        
        loadLottieAnimation(lottieContainer, slug, button);
    } else {
        lottieContainer.classList.remove('active');
        if (fallbackImage) {
            fallbackImage.style.display = 'block';
        }
        
        const currentSkeleton = lottieContainer.querySelector('.lottie-skeleton');
        if (currentSkeleton) {
            currentSkeleton.classList.remove('active');
        }
        
        lottieContainer.innerHTML = '';
        
        const newSkeleton = document.createElement('div');
        newSkeleton.className = 'lottie-skeleton';
        lottieContainer.appendChild(newSkeleton);
    }
};

async function loadLottieAnimation(lottieContainer, slug, button) {
    if (!lottieContainer) return;
    
    const lottieUrl = getLottieUrl(slug);
    const skeleton = lottieContainer.querySelector('.lottie-skeleton');
    
    if (lottieCache.has(lottieUrl)) {
        const cachedData = lottieCache.get(lottieUrl);
        
        if (skeleton) {
            skeleton.classList.remove('active');
        }
        
        renderLottiePlayer(lottieContainer, cachedData);
        return;
    }
    
    try {
        const response = await fetch(lottieUrl);
        if (!response.ok) throw new Error('Lottie not found');
        
        const lottieData = await response.json();
        lottieCache.set(lottieUrl, lottieData);
        
        if (skeleton) {
            skeleton.classList.remove('active');
        }
        
        renderLottiePlayer(lottieContainer, lottieData);
    } catch (error) {
        console.warn(`Failed to load Lottie for ${slug}:`, error);
        
        if (skeleton) {
            skeleton.classList.remove('active');
        }
        
        if (button) {
            button.classList.remove('active');
        }
        
        lottieContainer.classList.remove('active');
        const imageWrapper = lottieContainer.closest('.card-image-wrapper');
        if (imageWrapper) {
            const fallbackImg = imageWrapper.querySelector('.fallback-image');
            if (fallbackImg) {
                fallbackImg.style.display = 'block';
            }
        }
        
        if (button) {
            button.style.opacity = '0.5';
            button.style.cursor = 'not-allowed';
        }
    }
}

function renderLottiePlayer(container, lottieData) {
    const skeleton = container.querySelector('.lottie-skeleton');
    container.innerHTML = '';
    if (skeleton) {
        container.appendChild(skeleton);
    }
    
    const player = document.createElement('lottie-player');
    player.setAttribute('autoplay', '');
    player.setAttribute('loop', 'false');
    player.setAttribute('mode', 'normal');
    player.setAttribute('style', 'width: 100%; height: 100%;');
    player.setAttribute('count', '1');
    
    const lottieJson = JSON.stringify(lottieData);
    player.setAttribute('src', `data:application/json;charset=utf-8,${encodeURIComponent(lottieJson)}`);
    
    container.appendChild(player);
    
    player.addEventListener('load', () => {
        player.setAttribute('loop', 'false');
        player.setAttribute('count', '1');
        
        if (skeleton) {
            skeleton.classList.remove('active');
        }
    });
    
    player.addEventListener('complete', () => {
        console.log('Animation completed');
    });
}

// ===== FUNGSI UI =====
function updateSearchClearButton() {
    if (elements.idSearchInput.value.length > 0) {
        elements.idSearchClear.classList.add('visible');
    } else {
        elements.idSearchClear.classList.remove('visible');
    }
}

function setupEventListeners() {
    elements.idSearchInput.addEventListener('input', (e) => {
        activeFilters.id = e.target.value;
        filterAndSortGifts();
        renderActiveFilters();
        updateSearchClearButton();
    });
    
    elements.idSearchClear.addEventListener('click', () => {
        elements.idSearchInput.value = '';
        activeFilters.id = '';
        filterAndSortGifts();
        renderActiveFilters();
        updateSearchClearButton();
    });
    
    elements.filterToggle.addEventListener('click', () => {
        elements.filterPanel.classList.toggle('active');
        elements.filterToggle.classList.toggle('active');
        
        if (elements.activeFiltersContainer) {
            elements.activeFiltersContainer.classList.toggle('active');
        }
    });
    
    elements.filterBubbles.forEach(bubble => {
        bubble.addEventListener('click', () => {
            const filterType = bubble.dataset.filter;
            
            if (bubble.classList.contains('disabled')) {
                return;
            }
            
            openFilterPopup(filterType);
        });
    });
    
    elements.filterPopupClose.addEventListener('click', closeFilterPopup);
    elements.filterPopupOverlay.addEventListener('click', (e) => {
        if (e.target === elements.filterPopupOverlay) {
            closeFilterPopup();
        }
    });
    
    if (elements.selectAllBtn) {
        elements.selectAllBtn.addEventListener('click', () => {
            if (currentPopupFilter) {
                handleSelectAll(currentPopupFilter);
            }
        });
    }
    
    if (elements.clearAllBtn) {
        elements.clearAllBtn.addEventListener('click', () => {
            if (currentPopupFilter) {
                handleClearAll(currentPopupFilter);
            }
        });
    }
    
    elements.popupSearchInput.addEventListener('input', () => {
        if (currentPopupFilter) {
            renderPopupContent(currentPopupFilter, elements.popupSearchInput.value);
        }
    });
    
    if (elements.clearAllFiltersBtn) {
        elements.clearAllFiltersBtn.addEventListener('click', clearAllFilters);
    }
    
    if (elements.applyFiltersBtn) {
        elements.applyFiltersBtn.addEventListener('click', () => {
            filterAndSortGifts();
            renderActiveFilters();
            closeFilterPopup();
        });
    }
    
    if (elements.viewActiveFiltersBtn) {
        elements.viewActiveFiltersBtn.addEventListener('click', openActiveFiltersPopup);
    }
    
    if (elements.shareFilterBtn) {
        elements.shareFilterBtn.addEventListener('click', shareCurrentFilters);
    }
    
    if (elements.sheetCloseBtn) {
        elements.sheetCloseBtn.addEventListener('click', closeBottomSheet);
    }
    
    if (elements.bottomSheetOverlay) {
        elements.bottomSheetOverlay.addEventListener('click', (e) => {
            if (e.target === elements.bottomSheetOverlay) {
                closeBottomSheet();
            }
        });
    }
    
    if (elements.sheetHandle) {
        setupSheetDragEvents();
    }
    
    elements.scrollTopBtn.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
    
    if (elements.activeFiltersPopupClose) {
        elements.activeFiltersPopupClose.addEventListener('click', closeActiveFiltersPopup);
    }
    if (elements.activeFiltersPopupOverlay) {
        elements.activeFiltersPopupOverlay.addEventListener('click', (e) => {
            if (e.target === elements.activeFiltersPopupOverlay) {
                closeActiveFiltersPopup();
            }
        });
    }
}

// ===== FUNGSI BOTTOM SHEET DRAG =====
function setupSheetDragEvents() {
    if (!elements.sheetHandle || !elements.bottomSheet) return;
    
    let startY = 0;
    let currentY = 0;
    let isDragging = false;
    const threshold = 80;
    
    const onTouchStart = (e) => {
        e.preventDefault();
        startY = e.touches[0].clientY;
        isDragging = true;
        elements.bottomSheet.style.transition = 'none';
    };
    
    const onTouchMove = (e) => {
        if (!isDragging) return;
        e.preventDefault();
        
        currentY = e.touches[0].clientY;
        const deltaY = currentY - startY;
        
        if (deltaY > 0) {
            elements.bottomSheet.style.transform = `translateY(${deltaY}px)`;
        }
    };
    
    const onTouchEnd = (e) => {
        if (!isDragging) return;
        e.preventDefault();
        
        isDragging = false;
        elements.bottomSheet.style.transition = 'transform 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
        
        const deltaY = currentY - startY;
        if (deltaY > threshold) {
            closeBottomSheet();
        } else {
            elements.bottomSheet.style.transform = 'translateY(0)';
        }
    };
    
    elements.sheetHandle.addEventListener('touchstart', onTouchStart);
    elements.sheetHandle.addEventListener('touchmove', onTouchMove);
    elements.sheetHandle.addEventListener('touchend', onTouchEnd);
}

// ===== FUNGSI FILTER =====
function handleSelectAll(filterType) {
    switch(filterType) {
        case 'gift':
            activeFilters.gift = [...filterOptions.gifts];
            renderPopupContent('gift', elements.popupSearchInput.value);
            break;
        case 'model':
            if (activeFilters.gift.length > 0) {
                const selectedGiftNames = activeFilters.gift;
                const relevantGifts = gifts.filter(gift => {
                    const giftName = gift.nama || gift.name.split('#')[0].trim();
                    return selectedGiftNames.includes(giftName);
                });
                const modelSet = new Set(relevantGifts.map(g => g.model));
                activeFilters.model = Array.from(modelSet);
            }
            renderPopupContent('model', elements.popupSearchInput.value);
            break;
        case 'symbol':
            if (activeFilters.gift.length > 0) {
                const selectedGiftNames = activeFilters.gift;
                const relevantGifts = gifts.filter(gift => {
                    const giftName = gift.nama || gift.name.split('#')[0].trim();
                    return selectedGiftNames.includes(giftName);
                });
                const symbolSet = new Set(relevantGifts.map(g => g.symbol));
                activeFilters.symbol = Array.from(symbolSet);
            }
            renderPopupContent('symbol', elements.popupSearchInput.value);
            break;
        case 'bg':
            if (activeFilters.gift.length > 0) {
                const selectedGiftNames = activeFilters.gift;
                const relevantGifts = gifts.filter(gift => {
                    const giftName = gift.nama || gift.name.split('#')[0].trim();
                    return selectedGiftNames.includes(giftName);
                });
                const bgSet = new Set(relevantGifts.map(g => g.bg));
                activeFilters.bg = Array.from(bgSet);
            }
            renderPopupContent('bg', elements.popupSearchInput.value);
            break;
    }
    updateFilterCounts();
    updateDependentBubbles();
}

function handleClearAll(filterType) {
    switch(filterType) {
        case 'gift':
            activeFilters.gift = [];
            activeFilters.model = [];
            activeFilters.symbol = [];
            activeFilters.bg = [];
            renderPopupContent('gift', elements.popupSearchInput.value);
            break;
        case 'model':
            activeFilters.model = [];
            renderPopupContent('model', elements.popupSearchInput.value);
            break;
        case 'symbol':
            activeFilters.symbol = [];
            renderPopupContent('symbol', elements.popupSearchInput.value);
            break;
        case 'bg':
            activeFilters.bg = [];
            renderPopupContent('bg', elements.popupSearchInput.value);
            break;
    }
    updateFilterCounts();
    updateDependentBubbles();
}

function openActiveFiltersPopup() {
    renderActiveFiltersPopup();
    elements.activeFiltersPopupOverlay.classList.add('active');
    setTimeout(() => elements.activeFiltersPopup.classList.add('active'), 10);
    document.dispatchEvent(new Event('popupOpened'));
}

function closeActiveFiltersPopup() {
    elements.activeFiltersPopup.classList.remove('active');
    setTimeout(() => {
        elements.activeFiltersPopupOverlay.classList.remove('active');
        document.dispatchEvent(new Event('popupClosed'));
    }, 300);
}

function renderActiveFiltersPopup() {
    let html = '';
    
    if (activeFilters.id) {
        html += `
            <div class="popup-filter-group">
                <div class="popup-filter-group-title">ID Search</div>
                <div class="popup-filter-items">
                    <span class="popup-filter-item-tag">${activeFilters.id}</span>
                </div>
            </div>
        `;
    }
    
    if (activeFilters.gift.length > 0) {
        html += `
            <div class="popup-filter-group">
                <div class="popup-filter-group-title">Gift Names</div>
                <div class="popup-filter-items">
                    ${activeFilters.gift.map(gift => `<span class="popup-filter-item-tag">${gift}</span>`).join('')}
                </div>
            </div>
        `;
    }
    
    if (activeFilters.model.length > 0) {
        html += `
            <div class="popup-filter-group">
                <div class="popup-filter-group-title">Models</div>
                <div class="popup-filter-items">
                    ${activeFilters.model.map(model => `<span class="popup-filter-item-tag">${model}</span>`).join('')}
                </div>
            </div>
        `;
    }
    
    if (activeFilters.symbol.length > 0) {
        html += `
            <div class="popup-filter-group">
                <div class="popup-filter-group-title">Symbols</div>
                <div class="popup-filter-items">
                    ${activeFilters.symbol.map(symbol => `<span class="popup-filter-item-tag">${symbol}</span>`).join('')}
                </div>
            </div>
        `;
    }
    
    if (activeFilters.bg.length > 0) {
        html += `
            <div class="popup-filter-group">
                <div class="popup-filter-group-title">Backdrops</div>
                <div class="popup-filter-items">
                    ${activeFilters.bg.map(bg => `<span class="popup-filter-item-tag">${bg}</span>`).join('')}
                </div>
            </div>
        `;
    }
    
    if (activeFilters.sort !== 'price-asc') {
        const sortLabels = {
            'price-asc': 'Low to High',
            'price-desc': 'High to Low',
            'id-asc': 'ID Ascending',
            'id-desc': 'ID Descending',
            'latest': 'Latest'
        };
        html += `
            <div class="popup-filter-group">
                <div class="popup-filter-group-title">Sort By</div>
                <div class="popup-filter-items">
                    <span class="popup-filter-item-tag">${sortLabels[activeFilters.sort]}</span>
                </div>
            </div>
        `;
    }
    
    if (html === '') {
        html = '<div class="popup-empty-state">No active filters</div>';
    }
    
    elements.activeFiltersPopupContent.innerHTML = html;
}

function openFilterPopup(filterType) {
    currentPopupFilter = filterType;
    
    const titles = {
        'gift': 'Select Gift Name',
        'model': 'Select Model',
        'symbol': 'Select Symbol',
        'bg': 'Select Backdrop',
        'sort': 'Sort By'
    };
    elements.filterPopupTitle.textContent = titles[filterType] || 'Select';
    
    if (filterType === 'sort') {
        elements.selectAllBtn.style.display = 'none';
        elements.clearAllBtn.style.display = 'none';
    } else {
        elements.selectAllBtn.style.display = 'inline-block';
        elements.clearAllBtn.style.display = 'inline-block';
    }
    
    elements.popupSearchInput.value = '';
    
    renderPopupContent(filterType, '');
    
    elements.filterPopupOverlay.classList.add('active');
    setTimeout(() => elements.filterPopup.classList.add('active'), 10);
    document.dispatchEvent(new Event('popupOpened'));
}

function closeFilterPopup() {
    elements.filterPopup.classList.remove('active');
    setTimeout(() => {
        elements.filterPopupOverlay.classList.remove('active');
        currentPopupFilter = null;
        document.dispatchEvent(new Event('popupClosed'));
    }, 300);
}

function renderPopupContent(filterType, searchTerm = '') {
    if (!elements.filterPopupList) return;
    
    switch(filterType) {
        case 'gift':
            renderGiftPopup(searchTerm);
            break;
        case 'model':
            renderModelPopup(searchTerm);
            break;
        case 'symbol':
            renderSymbolPopup(searchTerm);
            break;
        case 'bg':
            renderBgPopup(searchTerm);
            break;
        case 'sort':
            renderSortPopup();
            break;
    }
}

function formatGiftNameForFile(giftName) {
    return giftName;
}

function renderGiftPopup(searchTerm = '') {
    const filteredGifts = filterOptions.gifts.filter(gift =>
        gift.toLowerCase().includes(searchTerm.toLowerCase())
    );

    if (filteredGifts.length === 0) {
        elements.filterPopupList.innerHTML = '<div class="popup-empty-state">No gifts found</div>';
        return;
    }

    elements.filterPopupList.innerHTML = filteredGifts.map(gift => {
        const isChecked = activeFilters.gift.includes(gift);
        const fileName = formatGiftNameForFile(gift);
        const imageUrl = `https://aldiprem.github.io/WINEDASH-GALERY/images/gifts/${fileName}.png`;

        return `
            <div class="popup-filter-item">
                <label class="popup-checkbox-container">
                    <input type="checkbox" value="${gift}" ${isChecked ? 'checked' : ''} onchange="toggleGiftFilter('${gift}', this.checked)">
                    <span class="popup-checkmark"></span>
                    <img src="${imageUrl}" alt="${gift}" class="gift-icon" onerror="this.style.display='none'; console.log('Gambar tidak ditemukan:', '${imageUrl}')">
                    <span class="popup-filter-item-label">${gift}</span>
                </label>
            </div>
        `;
    }).join('');
}

function renderModelPopup(searchTerm = '') {
    let availableModels = [];
    
    if (activeFilters.gift.length > 0) {
        const selectedGiftNames = activeFilters.gift;
        const relevantGifts = gifts.filter(gift => {
            const giftName = gift.nama || gift.name.split('#')[0].trim();
            return selectedGiftNames.includes(giftName);
        });
        
        const modelSet = new Set(relevantGifts.map(g => g.model));
        availableModels = Array.from(modelSet).sort();
    } else {
        elements.filterPopupList.innerHTML = '<div class="popup-empty-state">Please select at least one Gift Name first</div>';
        return;
    }
    
    const filteredModels = availableModels.filter(model => 
        model.toLowerCase().includes(searchTerm.toLowerCase())
    );
    
    if (filteredModels.length === 0) {
        elements.filterPopupList.innerHTML = '<div class="popup-empty-state">No models found</div>';
        return;
    }
    
    elements.filterPopupList.innerHTML = filteredModels.map(model => {
        const isChecked = activeFilters.model.includes(model);
        return `
            <div class="popup-filter-item">
                <label class="popup-checkbox-container">
                    <input type="checkbox" value="${model}" ${isChecked ? 'checked' : ''} onchange="toggleModelFilter('${model}', this.checked)">
                    <span class="popup-checkmark"></span>
                    <span class="popup-filter-item-label">${model}</span>
                </label>
            </div>
        `;
    }).join('');
}

function renderSymbolPopup(searchTerm = '') {
    let availableSymbols = [];
    
    if (activeFilters.gift.length > 0) {
        const selectedGiftNames = activeFilters.gift;
        const relevantGifts = gifts.filter(gift => {
            const giftName = gift.nama || gift.name.split('#')[0].trim();
            return selectedGiftNames.includes(giftName);
        });
        
        const symbolSet = new Set(relevantGifts.map(g => g.symbol));
        availableSymbols = Array.from(symbolSet).sort();
    } else {
        elements.filterPopupList.innerHTML = '<div class="popup-empty-state">Please select at least one Gift Name first</div>';
        return;
    }
    
    const filteredSymbols = availableSymbols.filter(symbol => 
        symbol.toLowerCase().includes(searchTerm.toLowerCase())
    );
    
    if (filteredSymbols.length === 0) {
        elements.filterPopupList.innerHTML = '<div class="popup-empty-state">No symbols found</div>';
        return;
    }
    
    elements.filterPopupList.innerHTML = filteredSymbols.map(symbol => {
        const isChecked = activeFilters.symbol.includes(symbol);
        return `
            <div class="popup-filter-item">
                <label class="popup-checkbox-container">
                    <input type="checkbox" value="${symbol}" ${isChecked ? 'checked' : ''} onchange="toggleSymbolFilter('${symbol}', this.checked)">
                    <span class="popup-checkmark"></span>
                    <span class="popup-filter-item-label">${symbol}</span>
                </label>
            </div>
        `;
    }).join('');
}

function renderBgPopup(searchTerm = '') {
    let availableBgs = [];
    
    if (activeFilters.gift.length > 0) {
        const selectedGiftNames = activeFilters.gift;
        const relevantGifts = gifts.filter(gift => {
            const giftName = gift.nama || gift.name.split('#')[0].trim();
            return selectedGiftNames.includes(giftName);
        });
        
        const bgSet = new Set(relevantGifts.map(g => g.bg));
        availableBgs = Array.from(bgSet).sort();
    } else {
        elements.filterPopupList.innerHTML = '<div class="popup-empty-state">Please select at least one Gift Name first</div>';
        return;
    }
    
    const filteredBgs = availableBgs.filter(bg => 
        bg.toLowerCase().includes(searchTerm.toLowerCase())
    );
    
    if (filteredBgs.length === 0) {
        elements.filterPopupList.innerHTML = '<div class="popup-empty-state">No backdrops found</div>';
        return;
    }
    
    elements.filterPopupList.innerHTML = filteredBgs.map(bg => {
        const isChecked = activeFilters.bg.includes(bg);
        return `
            <div class="popup-filter-item">
                <label class="popup-checkbox-container">
                    <input type="checkbox" value="${bg}" ${isChecked ? 'checked' : ''} onchange="toggleBgFilter('${bg}', this.checked)">
                    <span class="popup-checkmark"></span>
                    <span class="popup-filter-item-label">${bg}</span>
                </label>
            </div>
        `;
    }).join('');
}

function renderSortPopup() {
    const sortOptions = [
        { value: 'price-asc', label: 'Low to High' },
        { value: 'price-desc', label: 'High to Low' },
        { value: 'id-asc', label: 'ID Ascending' },
        { value: 'id-desc', label: 'ID Descending' },
        { value: 'latest', label: 'Latest' }
    ];
    
    elements.filterPopupList.innerHTML = sortOptions.map(option => {
        const isChecked = activeFilters.sort === option.value;
        return `
            <div class="popup-filter-item">
                <label class="popup-checkbox-container">
                    <input type="radio" name="sort" value="${option.value}" ${isChecked ? 'checked' : ''} onchange="updateSortFilter('${option.value}')">
                    <span class="popup-checkmark"></span>
                    <span class="popup-filter-item-label">${option.label}</span>
                </label>
            </div>
        `;
    }).join('');
    
    const currentSort = sortOptions.find(opt => opt.value === activeFilters.sort);
    if (currentSort) {
        elements.sortValue.textContent = currentSort.label;
    }
}

window.toggleGiftFilter = function(gift, checked) {
    if (checked) {
        if (!activeFilters.gift.includes(gift)) {
            activeFilters.gift.push(gift);
        }
    } else {
        activeFilters.gift = activeFilters.gift.filter(g => g !== gift);
        
        if (activeFilters.gift.length === 0) {
            activeFilters.model = [];
            activeFilters.symbol = [];
            activeFilters.bg = [];
        }
    }
    
    updateDependentBubbles();
    updateFilterCounts();
    renderActiveFilters();
    
    if (currentPopupFilter === 'gift') {
        renderPopupContent('gift', elements.popupSearchInput.value);
    }
};

window.toggleModelFilter = function(model, checked) {
    if (checked) {
        if (!activeFilters.model.includes(model)) {
            activeFilters.model.push(model);
        }
    } else {
        activeFilters.model = activeFilters.model.filter(m => m !== model);
    }
    updateFilterCounts();
    renderActiveFilters();
    
    if (currentPopupFilter === 'model') {
        renderPopupContent('model', elements.popupSearchInput.value);
    }
};

window.toggleSymbolFilter = function(symbol, checked) {
    if (checked) {
        if (!activeFilters.symbol.includes(symbol)) {
            activeFilters.symbol.push(symbol);
        }
    } else {
        activeFilters.symbol = activeFilters.symbol.filter(s => s !== symbol);
    }
    updateFilterCounts();
    renderActiveFilters();
    
    if (currentPopupFilter === 'symbol') {
        renderPopupContent('symbol', elements.popupSearchInput.value);
    }
};

window.toggleBgFilter = function(bg, checked) {
    if (checked) {
        if (!activeFilters.bg.includes(bg)) {
            activeFilters.bg.push(bg);
        }
    } else {
        activeFilters.bg = activeFilters.bg.filter(b => b !== bg);
    }
    updateFilterCounts();
    renderActiveFilters();
    
    if (currentPopupFilter === 'bg') {
        renderPopupContent('bg', elements.popupSearchInput.value);
    }
};

window.updateSortFilter = function(value) {
    activeFilters.sort = value;
    
    const sortLabels = {
        'price-asc': 'Low to High',
        'price-desc': 'High to Low',
        'id-asc': 'ID Ascending',
        'id-desc': 'ID Descending',
        'latest': 'Latest'
    };
    elements.sortValue.textContent = sortLabels[value];
    
    closeFilterPopup();
    filterAndSortGifts();
    renderActiveFilters();
};

function updateDependentBubbles() {
    const hasGiftSelected = activeFilters.gift.length > 0;
    
    if (hasGiftSelected) {
        elements.modelBubble.classList.remove('disabled');
        elements.symbolBubble.classList.remove('disabled');
        elements.bgBubble.classList.remove('disabled');
    } else {
        elements.modelBubble.classList.add('disabled');
        elements.symbolBubble.classList.add('disabled');
        elements.bgBubble.classList.add('disabled');
        
        activeFilters.model = [];
        activeFilters.symbol = [];
        activeFilters.bg = [];
    }
}

function updateFilterCounts() {
    elements.giftCount.textContent = activeFilters.gift.length || '0';
    elements.modelCount.textContent = activeFilters.model.length || '0';
    elements.symbolCount.textContent = activeFilters.symbol.length || '0';
    elements.bgCount.textContent = activeFilters.bg.length || '0';
}

function renderActiveFilters() {
    let html = '';
    
    if (activeFilters.id) {
        html += `
            <div class="filter-tag">
                <span class="filter-tag-category">ID:</span>
                <span class="filter-tag-value">${activeFilters.id}</span>
                <span class="filter-tag-remove" onclick="removeIdFilter()">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path d="M18 6L6 18M6 6L18 18" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                </span>
            </div>
        `;
    }
    
    activeFilters.gift.forEach(gift => {
        html += `
            <div class="filter-tag">
                <span class="filter-tag-category">Gift:</span>
                <span class="filter-tag-value">${gift}</span>
                <span class="filter-tag-remove" onclick="removeGiftFilter('${gift}')">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path d="M18 6L6 18M6 6L18 18" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                </span>
            </div>
        `;
    });
    
    activeFilters.model.forEach(model => {
        html += `
            <div class="filter-tag">
                <span class="filter-tag-category">Model:</span>
                <span class="filter-tag-value">${model}</span>
                <span class="filter-tag-remove" onclick="removeModelFilter('${model}')">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path d="M18 6L6 18M6 6L18 18" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                </span>
            </div>
        `;
    });
    
    activeFilters.symbol.forEach(symbol => {
        html += `
            <div class="filter-tag">
                <span class="filter-tag-category">Symbol:</span>
                <span class="filter-tag-value">${symbol}</span>
                <span class="filter-tag-remove" onclick="removeSymbolFilter('${symbol}')">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path d="M18 6L6 18M6 6L18 18" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                </span>
            </div>
        `;
    });
    
    activeFilters.bg.forEach(bg => {
        html += `
            <div class="filter-tag">
                <span class="filter-tag-category">Backdrop:</span>
                <span class="filter-tag-value">${bg}</span>
                <span class="filter-tag-remove" onclick="removeBgFilter('${bg}')">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path d="M18 6L6 18M6 6L18 18" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                </span>
            </div>
        `;
    });
    
    if (activeFilters.sort !== 'price-asc') {
        const sortLabels = {
            'price-asc': 'Low to High',
            'price-desc': 'High to Low',
            'id-asc': 'ID Ascending',
            'id-desc': 'ID Descending',
            'latest': 'Latest'
        };
        html += `
            <div class="filter-tag">
                <span class="filter-tag-category">Sort:</span>
                <span class="filter-tag-value">${sortLabels[activeFilters.sort]}</span>
                <span class="filter-tag-remove" onclick="resetSortFilter()">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path d="M18 6L6 18M6 6L18 18" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                </span>
            </div>
        `;
    }
    
    if (html === '') {
        elements.activeFilters.innerHTML = '<span style="color: var(--tg-text-hint); font-size: 0.75rem;">No active filters</span>';
    } else {
        elements.activeFilters.innerHTML = html;
    }
    
    updateShareButtonVisibility();
}

function updateShareButtonVisibility() {
    const hasActiveFilters = 
        activeFilters.id !== '' || 
        activeFilters.gift.length > 0 || 
        activeFilters.model.length > 0 || 
        activeFilters.symbol.length > 0 || 
        activeFilters.bg.length > 0 || 
        activeFilters.sort !== 'price-asc';
    
    if (elements.clearAllFiltersBtn && elements.applyFiltersBtn && 
        elements.viewActiveFiltersBtn && elements.shareFilterBtn) {
        
        if (hasActiveFilters) {
            elements.clearAllFiltersBtn.style.display = 'flex';
            elements.applyFiltersBtn.style.display = 'flex';
            elements.shareFilterBtn.style.display = 'flex';
            elements.viewActiveFiltersBtn.style.display = 'flex';
        } else {
            elements.clearAllFiltersBtn.style.display = 'none';
            elements.applyFiltersBtn.style.display = 'none';
            elements.shareFilterBtn.style.display = 'none';
            elements.viewActiveFiltersBtn.style.display = 'flex';
        }
    }
}

window.removeIdFilter = function() {
    elements.idSearchInput.value = '';
    activeFilters.id = '';
    filterAndSortGifts();
    renderActiveFilters();
    updateSearchClearButton();
};

window.removeGiftFilter = function(gift) {
    activeFilters.gift = activeFilters.gift.filter(g => g !== gift);
    
    if (activeFilters.gift.length === 0) {
        activeFilters.model = [];
        activeFilters.symbol = [];
        activeFilters.bg = [];
        updateDependentBubbles();
    }
    
    updateFilterCounts();
    renderActiveFilters();
    
    if (currentPopupFilter === 'gift') {
        renderPopupContent('gift', elements.popupSearchInput.value);
    }
};

window.removeModelFilter = function(model) {
    activeFilters.model = activeFilters.model.filter(m => m !== model);
    updateFilterCounts();
    renderActiveFilters();
    
    if (currentPopupFilter === 'model') {
        renderPopupContent('model', elements.popupSearchInput.value);
    }
};

window.removeSymbolFilter = function(symbol) {
    activeFilters.symbol = activeFilters.symbol.filter(s => s !== symbol);
    updateFilterCounts();
    renderActiveFilters();
    
    if (currentPopupFilter === 'symbol') {
        renderPopupContent('symbol', elements.popupSearchInput.value);
    }
};

window.removeBgFilter = function(bg) {
    activeFilters.bg = activeFilters.bg.filter(b => b !== bg);
    updateFilterCounts();
    renderActiveFilters();
    
    if (currentPopupFilter === 'bg') {
        renderPopupContent('bg', elements.popupSearchInput.value);
    }
};

window.resetSortFilter = function() {
    activeFilters.sort = 'price-asc';
    elements.sortValue.textContent = 'Low to High';
    renderActiveFilters();
    filterAndSortGifts();
};

function clearAllFilters() {
    elements.idSearchInput.value = '';
    activeFilters.id = '';
    
    activeFilters.gift = [];
    activeFilters.model = [];
    activeFilters.symbol = [];
    activeFilters.bg = [];
    
    activeFilters.sort = 'price-asc';
    elements.sortValue.textContent = 'Low to High';
    
    updateDependentBubbles();
    updateFilterCounts();
    renderActiveFilters();
    updateSearchClearButton();
    
    filterAndSortGifts();
}

function filterAndSortGifts() {
    if (currentPage !== 'store') return;
    
    filteredGifts = gifts.filter(gift => {
        const giftName = gift.nama || gift.name.split('#')[0].trim();

        if (activeFilters.id && !gift.id.includes(activeFilters.id)) {
            return false;
        }

        if (activeFilters.gift.length > 0 && !activeFilters.gift.includes(giftName)) {
            return false;
        }

        if (activeFilters.model.length > 0 && !activeFilters.model.includes(gift.model)) {
            return false;
        }

        if (activeFilters.symbol.length > 0 && !activeFilters.symbol.includes(gift.symbol)) {
            return false;
        }

        if (activeFilters.bg.length > 0 && !activeFilters.bg.includes(gift.bg)) {
            return false;
        }

        return true;
    });

    switch (activeFilters.sort) {
        case 'price-asc':
            filteredGifts.sort((a, b) => a.price - b.price);
            break;
        case 'price-desc':
            filteredGifts.sort((a, b) => b.price - a.price);
            break;
        case 'id-asc':
            filteredGifts.sort((a, b) => parseInt(a.id) - parseInt(b.id));
            break;
        case 'id-desc':
            filteredGifts.sort((a, b) => parseInt(b.id) - parseInt(a.id));
            break;
        case 'latest':
            filteredGifts.sort((a, b) => parseInt(b.id) - parseInt(a.id));
            break;
    }

    renderGifts();
    updateStats();
    renderActiveFilters();
}

function renderGifts() {
    if (currentPage !== 'store') return;
    
    const giftsToRender = filteredGifts.length > 0 ? filteredGifts : gifts;
    
    if (giftsToRender.length === 0) {
        elements.cardsGrid.innerHTML = `
            <div class="empty-state">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" style="margin-bottom: 16px; opacity: 0.5;">
                    <circle cx="12" cy="12" r="10" stroke-width="1.5"/>
                    <path d="M12 8V12M12 16H12.01" stroke-width="1.5" stroke-linecap="round"/>
                </svg>
                <h3>No gifts found</h3>
                <p style="margin-top: 8px; color: var(--tg-text-hint);">Try adjusting your filters</p>
            </div>
        `;
        return;
    }
    
    elements.cardsGrid.innerHTML = giftsToRender.map(gift => {
        const cleanName = gift.nama || gift.name.split('#')[0].trim();
        const formattedName = formatGiftName(cleanName);
        const giftId = extractIdFromSlug(gift.slug);
        
        return `
        <div class="gift-card" onclick="openBottomSheet(${JSON.stringify({
            ...gift,
            formattedName,
            giftId
        }).replace(/"/g, '&quot;')})">
            <div class="card-image-wrapper">
                <img class="fallback-image" src="https://nft.fragment.com/gift/${gift.slug}.medium.jpg" alt="${gift.name}" style="display: block; width: 100%; height: 100%; object-fit: cover; position: absolute; top: 0; left: 0;" onerror="this.src='https://via.placeholder.com/400?text=NFT+Gift'">
                <div class="lottie-container" data-slug="${gift.slug}">
                    <div class="lottie-skeleton"></div>
                </div>
                <button class="lottie-play-btn" onclick="toggleLottie(this, '${gift.slug}', event)">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M8 5V19L19 12L8 5Z" fill="currentColor" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
                    </svg>
                </button>
            </div>
            <div class="card-content">
                <div class="card-name-container">
                    <span class="card-slug">${formattedName}</span>
                    <span class="card-id">${giftId}</span>
                </div>
                <div class="card-price">
                    <span class="price-label">Price</span>
                    <span class="price-value">💰 ${formatPrice(gift.price)}</span>
                </div>
            </div>
        </div>
    `}).join('');
    
    if (giftsToRender.length === 1) {
        const card = elements.cardsGrid.querySelector('.gift-card');
        if (card) {
            card.style.gridColumn = '1 / -1';
            card.style.maxWidth = '50%';
            card.style.margin = '0 auto';
        }
    }
}

// ===== FUNGSI OPEN BOTTOM SHEET (UNTUK STORE) =====
window.openBottomSheet = function(gift) {
    const cleanName = gift.formattedName || formatGiftName(gift.nama || gift.name.split('#')[0].trim());
    const formattedPrice = formatPriceRupiah(gift.price);
    const giftId = gift.giftId || extractIdFromSlug(gift.slug);
    
    const modelValue = gift.model || '-';
    const symbolValue = gift.symbol || '-';
    const bgValue = gift.bg || '-';
    
    const postedText = gift.posting || 'Unknown';
    const postedLink = postedText.startsWith('@') 
        ? `https://t.me/${postedText.substring(1)}` 
        : postedText;
    
    const slugId = gift.slug_id || generateSlugId(gift);
    
    const content = `
        <div class="sheet-item-detail">
            <div class="sheet-lottie-wrapper">
                <div class="sheet-lottie-container">
                    <lottie-player
                        src="https://nft.fragment.com/gift/${gift.slug}.lottie.json"
                        background="transparent"
                        speed="1"
                        style="width: 100%; height: 100%;"
                        loop="false"
                        count="1"
                        autoplay>
                    </lottie-player>
                </div>
            </div>
            <div class="sheet-info">
                <div class="sheet-name-container">
                    <span class="sheet-name">${cleanName}</span>
                    <span class="sheet-id">${giftId}</span>
                </div>
                
                <div class="sheet-data-container">
                    <div class="sheet-data-row">
                        <span class="sheet-data-label">Model</span>
                        <span class="sheet-data-value">${modelValue}</span>
                    </div>
                    <div class="sheet-data-row">
                        <span class="sheet-data-label">Symbol</span>
                        <span class="sheet-data-value">${symbolValue}</span>
                    </div>
                    <div class="sheet-data-row">
                        <span class="sheet-data-label">Backdrop</span>
                        <span class="sheet-data-value">${bgValue}</span>
                    </div>
                </div>
                
                <div class="sheet-price-row">
                    <span class="sheet-price-label">Price</span>
                    <span class="sheet-price-value">💰 ${formattedPrice}</span>
                </div>
            </div>
        </div>
        <div class="sheet-actions">
            <a href="https://t.me/marketaldibot?start=beli_${gift.slug}" class="btn btn-buy" target="_blank">BUY NOW</a>
            <div class="sheet-middle-buttons">
                <a href="https://t.me/nft/${gift.slug}" class="btn btn-telegram-circle" target="_blank" title="Open in Telegram">
                    <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.64 6.8c-.15 1.58-.8 5.42-1.13 7.19-.14.75-.42 1-.68 1.03-.58.05-1.02-.38-1.58-.75-.88-.58-1.38-.94-2.23-1.5-.99-.65-.35-1.01.22-1.59.15-.15 2.71-2.48 2.76-2.69.01-.03.01-.14-.07-.2-.08-.06-.19-.04-.27-.02-.12.02-1.95 1.24-5.5 3.64-.52.36-1 .53-1.42.52-.47-.01-1.37-.26-2.03-.48-.82-.27-1.47-.42-1.42-.88.03-.24.36-.48.99-.74 3.84-1.67 6.4-2.78 7.68-3.32 3.66-1.56 4.42-1.83 4.92-1.84.11 0 .36.03.52.16.14.12.18.28.2.4-.02.12 0 .38 0 .38z"/>
                    </svg>
                </a>
                <button class="btn btn-gift-share" onclick="shareGift('${slugId}', event)" title="Share this gift">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <rect x="3" y="8" width="18" height="12" rx="2" stroke="currentColor" stroke-width="1.5" fill="none"/>
                        <path d="M7 8V6C7 4.89543 7.89543 4 9 4H15C16.1046 4 17 4.89543 17 6V8" stroke="currentColor" stroke-width="1.5"/>
                        <path d="M12 12V16M12 16L14 14M12 16L10 14" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                        <circle cx="12" cy="12" r="1" fill="currentColor"/>
                    </svg>
                </button>
            </div>
            <a href="https://t.me/marketaldibot?start=nego_${gift.slug}" class="btn btn-nego" target="_blank">MAKE OFFER</a>
        </div>
        <div class="sheet-posted">
            <a href="${postedLink}" class="sheet-posted-link" target="_blank" rel="noopener noreferrer">
                Posted via ${postedText}
            </a>
        </div>
    `;
    
    elements.sheetContent.innerHTML = content;
    
    document.body.classList.add('sheet-open');
    elements.bottomSheetOverlay.classList.add('active');
    setTimeout(() => elements.bottomSheet.classList.add('active'), 10);
    document.dispatchEvent(new Event('popupOpened'));
};

// ===== FUNGSI SHARE GIFT =====
function generateGiftShareLink(slugId) {
    const baseUrl = 'https://t.me/marketaldibot/gifts';
    return `${baseUrl}?startapp=gifts_${slugId}`;
}

window.shareGift = function(slugId, event) {
    if (event) {
        event.stopPropagation();
    }
    
    const shareLink = generateGiftShareLink(slugId);
    copyToClipboard(shareLink);
};

// ===== FUNGSI CLOSE BOTTOM SHEET =====
window.closeBottomSheet = function() {
    elements.bottomSheet.classList.remove('active');
    setTimeout(() => {
        elements.bottomSheetOverlay.classList.remove('active');
        document.body.classList.remove('sheet-open');
        document.dispatchEvent(new Event('popupClosed'));
    }, 300);
};

function updateStats() {
    const currentGifts = filteredGifts.length > 0 ? filteredGifts : gifts;
    if (elements.totalItems) {
        elements.totalItems.textContent = currentGifts.length;
    }
    
    if (currentGifts.length > 0 && elements.floorPrice) {
        const floor = Math.min(...currentGifts.map(g => g.price));
        elements.floorPrice.textContent = `${formatPriceRupiah(floor)}`;
    } else if (elements.floorPrice) {
        elements.floorPrice.textContent = '0';
    }
}

function setupScrollToTop() {
    window.addEventListener('scroll', () => {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const cards = document.querySelectorAll('.gift-card');
        const cardCount = cards.length;
        
        if (scrollTop > 400 && cardCount >= 2) {
            elements.scrollTopBtn.classList.add('visible');
        } else {
            elements.scrollTopBtn.classList.remove('visible');
        }
    });
}

function showError() {
    elements.loadingState.style.display = 'none';
    elements.cardsGrid.innerHTML = `
        <div class="empty-state" style="grid-column: span 2;">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" style="margin-bottom: 16px; opacity: 0.5;">
                <circle cx="12" cy="12" r="10" stroke-width="1.5"/>
                <path d="M12 8V12M12 16H12.01" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
            <h3>Failed to load gifts</h3>
            <p style="margin-top: 8px; color: var(--tg-text-hint);">Please refresh the page</p>
            <button onclick="location.reload()" style="margin-top: 16px; padding: 12px 24px; background: var(--tg-primary); border: none; border-radius: var(--radius-md); color: white; font-weight: 600; cursor: pointer;">Try Again</button>
        </div>
    `;
}

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && elements.bottomSheetOverlay.classList.contains('active')) {
        closeBottomSheet();
    }
    if (e.key === 'Escape' && elements.filterPopupOverlay.classList.contains('active')) {
        closeFilterPopup();
    }
    if (e.key === 'Escape' && elements.activeFiltersPopupOverlay.classList.contains('active')) {
        closeActiveFiltersPopup();
    }
});

window.addEventListener('load', () => {
    setTimeout(() => {
        document.querySelectorAll('lottie-player').forEach(player => {
            player.setAttribute('loop', 'false');
            player.setAttribute('count', '1');
        });
    }, 500);
});

document.addEventListener('click', (e) => {
    const playButton = e.target.closest('.lottie-play-btn');
    if (playButton) {
        e.stopPropagation();
    }
});

// ===== FUNGSI SHARE FILTER =====
function showToast(message, duration = 2000) {
    const toast = document.getElementById('toastNotification');
    const toastMessage = document.getElementById('toastMessage');
    
    if (!toast) return;
    
    toastMessage.textContent = message;
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, duration);
}

function encodeFiltersToBase64() {
    const filterData = {
        id: activeFilters.id || '',
        gift: activeFilters.gift || [],
        model: activeFilters.model || [],
        symbol: activeFilters.symbol || [],
        bg: activeFilters.bg || [],
        sort: activeFilters.sort || 'price-asc'
    };
    
    const jsonString = JSON.stringify(filterData);
    return btoa(unescape(encodeURIComponent(jsonString)));
}

function decodeFiltersFromBase64(encodedString) {
    try {
        const jsonString = decodeURIComponent(escape(atob(encodedString)));
        const filterData = JSON.parse(jsonString);
        
        return {
            id: filterData.id || '',
            gift: Array.isArray(filterData.gift) ? filterData.gift : [],
            model: Array.isArray(filterData.model) ? filterData.model : [],
            symbol: Array.isArray(filterData.symbol) ? filterData.symbol : [],
            bg: Array.isArray(filterData.bg) ? filterData.bg : [],
            sort: filterData.sort || 'price-asc'
        };
    } catch (error) {
        console.error('Error decoding filters:', error);
        return null;
    }
}

function applyFiltersFromEncoded(encodedString) {
    const decodedFilters = decodeFiltersFromBase64(encodedString);
    if (!decodedFilters) return false;
    
    activeFilters.id = decodedFilters.id;
    activeFilters.gift = decodedFilters.gift;
    activeFilters.model = decodedFilters.model;
    activeFilters.symbol = decodedFilters.symbol;
    activeFilters.bg = decodedFilters.bg;
    activeFilters.sort = decodedFilters.sort;
    
    elements.idSearchInput.value = activeFilters.id;
    
    const sortLabels = {
        'price-asc': 'Low to High',
        'price-desc': 'High to Low',
        'id-asc': 'ID Ascending',
        'id-desc': 'ID Descending',
        'latest': 'Latest'
    };
    elements.sortValue.textContent = sortLabels[activeFilters.sort] || 'Low to High';
    
    updateDependentBubbles();
    updateFilterCounts();
    updateSearchClearButton();
    
    filterAndSortGifts();
    renderActiveFilters();
    
    return true;
}

function generateTelegramShareLink() {
    const baseUrl = 'https://t.me/marketaldibot/gifts';
    const encodedFilters = encodeFiltersToBase64();
    return `${baseUrl}?startapp=${encodedFilters}`;
}

function generateGitHubDirectLink() {
    const baseUrl = window.location.origin + window.location.pathname;
    const encodedFilters = encodeFiltersToBase64();
    return `${baseUrl}?search=${encodedFilters}`;
}

function shareCurrentFilters() {
    const telegramLink = generateTelegramShareLink();
    
    if (tg) {
        tg.showPopup({
            title: 'Share Filters',
            message: 'Share this filtered view with your friends?',
            buttons: [
                { id: 'share', type: 'default', text: 'Share Link' },
                { id: 'copy', type: 'default', text: 'Copy Link' },
                { id: 'cancel', type: 'destructive', text: 'Cancel' }
            ]
        }, (buttonId) => {
            if (buttonId === 'share') {
                if (tg.shareToStory) {
                    tg.shareToStory(telegramLink);
                } else {
                    copyToClipboard(telegramLink);
                }
            } else if (buttonId === 'copy') {
                copyToClipboard(telegramLink);
            }
        });
    } else {
        copyToClipboard(telegramLink);
    }
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Link copied to clipboard!');
    }).catch(err => {
        console.error('Failed to copy:', err);
        prompt('Copy this link:', text);
    });
}

// ===== FUNGSI UNTUK GENERATE SLUG ID =====
function generateSlugId(gift) {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < 20; i++) {
        if (i > 0 && i % 5 === 0) result += '-';
        result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
}

// ===== FUNGSI UNTUK CEK GIFT ID DI URL =====
function checkForGiftIdInUrl() {
    let slugId = null;
    
    const pathParts = window.location.pathname.split('/');
    const giftIndex = pathParts.indexOf('gift');
    if (giftIndex !== -1 && pathParts.length > giftIndex + 1) {
        slugId = pathParts[giftIndex + 1];
        console.log('Found gift slug_id in path:', slugId);
    }
    
    if (tg && tg.initDataUnsafe && tg.initDataUnsafe.startapp) {
        const startapp = tg.initDataUnsafe.startapp;
        if (startapp.startsWith('gifts_')) {
            slugId = startapp.replace('gifts_', '');
            console.log('Found gift slug_id in startapp:', slugId);
        }
    }
    
    if (!slugId) {
        const urlParams = new URLSearchParams(window.location.search);
        slugId = urlParams.get('gift');
        console.log('Found gift slug_id in search param:', slugId);
    }
    
    if (slugId) {
        const gift = gifts.find(g => g.slug_id === slugId);
        if (gift) {
            setTimeout(() => {
                openBottomSheet(gift);
            }, 500);
        } else {
            console.log('Gift with slug_id not found:', slugId);
        }
    }
}

function checkForUrlParameters() {
    let encodedFilters = null;
    
    if (tg && tg.initDataUnsafe && tg.initDataUnsafe.start_param) {
        encodedFilters = tg.initDataUnsafe.start_param;
        console.log('Found Telegram start_param:', encodedFilters);
    }
    
    if (!encodedFilters) {
        const urlParams = new URLSearchParams(window.location.search);
        encodedFilters = urlParams.get('search');
        
        if (encodedFilters) {
            console.log('Found URL search param:', encodedFilters);
        }
    }
    
    if (encodedFilters) {
        const success = applyFiltersFromEncoded(encodedFilters);
        
        if (success) {
            showToast('Filters applied from shared link!');
            
            if (elements.shareFilterBtn) {
                elements.shareFilterBtn.classList.add('pulse');
                setTimeout(() => elements.shareFilterBtn.classList.remove('pulse'), 2000);
            }
        } else {
            showToast('Failed to apply filters', 3000);
        }
    }
}

// ===== EXPORT FUNCTIONS KE GLOBAL =====
window.openFinancePopup = openFinancePopup;
window.closeFinancePopup = closeFinancePopup;
window.openHistoryPopup = openHistoryPopup;
window.closeHistoryPopup = closeHistoryPopup;
window.switchHistoryTab = switchHistoryTab;
window.openWalletPopup = openWalletPopup;
window.closeWalletPopup = closeWalletPopup;
window.openDepositModal = openDepositModal;
window.closeDepositModal = closeDepositModal;
window.setDepositAmount = setDepositAmount;
window.processDeposit = processDeposit;
window.openWithdrawModal = openWithdrawModal;
window.shareCurrentFilters = shareCurrentFilters;
window.copyToClipboard = copyToClipboard;
window.closeBottomSheet = closeBottomSheet;
window.closeFilterPopup = closeFilterPopup;
window.closeActiveFiltersPopup = closeActiveFiltersPopup;
window.toggleGiftFilter = toggleGiftFilter;
window.toggleModelFilter = toggleModelFilter;
window.toggleSymbolFilter = toggleSymbolFilter;
window.toggleBgFilter = toggleBgFilter;
window.updateSortFilter = updateSortFilter;
window.removeIdFilter = removeIdFilter;
window.removeGiftFilter = removeGiftFilter;
window.removeModelFilter = removeModelFilter;
window.removeSymbolFilter = removeSymbolFilter;
window.removeBgFilter = removeBgFilter;
window.resetSortFilter = resetSortFilter;
window.shareGift = shareGift;
window.unlistGift = unlistGift;
window.editPrice = editPrice;
window.showProfilePage = showProfilePage;
window.toggleListingStatus = toggleListingStatus;
window.openUserGiftSheet = openUserGiftSheet;
