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

// Current active popup
let currentPopupFilter = null;

// Lottie cache
const lottieCache = new Map();

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
    clearAllFilters: document.getElementById('clearAllFilters'),
    applyFiltersBtn: document.getElementById('applyFiltersBtn'),
    activeFilters: document.getElementById('activeFilters'),
    filterPopupOverlay: document.getElementById('filterPopupOverlay'),
    filterPopup: document.getElementById('filterPopup'),
    filterPopupTitle: document.getElementById('filterPopupTitle'),
    filterPopupClose: document.getElementById('filterPopupClose'),
    popupSearchInput: document.getElementById('popupSearchInput'),
    filterPopupList: document.getElementById('filterPopupList'),
    totalItems: document.getElementById('total-items'),
    floorPrice: document.getElementById('floor-price'),
    loadingState: document.getElementById('loadingState'),
    bottomSheetOverlay: document.getElementById('bottomSheetOverlay'),
    bottomSheet: document.getElementById('bottomSheet'),
    sheetContent: document.getElementById('sheetContent'),
    scrollTopBtn: document.getElementById('scrollTopBtn')
};

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    await loadGifts();
    setupEventListeners();
    updateFilterCounts();
    renderGifts();
    setupScrollToTop();
});

// Load JSON data
async function loadGifts() {
    try {
        elements.loadingState.style.display = 'flex';
        const response = await fetch('export/data.json');
        gifts = await response.json();
        
        // Extract unique values for filter options
        const giftSet = new Set();
        const modelSet = new Set();
        const symbolSet = new Set();
        const bgSet = new Set();
        
        gifts.forEach(gift => {
            const giftName = gift.nama || gift.name.split('#')[0].trim();
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
    } catch (error) {
        console.error('Error loading gifts:', error);
        showError();
    }
}

// Get Lottie URL from gift slug
function getLottieUrl(slug) {
    return `https://nft.fragment.com/gift/${slug}.lottie.json`;
}

// Load Lottie animation
async function loadLottieAnimation(lottieContainer, slug) {
    if (!lottieContainer) return;
    
    const lottieUrl = getLottieUrl(slug);
    
    // Check cache first
    if (lottieCache.has(lottieUrl)) {
        const cachedData = lottieCache.get(lottieUrl);
        renderLottiePlayer(lottieContainer, cachedData);
        return;
    }
    
    // Show skeleton loader
    const skeleton = document.createElement('div');
    skeleton.className = 'lottie-skeleton';
    lottieContainer.appendChild(skeleton);
    
    try {
        const response = await fetch(lottieUrl);
        if (!response.ok) throw new Error('Lottie not found');
        
        const lottieData = await response.json();
        lottieCache.set(lottieUrl, lottieData);
        
        // Remove skeleton
        skeleton.remove();
        
        // Render Lottie player
        renderLottiePlayer(lottieContainer, lottieData);
    } catch (error) {
        console.warn(`Failed to load Lottie for ${slug}:`, error);
        skeleton.remove();
        
        // Mark as error and show fallback
        lottieContainer.classList.add('lottie-error');
        
        // Try to load fallback image
        const fallbackImg = lottieContainer.querySelector('.fallback-image');
        if (fallbackImg) {
            fallbackImg.style.display = 'block';
        }
    }
}

// Render Lottie player
function renderLottiePlayer(container, lottieData) {
    // Clear container
    container.innerHTML = '';
    
    // Create Lottie player
    const player = document.createElement('lottie-player');
    player.setAttribute('autoplay', '');
    player.setAttribute('loop', '');
    player.setAttribute('mode', 'normal');
    player.setAttribute('style', 'width: 100%; height: 100%;');
    
    // Stringify the lottie data and set as src
    const lottieJson = JSON.stringify(lottieData);
    player.setAttribute('src', `data:application/json;charset=utf-8,${encodeURIComponent(lottieJson)}`);
    
    container.appendChild(player);
}

// Setup event listeners
function setupEventListeners() {
    // ID Search
    elements.idSearchInput.addEventListener('input', (e) => {
        activeFilters.id = e.target.value;
        // Auto apply for ID search
        filterAndSortGifts();
        renderActiveFilters();
    });
    
    elements.idSearchClear.addEventListener('click', () => {
        elements.idSearchInput.value = '';
        activeFilters.id = '';
        filterAndSortGifts();
        renderActiveFilters();
    });
    
    // Filter toggle (show/hide bubbles)
    elements.filterToggle.addEventListener('click', () => {
        elements.filterPanel.classList.toggle('active');
        elements.filterToggle.classList.toggle('active');
    });
    
    // Filter bubbles click
    elements.filterBubbles.forEach(bubble => {
        bubble.addEventListener('click', () => {
            const filterType = bubble.dataset.filter;
            
            // Check if bubble is disabled
            if (bubble.classList.contains('disabled')) {
                return;
            }
            
            openFilterPopup(filterType);
        });
    });
    
    // Close popup
    elements.filterPopupClose.addEventListener('click', closeFilterPopup);
    elements.filterPopupOverlay.addEventListener('click', (e) => {
        if (e.target === elements.filterPopupOverlay) {
            closeFilterPopup();
        }
    });
    
    // Popup search input
    elements.popupSearchInput.addEventListener('input', () => {
        if (currentPopupFilter) {
            renderPopupContent(currentPopupFilter, elements.popupSearchInput.value);
        }
    });
    
    // Clear all filters
    elements.clearAllFilters.addEventListener('click', clearAllFilters);
    
    // Apply filters button
    elements.applyFiltersBtn.addEventListener('click', () => {
        filterAndSortGifts();
        renderActiveFilters();
        closeFilterPopup();
    });
    
    // Close bottom sheet
    elements.bottomSheetOverlay.addEventListener('click', (e) => {
        if (e.target === elements.bottomSheetOverlay) {
            closeBottomSheet();
        }
    });
    
    // Scroll to top button
    elements.scrollTopBtn.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// Open filter popup
function openFilterPopup(filterType) {
    currentPopupFilter = filterType;
    
    // Set title
    const titles = {
        'gift': 'Select Gift Name',
        'model': 'Select Model',
        'symbol': 'Select Symbol',
        'bg': 'Select Backdrop',
        'sort': 'Sort By'
    };
    elements.filterPopupTitle.textContent = titles[filterType] || 'Select';
    
    // Clear search
    elements.popupSearchInput.value = '';
    
    // Render content
    renderPopupContent(filterType, '');
    
    // Show popup
    elements.filterPopupOverlay.classList.add('active');
    setTimeout(() => elements.filterPopup.classList.add('active'), 10);
}

// Close filter popup
function closeFilterPopup() {
    elements.filterPopup.classList.remove('active');
    setTimeout(() => {
        elements.filterPopupOverlay.classList.remove('active');
        currentPopupFilter = null;
    }, 300);
}

// Render popup content based on filter type
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

// Render Gift popup
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
        return `
            <div class="popup-filter-item">
                <label class="popup-checkbox-container">
                    <input type="checkbox" value="${gift}" ${isChecked ? 'checked' : ''} onchange="toggleGiftFilter('${gift}', this.checked)">
                    <span class="popup-checkmark"></span>
                    <span class="popup-filter-item-label">${gift}</span>
                </label>
            </div>
        `;
    }).join('');
}

