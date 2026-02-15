// ===== FUNGSI UTILITY =====
function formatGiftName(name) {
    return name.replace(/([A-Z])/g, ' $1').trim();
}

function extractIdFromSlug(slug) {
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

function generateSlugId(gift) {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < 20; i++) {
        if (i > 0 && i % 5 === 0) result += '-';
        result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
}

// ===== GLOBAL STATE =====
let tg = null;
let telegramUser = null;
let userBalance = 0;
let userGifts = [];
let lottieCache = new Map();

// DOM Elements
const elements = {
    cardsGrid: document.getElementById('cardsGrid'),
    loadingState: document.getElementById('loadingState'),
    userAvatar: document.getElementById('userAvatar'),
    userBalance: document.getElementById('userBalance'),
    userProfile: document.getElementById('userProfile'),
    profileHeader: document.getElementById('profileHeader'),
    bottomSheetOverlay: document.getElementById('bottomSheetOverlay'),
    bottomSheet: document.getElementById('bottomSheet'),
    sheetContent: document.getElementById('sheetContent'),
    sheetCloseBtn: document.getElementById('sheetCloseBtn'),
    sheetHandle: document.querySelector('.sheet-handle'),
    scrollTopBtn: document.getElementById('scrollTopBtn')
};

// ===== INITIALIZE =====
document.addEventListener('DOMContentLoaded', async () => {
    await initializeTelegramApp();
    await loadProfileData();
    setupEventListeners();
    setupScrollToTop();
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
    closeBottomSheet();
}

// ===== FUNGSI LOAD DATA PROFIL =====
async function loadProfileData() {
    if (!telegramUser) {
        elements.cardsGrid.innerHTML = `
            <div class="empty-state" style="grid-column: 1 / -1;">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" style="margin-bottom: 16px; opacity: 0.5;">
                    <circle cx="12" cy="8" r="4" stroke-width="1.5"/>
                    <path d="M5 20V19C5 15.1 8.1 12 12 12C15.9 12 19 15.1 19 19V20" stroke-width="1.5" stroke-linecap="round"/>
                </svg>
                <h3>Please login first</h3>
                <p>Open this app from Telegram</p>
            </div>
        `;
        return;
    }
    
    elements.loadingState.style.display = 'flex';
    
    try {
        const API_BASE_URL = 'https://involved-sue-tan-hundreds.trycloudflare.com';
        
        // Fetch user data
        const userResponse = await fetch(`${API_BASE_URL}/api/users/${telegramUser.id}`);
        
        if (!userResponse.ok) {
            throw new Error(`HTTP error! status: ${userResponse.status}`);
        }
        
        const userData = await userResponse.json();
        
        if (!userData.success) {
            throw new Error(userData.error || 'Unknown error');
        }
        
        userGifts = userData.user.added_gifts || [];
        
        // Fetch all gifts untuk mendapatkan posting
        const giftsResponse = await fetch(`${API_BASE_URL}/api/gifts?limit=1000`);
        const allMarketGifts = await giftsResponse.json();
        
        const postingMap = {};
        allMarketGifts.forEach(gift => {
            if (gift.slug && gift.posting) {
                postingMap[gift.slug] = gift.posting;
            }
        });
        
        const soldGiftsCount = userGifts.filter(gift => gift.is_sold === 1).length;
        
        const allGifts = userGifts.map(gift => ({
            ...gift,
            price: gift.is_listed === 0 ? 0 : gift.price,
            posting: gift.posting || postingMap[gift.slug] || 'https://t.me/market_wine/57/None'
        }));
        
        elements.loadingState.style.display = 'none';
        renderProfilePage(allGifts, soldGiftsCount);
        
    } catch (error) {
        console.error('Error loading user gifts:', error);
        elements.loadingState.style.display = 'none';
        elements.cardsGrid.innerHTML = `
            <div class="empty-state" style="grid-column: 1 / -1;">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" style="margin-bottom: 16px; opacity: 0.5;">
                    <circle cx="12" cy="12" r="10" stroke-width="1.5"/>
                    <path d="M12 8V12M12 16H12.01" stroke-width="1.5" stroke-linecap="round"/>
                </svg>
                <h3>Failed to load your gifts</h3>
                <p style="margin-top: 8px;">${error.message}</p>
                <button onclick="location.reload()" style="margin-top: 16px; padding: 12px 24px; background: var(--tg-primary); border: none; border-radius: var(--radius-md); color: white; font-weight: 600; cursor: pointer;">Try Again</button>
            </div>
        `;
    }
}

function renderProfilePage(gifts, soldGiftsCount = 0) {
    const firstName = telegramUser.first_name || '';
    const lastName = telegramUser.last_name || '';
    const fullName = `${firstName} ${lastName}`.trim() || 'User';
    const username = telegramUser.username ? `@${telegramUser.username}` : '-';
    const isPremium = telegramUser.is_premium ? '⭐ Premium' : 'Free';
    
    // Clone avatar dari header
    const avatarElement = elements.userAvatar.cloneNode(true);
    
    const profileHeader = `
        <div class="profile-header glass-panel">
            <div class="profile-avatar" id="profilePageAvatar">
                ${avatarElement.innerHTML}
            </div>
            <div class="profile-info">
                <h3 class="profile-name">${fullName}</h3>
                <p class="profile-username">${username}</p>
                <p class="profile-status ${telegramUser.is_premium ? 'premium' : ''}">${isPremium}</p>
                <div class="profile-stats-container" style="display: flex; gap: 16px;">
                    <p class="profile-stats">Listed: ${gifts.filter(g => g.is_listed === 1).length}</p>
                    <p class="profile-stats">Unlisted: ${gifts.filter(g => g.is_listed === 0).length}</p>
                    <p class="profile-stats">Sold: ${soldGiftsCount}</p>
                </div>
            </div>
        </div>
    `;
    
    if (gifts.length === 0) {
        elements.cardsGrid.innerHTML = profileHeader + `
            <div class="empty-state" style="grid-column: 1 / -1;">
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
        
        const modelDisplay = gift.model && gift.model_rarity 
            ? `${gift.model} (${gift.model_rarity})` 
            : (gift.model || '-');
        
        const symbolDisplay = gift.symbol && gift.symbol_rarity 
            ? `${gift.symbol} (${gift.symbol_rarity})` 
            : (gift.symbol || '-');
        
        const bgDisplay = gift.background && gift.background_rarity 
            ? `${gift.background} (${gift.background_rarity})` 
            : (gift.background || '-');
        
        return `
        <div class="gift-card profile-gift-card" onclick="openUserGiftSheet(${JSON.stringify({
            ...gift,
            formattedName,
            modelDisplay,
            symbolDisplay,
            bgDisplay,
            giftId
        }).replace(/"/g, '&quot;')})">
            <div class="card-image-wrapper">
                <img class="fallback-image" src="https://nft.fragment.com/gift/${gift.slug}.medium.jpg" 
                     alt="${gift.name}" 
                     style="display: block; width: 100%; height: 100%; object-fit: cover; position: absolute; top: 0; left: 0;" 
                     onerror="this.src='https://via.placeholder.com/400?text=NFT+Gift'">
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
                    <span class="price-value">💰 ${gift.is_listed === 1 ? formatPrice(gift.price) : 'UNLISTED'}</span>
                </div>
            </div>
        </div>
    `}).join('');
    
    elements.cardsGrid.innerHTML = profileHeader + giftsHtml;
}

// ===== FUNGSI BOTTOM SHEET =====
window.openUserGiftSheet = function(gift) {
    closeBottomSheet();
    
    setTimeout(() => {
        const cleanName = gift.formattedName || formatGiftName(gift.nama || gift.slug.split('-')[0]);
        const formattedPrice = gift.is_listed === 1 ? formatPriceRupiah(gift.price) : 'UNLISTED';
        const giftId = gift.giftId || extractIdFromSlug(gift.slug);
        
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
        const buttonText = gift.is_listed === 1 ? 'UNLISTED' : 'LISTED';
        const postedLink = gift.posting || 'https://t.me/market_wine/57/None';
        
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
    }, 100);
};

window.toggleListingStatus = async function(slug) {
    closeBottomSheet();
    showToast('Updating listing status...', 0);
    
    try {
        const API_BASE_URL = 'https://involved-sue-tan-hundreds.trycloudflare.com';
        
        const response = await fetch(`${API_BASE_URL}/api/gift/toggle-listing`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                slug: slug,
                user_id: telegramUser ? telegramUser.id : null
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast(data.message || 'Status updated! ✅');
            setTimeout(() => loadProfileData(), 1000);
        } else {
            showToast(`Error: ${data.error || 'Failed to update status'}`);
        }
        
    } catch (error) {
        console.error('Error toggling listing status:', error);
        showToast('Failed to update status. Check console for details.');
    }
};

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
            setTimeout(() => loadProfileData(), 1000);
        } else {
            showToast(`Error: ${data.error || 'Failed to update price'}`);
        }

    } catch (error) {
        console.error('Error updating price:', error);
        showToast('Failed to update price. Check console for details.');
    }
};

window.shareGift = function(slugId, event) {
    if (event) event.stopPropagation();
    const shareLink = `https://t.me/marketaldibot/gifts?startapp=gifts_${slugId}`;
    copyToClipboard(shareLink);
};

// ===== FUNGSI LOTTIE =====
function getLottieUrl(slug) {
    return `https://nft.fragment.com/gift/${slug}.lottie.json`;
}

window.toggleLottie = function(button, slug, event) {
    if (event) event.stopPropagation();
    
    const card = button.closest('.gift-card');
    const imageWrapper = card.querySelector('.card-image-wrapper');
    const lottieContainer = imageWrapper.querySelector('.lottie-container');
    const fallbackImage = imageWrapper.querySelector('.fallback-image');
    const skeleton = lottieContainer.querySelector('.lottie-skeleton');
    
    button.classList.toggle('active');
    
    if (button.classList.contains('active')) {
        lottieContainer.classList.add('active');
        if (fallbackImage) fallbackImage.style.display = 'none';
        
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
        if (fallbackImage) fallbackImage.style.display = 'block';
        
        const currentSkeleton = lottieContainer.querySelector('.lottie-skeleton');
        if (currentSkeleton) currentSkeleton.classList.remove('active');
        
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
        if (skeleton) skeleton.classList.remove('active');
        renderLottiePlayer(lottieContainer, cachedData);
        return;
    }
    
    try {
        const response = await fetch(lottieUrl);
        if (!response.ok) throw new Error('Lottie not found');
        
        const lottieData = await response.json();
        lottieCache.set(lottieUrl, lottieData);
        
        if (skeleton) skeleton.classList.remove('active');
        renderLottiePlayer(lottieContainer, lottieData);
    } catch (error) {
        console.warn(`Failed to load Lottie for ${slug}:`, error);
        
        if (skeleton) skeleton.classList.remove('active');
        if (button) button.classList.remove('active');
        
        lottieContainer.classList.remove('active');
        const imageWrapper = lottieContainer.closest('.card-image-wrapper');
        if (imageWrapper) {
            const fallbackImg = imageWrapper.querySelector('.fallback-image');
            if (fallbackImg) fallbackImg.style.display = 'block';
        }
        if (button) button.style.opacity = '0.5';
    }
}

function renderLottiePlayer(container, lottieData) {
    const skeleton = container.querySelector('.lottie-skeleton');
    container.innerHTML = '';
    if (skeleton) container.appendChild(skeleton);
    
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
        if (skeleton) skeleton.classList.remove('active');
    });
}

// ===== FUNGSI UI =====
function setupEventListeners() {
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
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
}

function setupSheetDragEvents() {
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

function setupScrollToTop() {
    window.addEventListener('scroll', () => {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        if (scrollTop > 400) {
            elements.scrollTopBtn.classList.add('visible');
        } else {
            elements.scrollTopBtn.classList.remove('visible');
        }
    });
}

function closeBottomSheet() {
    elements.bottomSheet.classList.remove('active');
    setTimeout(() => {
        elements.bottomSheetOverlay.classList.remove('active');
        document.body.classList.remove('sheet-open');
        document.dispatchEvent(new Event('popupClosed'));
    }, 300);
}

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

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Link copied to clipboard!');
    }).catch(err => {
        console.error('Failed to copy:', err);
        prompt('Copy this link:', text);
    });
}

// Keyboard events
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && elements.bottomSheetOverlay.classList.contains('active')) {
        closeBottomSheet();
    }
});
