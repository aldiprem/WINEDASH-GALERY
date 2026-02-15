// ===== BOTTOM NAVIGATION =====
let currentPage = 'store'; // store, stats, profile
let userGifts = []; // Untuk menyimpan gift user

// DOM Elements untuk navigasi
const navStore = document.getElementById('navStore');
const navStats = document.getElementById('navStats');
const navProfile = document.getElementById('navProfile');

// Event listeners untuk navigasi
navStore.addEventListener('click', () => switchPage('store'));
navStats.addEventListener('click', () => switchPage('stats'));
navProfile.addEventListener('click', () => switchPage('profile'));

function switchPage(page) {
    currentPage = page;
    
    // Update active class
    [navStore, navStats, navProfile].forEach(btn => btn.classList.remove('active'));
    if (page === 'store') navStore.classList.add('active');
    else if (page === 'stats') navStats.classList.add('active');
    else if (page === 'profile') navProfile.classList.add('active');
    
    // Update konten
    if (page === 'store') {
        showStorePage();
    } else if (page === 'stats') {
        showStatsPage();
    } else if (page === 'profile') {
        showProfilePage();
    }
}

function showStorePage() {
    // Tampilkan filter section
    document.querySelector('.filter-section').style.display = 'block';
    // Tampilkan semua gift
    filterAndSortGifts();
}

function showStatsPage() {
    // Sembunyikan filter section
    document.querySelector('.filter-section').style.display = 'none';
    // Tampilkan halaman stats (akan diimplementasikan nanti)
    elements.cardsGrid.innerHTML = `
        <div class="empty-state">
            <h3>Stats Page</h3>
            <p style="margin-top: 8px;">Coming soon...</p>
        </div>
    `;
}

async function showProfilePage() {
    // Sembunyikan filter section
    document.querySelector('.filter-section').style.display = 'none';
    
    if (!telegramUser) {
        elements.cardsGrid.innerHTML = `
            <div class="empty-state">
                <h3>Please login first</h3>
                <p>Open this app from Telegram</p>
            </div>
        `;
        return;
    }
    
    elements.loadingState.style.display = 'flex';
    
    try {
        // Ambil data user dari API
        const API_BASE_URL = 'https://involved-sue-tan-hundreds.trycloudflare.com';
        const response = await fetch(`${API_BASE_URL}/api/users/${telegramUser.id}`);
        
        if (!response.ok) {
            throw new Error('Failed to fetch user data');
        }
        
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error || 'Unknown error');
        }
        
        // Ambil added_gifts (gifts yang ditambahkan user)
        userGifts = data.user.added_gifts || [];
        
        // Filter hanya yang is_listed = 1
        const listedGifts = userGifts.filter(gift => gift.is_listed === 1);
        
        elements.loadingState.style.display = 'none';
        
        if (listedGifts.length === 0) {
            elements.cardsGrid.innerHTML = `
                <div class="empty-state">
                    <h3>No listed gifts</h3>
                    <p style="margin-top: 8px;">You haven't listed any gifts yet</p>
                </div>
            `;
            return;
        }
        
        // Render gifts user
        renderUserGifts(listedGifts);
        
    } catch (error) {
        console.error('Error loading user gifts:', error);
        elements.loadingState.style.display = 'none';
        elements.cardsGrid.innerHTML = `
            <div class="empty-state">
                <h3>Failed to load your gifts</h3>
                <p style="margin-top: 8px;">${error.message}</p>
                <button onclick="showProfilePage()" style="margin-top: 16px;">Try Again</button>
            </div>
        `;
    }
}

function renderUserGifts(gifts) {
    elements.cardsGrid.innerHTML = gifts.map(gift => {
        const cleanName = gift.nama || gift.slug.split('-')[0];
        
        return `
        <div class="gift-card" onclick="openUserGiftSheet(${JSON.stringify(gift).replace(/"/g, '&quot;')})">
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
                    <span class="card-slug">${cleanName}</span>
                    <span class="card-id">${gift.id}</span>
                </div>
                <div class="card-price">
                    <span class="price-label">Price</span>
                    <span class="price-value">💰 ${formatPrice(gift.price)}</span>
                </div>
            </div>
        </div>
    `}).join('');
}

// ===== FUNGSI OPEN BOTTOM SHEET UNTUK GIFT USER =====
window.openUserGiftSheet = function(gift) {
    const cleanName = gift.nama || gift.slug.split('-')[0];
    const formattedPrice = formatPriceRupiah(gift.price);
    
    // Format model, symbol, bg
    const modelValue = gift.model || '-';
    const symbolValue = gift.symbol || '-';
    const bgValue = gift.bg || '-';
    
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
                    <span class="sheet-id">${gift.id}</span>
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
        <div class="sheet-actions" style="grid-template-columns: 1fr 1fr;">
            <button class="btn btn-nego" onclick="unlistGift('${gift.slug}')">UNLISTED</button>
            <button class="btn btn-buy" onclick="editPrice('${gift.slug}')">EDIT PRICE</button>
        </div>
    `;
    
    elements.sheetContent.innerHTML = content;
    
    document.body.classList.add('sheet-open');
    elements.bottomSheetOverlay.classList.add('active');
    setTimeout(() => elements.bottomSheet.classList.add('active'), 10);
    document.dispatchEvent(new Event('popupOpened'));
};

// Fungsi sementara untuk unlist dan edit price
window.unlistGift = function(slug) {
    closeBottomSheet();
    showToast('Unlist feature coming soon!');
    // TODO: Implement unlist API
};

window.editPrice = function(slug) {
    closeBottomSheet();
    showToast('Edit price feature coming soon!');
    // TODO: Implement edit price API
};