// Render Model popup (dependent on selected gifts)
function renderModelPopup(searchTerm = '') {
    // Get models only from selected gifts
    let availableModels = [];
    
    if (activeFilters.gift.length > 0) {
        // Filter gifts based on selected gift names
        const selectedGiftNames = activeFilters.gift;
        const relevantGifts = gifts.filter(gift => {
            const giftName = gift.nama || gift.name.split('#')[0].trim();
            return selectedGiftNames.includes(giftName);
        });
        
        const modelSet = new Set(relevantGifts.map(g => g.model));
        availableModels = Array.from(modelSet).sort();
    } else {
        // If no gift selected, show empty state
        elements.filterPopupList.innerHTML = '<div class="popup-empty-state">Please select at least one Gift Name first</div>';
        return;
    }
    
    // Filter by search term
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

// Render Symbol popup (dependent on selected gifts)
function renderSymbolPopup(searchTerm = '') {
    // Get symbols only from selected gifts
    let availableSymbols = [];
    
    if (activeFilters.gift.length > 0) {
        // Filter gifts based on selected gift names
        const selectedGiftNames = activeFilters.gift;
        const relevantGifts = gifts.filter(gift => {
            const giftName = gift.nama || gift.name.split('#')[0].trim();
            return selectedGiftNames.includes(giftName);
        });
        
        const symbolSet = new Set(relevantGifts.map(g => g.symbol));
        availableSymbols = Array.from(symbolSet).sort();
    } else {
        // If no gift selected, show empty state
        elements.filterPopupList.innerHTML = '<div class="popup-empty-state">Please select at least one Gift Name first</div>';
        return;
    }
    
    // Filter by search term
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

// Render Backdrop popup (dependent on selected gifts)
function renderBgPopup(searchTerm = '') {
    // Get backdrops only from selected gifts
    let availableBgs = [];
    
    if (activeFilters.gift.length > 0) {
        // Filter gifts based on selected gift names
        const selectedGiftNames = activeFilters.gift;
        const relevantGifts = gifts.filter(gift => {
            const giftName = gift.nama || gift.name.split('#')[0].trim();
            return selectedGiftNames.includes(giftName);
        });
        
        const bgSet = new Set(relevantGifts.map(g => g.bg));
        availableBgs = Array.from(bgSet).sort();
    } else {
        // If no gift selected, show empty state
        elements.filterPopupList.innerHTML = '<div class="popup-empty-state">Please select at least one Gift Name first</div>';
        return;
    }
    
    // Filter by search term
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

// Render Sort popup
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
    
    // Update sort value display
    const currentSort = sortOptions.find(opt => opt.value === activeFilters.sort);
    if (currentSort) {
        elements.sortValue.textContent = currentSort.label;
    }
}

// Toggle functions for filters
window.toggleGiftFilter = function(gift, checked) {
    if (checked) {
        if (!activeFilters.gift.includes(gift)) {
            activeFilters.gift.push(gift);
        }
    } else {
        activeFilters.gift = activeFilters.gift.filter(g => g !== gift);
        
        // Clear dependent filters when gift is deselected
        if (activeFilters.gift.length === 0) {
            activeFilters.model = [];
            activeFilters.symbol = [];
            activeFilters.bg = [];
        }
    }
    
    // Enable/disable dependent bubbles
    updateDependentBubbles();
    updateFilterCounts();
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
};

// Update sort filter
window.updateSortFilter = function(value) {
    activeFilters.sort = value;
    
    // Update sort value display
    const sortLabels = {
        'price-asc': 'Low to High',
        'price-desc': 'High to Low',
        'id-asc': 'ID Ascending',
        'id-desc': 'ID Descending',
        'latest': 'Latest'
    };
    elements.sortValue.textContent = sortLabels[value];
};

// Update dependent bubbles (Model, Symbol, Backdrop)
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
        
        // Clear dependent filters when no gift selected
        activeFilters.model = [];
        activeFilters.symbol = [];
        activeFilters.bg = [];
    }
}

// Update filter count badges
function updateFilterCounts() {
    elements.giftCount.textContent = activeFilters.gift.length || '0';
    elements.modelCount.textContent = activeFilters.model.length || '0';
    elements.symbolCount.textContent = activeFilters.symbol.length || '0';
    elements.bgCount.textContent = activeFilters.bg.length || '0';
}

// Render active filters as tags
function renderActiveFilters() {
    let activeFilterCount = 0;
    let html = '';
    
    // ID filter
    if (activeFilters.id) {
        activeFilterCount++;
        html += `
            <div class="filter-tag">
                <span class="filter-tag-category">ID:</span>
                <span class="filter-tag-value">${activeFilters.id}</span>
                <span class="filter-tag-remove" onclick="removeIdFilter()">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path d="M18 6L6 18M6 6L18 18" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                </span>
            </div>
        `;
    }
    
    // Gift filters
    activeFilters.gift.forEach(gift => {
        activeFilterCount++;
        html += `
            <div class="filter-tag">
                <span class="filter-tag-category">Gift:</span>
                <span class="filter-tag-value">${gift}</span>
                <span class="filter-tag-remove" onclick="removeGiftFilter('${gift}')">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path d="M18 6L6 18M6 6L18 18" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                </span>
            </div>
        `;
    });
    
    // Model filters
    activeFilters.model.forEach(model => {
        activeFilterCount++;
        html += `
            <div class="filter-tag">
                <span class="filter-tag-category">Model:</span>
                <span class="filter-tag-value">${model}</span>
                <span class="filter-tag-remove" onclick="removeModelFilter('${model}')">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path d="M18 6L6 18M6 6L18 18" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                </span>
            </div>
        `;
    });
    
    // Symbol filters
    activeFilters.symbol.forEach(symbol => {
        activeFilterCount++;
        html += `
            <div class="filter-tag">
                <span class="filter-tag-category">Symbol:</span>
                <span class="filter-tag-value">${symbol}</span>
                <span class="filter-tag-remove" onclick="removeSymbolFilter('${symbol}')">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path d="M18 6L6 18M6 6L18 18" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                </span>
            </div>
        `;
    });
    
    // Backdrop filters
    activeFilters.bg.forEach(bg => {
        activeFilterCount++;
        html += `
            <div class="filter-tag">
                <span class="filter-tag-category">Backdrop:</span>
                <span class="filter-tag-value">${bg}</span>
                <span class="filter-tag-remove" onclick="removeBgFilter('${bg}')">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path d="M18 6L6 18M6 6L18 18" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                </span>
            </div>
        `;
    });
    
    // Sort filter (always show if not default)
    if (activeFilters.sort !== 'price-asc') {
        const sortLabels = {
            'price-asc': 'Low to High',
            'price-desc': 'High to Low',
            'id-asc': 'ID Ascending',
            'id-desc': 'ID Descending',
            'latest': 'Latest'
        };
        activeFilterCount++;
        html += `
            <div class="filter-tag">
                <span class="filter-tag-category">Sort:</span>
                <span class="filter-tag-value">${sortLabels[activeFilters.sort]}</span>
                <span class="filter-tag-remove" onclick="resetSortFilter()">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path d="M18 6L6 18M6 6L18 18" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                </span>
            </div>
        `;
    }
    
    if (activeFilterCount === 0) {
        elements.activeFilters.innerHTML = '<span style="color: var(--tg-text-hint); font-size: 0.8rem;">No active filters</span>';
    } else {
        elements.activeFilters.innerHTML = html;
    }
}

// Remove filter functions
window.removeIdFilter = function() {
    elements.idSearchInput.value = '';
    activeFilters.id = '';
    filterAndSortGifts();
    renderActiveFilters();
};

window.removeGiftFilter = function(gift) {
    activeFilters.gift = activeFilters.gift.filter(g => g !== gift);
    
    // If no gift selected, clear dependent filters
    if (activeFilters.gift.length === 0) {
        activeFilters.model = [];
        activeFilters.symbol = [];
        activeFilters.bg = [];
        updateDependentBubbles();
    }
    
    updateFilterCounts();
    renderActiveFilters();
    
    // If popup is open, refresh content
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

// Clear all filters
function clearAllFilters() {
    // Clear ID search
    elements.idSearchInput.value = '';
    activeFilters.id = '';
    
    // Clear all arrays
    activeFilters.gift = [];
    activeFilters.model = [];
    activeFilters.symbol = [];
    activeFilters.bg = [];
    
    // Reset sort
    activeFilters.sort = 'price-asc';
    elements.sortValue.textContent = 'Low to High';
    
    // Update UI
    updateDependentBubbles();
    updateFilterCounts();
    renderActiveFilters();
    
    // Apply filters
    filterAndSortGifts();
}

// Filter and sort gifts
function filterAndSortGifts() {
    filteredGifts = gifts.filter(gift => {
        const giftName = gift.nama || gift.name.split('#')[0].trim();
        
        // ID filter
        if (activeFilters.id && !gift.id.includes(activeFilters.id)) {
            return false;
        }
        
        // Gift name filter
        if (activeFilters.gift.length > 0 && !activeFilters.gift.includes(giftName)) {
            return false;
        }
        
        // Model filter
        if (activeFilters.model.length > 0 && !activeFilters.model.includes(gift.model)) {
            return false;
        }
        
        // Symbol filter
        if (activeFilters.symbol.length > 0 && !activeFilters.symbol.includes(gift.symbol)) {
            return false;
        }
        
        // Backdrop filter
        if (activeFilters.bg.length > 0 && !activeFilters.bg.includes(gift.bg)) {
            return false;
        }
        
        return true;
    });
    
    // Apply sorting
    switch(activeFilters.sort) {
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
}

// Render gifts to grid with Lottie animations
function renderGifts() {
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
        
        return `
        <div class="gift-card" onclick="openBottomSheet(${JSON.stringify(gift).replace(/"/g, '&quot;')})">
            <div class="card-image-wrapper">
                <div class="lottie-container" data-slug="${gift.slug}">
                    <img class="fallback-image" src="${gift.image}" alt="${gift.name}" loading="lazy">
                </div>
            </div>
            <div class="card-content">
                <div class="card-name-container">
                    <span class="card-slug">${cleanName}</span>
                    <span class="card-id">#${gift.id}</span>
                </div>
                <div class="card-price">
                    <span class="price-label">Price</span>
                    <span class="price-value">💰 ${formatPrice(gift.price)}</span>
                </div>
            </div>
        </div>
    `}).join('');
    
    // Initialize Lottie animations for each card
    setTimeout(() => {
        document.querySelectorAll('.lottie-container').forEach(container => {
            const slug = container.dataset.slug;
            loadLottieAnimation(container, slug);
        });
    }, 100);
    
    // Fix for single card layout
    if (giftsToRender.length === 1) {
        const card = elements.cardsGrid.querySelector('.gift-card');
        if (card) {
            card.style.gridColumn = '1 / -1';
            card.style.maxWidth = '50%';
            card.style.margin = '0 auto';
        }
    }
}

// Open bottom sheet with gift details
window.openBottomSheet = function(gift) {
    const cleanName = gift.nama || gift.name.split('#')[0].trim();
    
    const content = `
        <div class="sheet-item-detail">
            <div class="sheet-lottie-container">
                <lottie-player
                    src="https://nft.fragment.com/gift/${gift.slug}.lottie.json"
                    background="transparent"
                    speed="1"
                    style="width: 100%; height: 100%;"
                    loop
                    autoplay>
                </lottie-player>
            </div>
            <div class="sheet-info">
                <div class="sheet-name">${cleanName}</div>
                <div style="color: var(--tg-text-hint); font-size: 0.8rem; margin-bottom: 4px;">#${gift.id}</div>
                <div class="sheet-model">${gift.model}</div>
                <div class="sheet-model" style="margin-top: 2px;">${gift.symbol}</div>
                <div class="sheet-model" style="margin-top: 2px;">${gift.bg}</div>
                <div class="sheet-price">💰 ${formatPrice(gift.price)}</div>
            </div>
        </div>
        <div class="sheet-actions">
            <a href="https://t.me/marketaldibot?start=beli_${gift.slug}" class="btn btn-buy" target="_blank">🛍️ BUY NOW</a>
            <a href="https://t.me/marketaldibot?start=nego_${gift.slug}" class="btn btn-nego" target="_blank">💬 MAKE OFFER</a>
        </div>
        <div style="display: flex; justify-content: center; margin-top: 8px;">
            <span style="color: var(--tg-text-hint); font-size: 0.7rem;">Posted via ${gift.posting}</span>
        </div>
    `;
    
    elements.sheetContent.innerHTML = content;
    elements.bottomSheetOverlay.classList.add('active');
    setTimeout(() => elements.bottomSheet.classList.add('active'), 10);
};

// Close bottom sheet
window.closeBottomSheet = function() {
    elements.bottomSheet.classList.remove('active');
    setTimeout(() => {
        elements.bottomSheetOverlay.classList.remove('active');
    }, 300);
};

// Update statistics
function updateStats() {
    const currentGifts = filteredGifts.length > 0 ? filteredGifts : gifts;
    elements.totalItems.textContent = currentGifts.length;
    
    if (currentGifts.length > 0) {
        const floor = Math.min(...currentGifts.map(g => g.price));
        elements.floorPrice.textContent = `${formatPrice(floor)}`;
    } else {
        elements.floorPrice.textContent = '0';
    }
}

// Format price with K/M suffix
function formatPrice(price) {
    if (price >= 1000000) {
        return (price / 1000000).toFixed(1) + 'M';
    }
    if (price >= 1000) {
        return (price / 1000).toFixed(1) + 'K';
    }
    return price.toString();
}

// Setup scroll to top visibility
function setupScrollToTop() {
    window.addEventListener('scroll', () => {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const cards = document.querySelectorAll('.gift-card');
        const cardCount = cards.length;
        
        // Show button after scrolling past 2 rows (approximately 2 cards height)
        if (scrollTop > 400 && cardCount >= 2) {
            elements.scrollTopBtn.classList.add('visible');
        } else {
            elements.scrollTopBtn.classList.remove('visible');
        }
    });
}

// Show error state
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

// Close bottom sheet with ESC key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && elements.bottomSheetOverlay.classList.contains('active')) {
        closeBottomSheet();
    }
    if (e.key === 'Escape' && elements.filterPopupOverlay.classList.contains('active')) {
        closeFilterPopup();
    }
});

// Lazy load Lottie animations when cards are in viewport
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const container = entry.target;
            const slug = container.dataset.slug;
            if (slug && !container.hasAttribute('data-loaded')) {
                loadLottieAnimation(container, slug);
                container.setAttribute('data-loaded', 'true');
            }
        }
    });
}, { threshold: 0.1 });

// Observe new Lottie containers
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        document.querySelectorAll('.lottie-container').forEach(container => {
            observer.observe(container);
        });
    }, 500);
});
