// ===== ELEMENT REFERENCES =====
const elements = {
    // Filter inputs
    giftFilter: document.getElementById("giftFilter") || { value: "" },
    modelFilter: document.getElementById("modelFilter") || { value: "" },
    symbolFilter: document.getElementById("symbolFilter") || { value: "" },
    bgFilter: document.getElementById("bgFilter") || { value: "" },
    maxPrice: document.getElementById("maxPrice") || { value: "" },
    
    // Grid
    grid: document.getElementById("giftGrid") || document.createElement("div"),
    
    // Search
    giftSearchInput: document.getElementById("giftSearchInput") || { value: "" },
    giftDropdown: document.getElementById("giftDropdown") || { style: {}, innerHTML: "" },
    giftSelected: document.getElementById("giftSelected") || document.createElement("div"),
    giftSearchBtn: document.getElementById("giftSearchBtn"),
    
    // Detail Panel
    panel: document.getElementById("giftDetailPanel") || document.createElement("div"),
    overlay: document.getElementById("panelOverlay") || document.createElement("div"),
    btnBeli: document.getElementById("btnBeli") || document.createElement("a"),
    btnNego: document.getElementById("btnNego") || document.createElement("a"),
    detailImg: document.getElementById("detailImg") || document.createElement("img"),
    detailTitle: document.getElementById("detailTitle") || document.createElement("div"),
    detailModel: document.getElementById("detailModel") || document.createElement("b"),
    detailBg: document.getElementById("detailBg") || document.createElement("b"),
    detailSymbol: document.getElementById("detailSymbol") || document.createElement("b"),
    detailPrice: document.getElementById("detailPrice") || document.createElement("b"),
    
    // Loader & Scroll
    pageLoader: document.getElementById("pageLoader") || document.createElement("div"),
    scrollTopBtn: document.getElementById("scrollTopBtn") || document.createElement("div"),
    
    // Filter Panel
    filterToggleBtn: document.getElementById("filterToggleBtn"),
    filterPanel: document.getElementById("filterPanel"),
    closeFilterPanel: document.getElementById("closeFilterPanel"),
    applyFilterBtn: document.getElementById("applyFilterBtn"),
    cancelFilterBtn: document.getElementById("cancelFilterBtn"),
    
    // Filter Selects
    giftFilterSelect: document.getElementById("giftFilterSelect"),
    modelFilterSelect: document.getElementById("modelFilterSelect"),
    symbolFilterSelect: document.getElementById("symbolFilterSelect"),
    bgFilterSelect: document.getElementById("bgFilterSelect"),
    maxPriceFilter: document.getElementById("maxPriceFilter"),
    
    // Filter Search Inputs
    giftSearchFilter: document.getElementById("giftSearchFilter"),
    modelSearchFilter: document.getElementById("modelSearchFilter"),
    symbolSearchFilter: document.getElementById("symbolSearchFilter"),
    bgSearchFilter: document.getElementById("bgSearchFilter"),
    
    // Bubble Board
    giftBubbleBoard: document.getElementById("giftBubbleBoard"),
    filterOverlay: document.getElementById("filterOverlay"),
    filterBubbleBoard: document.getElementById("filterBubbleBoard"),
    
    // Old Filter Buttons (compatibility)
    btnAllGifts: document.getElementById("btnAllGifts") || document.createElement("button"),
    btnAllModels: document.getElementById("btnAllModels") || document.createElement("button"),
    btnAllSymbols: document.getElementById("btnAllSymbols") || document.createElement("button"),
    btnAllBackdrops: document.getElementById("btnAllBackdrops") || document.createElement("button"),
    btnSort: document.getElementById("btnSort") || document.createElement("button"),
    sortOptions: document.getElementById("sortOptions") || document.createElement("div"),
    subFilters: document.getElementById("subFilters") || document.createElement("div")
};

// ===== STATE MANAGEMENT =====
let state = {
    giftsData: [],
    filteredGifts: [],
    selectedGifts: new Set(),
    selectedGift: null,
    giftList: [],
    sortType: 'default'
};

// ===== UTILITY FUNCTIONS =====

/**
 * Format number to IDR currency
 */
function formatIDR(number) {
    return new Intl.NumberFormat('id-ID', {
        style: 'currency',
        currency: 'IDR',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(number || 0);
}

/**
 * Format NFT name (remove trailing #number)
 */
function formatNFTName(name) {
    if (!name) return "";
    return name.replace(/\s*#\d+$/, "").trim();
}

/**
 * Get preview image URL
 */
function getPreviewImage(nft) {
    if (nft.image && (nft.image.includes("/previews/") || nft.image.includes("http"))) {
        return nft.image;
    }
    if (nft.slug) {
        return `previews/${nft.slug}.jpg`;
    }
    return `previews/${nft.id}.jpg`;
}

// ===== GRID FUNCTIONS =====

/**
 * Render gift grid with 2 cards per row
 */
function renderGrid(data) {
    if (!elements.grid) return;
    
    elements.grid.innerHTML = '';
    
    if (!data || data.length === 0) {
        elements.grid.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">🎁</div>
                <h3>Tidak ada gift ditemukan</h3>
                <p>Coba gunakan filter atau kata kunci lain</p>
                <button onclick="window.showAllGifts()" class="btn btn-primary">
                    Tampilkan Semua
                </button>
            </div>
        `;
        return;
    }
    
    data.forEach(nft => {
        const card = document.createElement('div');
        card.className = 'gift-card';
        card.dataset.id = nft.id;
        card.dataset.name = (nft.name || '').toLowerCase();
        card.dataset.model = nft.model || '';
        card.dataset.symbol = nft.symbol || '';
        card.dataset.bg = nft.bg || nft.background || '';
        card.dataset.price = nft.price || 0;
        
        const giftName = formatNFTName(nft.name);
        const giftId = nft.id;
        const giftPrice = formatIDR(nft.price);
        const previewImage = getPreviewImage(nft);
        
        card.innerHTML = `
            <div class="card-image-container">
                <img 
                    src="${previewImage}" 
                    alt="${giftName}" 
                    class="card-image"
                    loading="lazy"
                    onerror="this.src='https://via.placeholder.com/400x400/6366f1/ffffff?text=No+Preview'"
                >
                <span class="price-bubble">${giftPrice}</span>
            </div>
            <div class="card-content">
                <div class="card-text">
                    <h3 class="gift-name">${giftName}</h3>
                    <p class="gift-id">#${giftId}</p>
                </div>
            </div>
        `;
        
        elements.grid.appendChild(card);
    });
    
    // Store cards reference
    state.cards = Array.from(document.querySelectorAll('.gift-card'));
}

// ===== FILTER FUNCTIONS =====

/**
 * Filter NFT based on all active filters
 */
function filterNFT() {
    const searchText = (elements.giftSearchInput.value || '').toLowerCase().trim();
    const model = elements.modelFilter.value || '';
    const symbol = elements.symbolFilter.value || '';
    const bg = elements.bgFilter.value || '';
    const max = parseFloat(elements.maxPrice.value) || Infinity;
    
    state.filteredGifts = state.giftsData.filter(nft => {
        const name = (nft.name || '').toLowerCase();
        const nftModel = nft.model || '';
        const nftSymbol = nft.symbol || '';
        const nftBg = nft.bg || nft.background || '';
        const price = nft.price || 0;
        
        // Search filter
        if (searchText && !name.includes(searchText)) return false;
        
        // Selected gifts filter
        if (state.selectedGifts.size > 0) {
            let matched = false;
            state.selectedGifts.forEach(gift => {
                if (name.includes(gift.toLowerCase())) matched = true;
            });
            if (!matched) return false;
        }
        
        // Model filter
        if (model && nftModel !== model) return false;
        
        // Symbol filter
        if (symbol && nftSymbol !== symbol) return false;
        
        // Backdrop filter
        if (bg && nftBg !== bg) return false;
        
        // Price filter
        if (price > max) return false;
        
        return true;
    });
    
    renderGrid(state.filteredGifts);
    updateBubbleBoard();
}

/**
 * Update sub-filters based on selected gifts
 */
function updateSubFiltersForSelectedGifts() {
    let relevantGifts = state.giftsData;
    
    if (state.selectedGifts.size > 0) {
        relevantGifts = state.giftsData.filter(g => {
            for (let gift of state.selectedGifts) {
                if (formatNFTName(g.name) === gift) return true;
            }
            return false;
        });
    }
    
    const models = [...new Set(relevantGifts.map(g => g.model).filter(Boolean))];
    const symbols = [...new Set(relevantGifts.map(g => g.symbol).filter(Boolean))];
    const bgs = [...new Set(relevantGifts.map(g => g.background).filter(Boolean))];
    
    if (elements.btnAllModels) {
        elements.btnAllModels.innerHTML = 'All Models ⬇<br>' + models.join('<br>');
    }
    if (elements.btnAllSymbols) {
        elements.btnAllSymbols.innerHTML = 'All Symbols ⬇<br>' + symbols.join('<br>');
    }
    if (elements.btnAllBackdrops) {
        elements.btnAllBackdrops.innerHTML = 'All Backdrops ⬇<br>' + bgs.join('<br>');
    }
}

// ===== GIFT BUBBLE FUNCTIONS =====

/**
 * Add gift bubble to selected gifts
 */
function addGiftBubble(gift) {
    if (state.selectedGifts.has(gift)) return;
    
    state.selectedGifts.add(gift);
    
    const bubble = document.createElement('div');
    bubble.className = 'gift-bubble';
    bubble.innerHTML = `
        ${gift}
        <span>×</span>
    `;
    
    bubble.addEventListener('click', (e) => {
        e.stopPropagation();
        state.selectedGifts.delete(gift);
        bubble.remove();
        filterNFT();
        updateSubFiltersForSelectedGifts();
        updateFilterPanelSelections();
    });
    
    elements.giftSelected.appendChild(bubble);
    elements.giftSearchInput.value = '';
    hideDropdown();
    filterNFT();
    updateSubFiltersForSelectedGifts();
    updateFilterPanelSelections();
}

/**
 * Create bubble for bubble board
 */
function createBubble(name, count = "", type = "gift") {
    const bubble = document.createElement('div');
    bubble.className = `gift-bubble ${type}`;
    bubble.textContent = count ? `${name} (${count})` : name;
    
    bubble.addEventListener('click', () => {
        switch (type) {
            case "gift":
                addGiftBubble(name);
                break;
            case "model":
                elements.modelFilter.value = elements.modelFilter.value === name ? "" : name;
                filterNFT();
                break;
            case "symbol":
                elements.symbolFilter.value = elements.symbolFilter.value === name ? "" : name;
                filterNFT();
                break;
            case "bg":
                elements.bgFilter.value = elements.bgFilter.value === name ? "" : name;
                filterNFT();
                break;
            case "sort":
                applySort(name);
                closeFilterModal();
                break;
        }
    });
    
    return bubble;
}

/**
 * Build bubble board
 */
function buildBubbles() {
    if (!elements.giftBubbleBoard) return;
    
    elements.giftBubbleBoard.innerHTML = '';
    
    // Gift counts
    const giftCounts = {};
    state.giftsData.forEach(g => {
        const name = formatNFTName(g.name);
        giftCounts[name] = (giftCounts[name] || 0) + 1;
    });
    
    // Add gift bubbles
    Object.entries(giftCounts)
        .sort((a, b) => b[1] - a[1])
        .forEach(([name, count]) => {
            const bubble = createBubble(name, count, "gift");
            elements.giftBubbleBoard.appendChild(bubble);
        });
    
    // Add model bubbles
    const models = [...new Set(state.giftsData.map(g => g.model).filter(Boolean))];
    models.forEach(m => {
        const bubble = createBubble(m, "", "model");
        elements.giftBubbleBoard.appendChild(bubble);
    });
    
    // Add symbol bubbles
    const symbols = [...new Set(state.giftsData.map(g => g.symbol).filter(Boolean))];
    symbols.forEach(s => {
        const bubble = createBubble(s, "", "symbol");
        elements.giftBubbleBoard.appendChild(bubble);
    });
    
    // Add backdrop bubbles
    const bgs = [...new Set(state.giftsData.map(g => g.background).filter(Boolean))];
    bgs.forEach(b => {
        const bubble = createBubble(b, "", "bg");
        elements.giftBubbleBoard.appendChild(bubble);
    });
}

/**
 * Update bubble board active states
 */
function updateBubbleBoard() {
    if (!elements.giftBubbleBoard) return;
    
    const bubbles = elements.giftBubbleBoard.querySelectorAll('.gift-bubble');
    bubbles.forEach(bubble => {
        bubble.classList.remove('active');
        
        if (bubble.dataset.type === 'model' && bubble.textContent === elements.modelFilter.value) {
            bubble.classList.add('active');
        }
        if (bubble.dataset.type === 'symbol' && bubble.textContent === elements.symbolFilter.value) {
            bubble.classList.add('active');
        }
        if (bubble.dataset.type === 'bg' && bubble.textContent === elements.bgFilter.value) {
            bubble.classList.add('active');
        }
    });
}

// ===== FILTER PANEL FUNCTIONS =====

/**
 * Open filter panel
 */
function openFilterPanel() {
    if (elements.filterPanel) {
        elements.filterPanel.classList.add('active');
        document.body.style.overflow = 'hidden';
        populateFilterOptions();
    }
}

/**
 * Close filter panel
 */
function closeFilterPanelFunc() {
    if (elements.filterPanel) {
        elements.filterPanel.classList.remove('active');
        document.body.style.overflow = '';
    }
}

/**
 * Populate filter select options
 */
function populateFilterOptions() {
    // Clear existing options
    if (elements.giftFilterSelect) elements.giftFilterSelect.innerHTML = '';
    if (elements.modelFilterSelect) elements.modelFilterSelect.innerHTML = '';
    if (elements.symbolFilterSelect) elements.symbolFilterSelect.innerHTML = '';
    if (elements.bgFilterSelect) elements.bgFilterSelect.innerHTML = '';
    
    // Gift options
    if (elements.giftFilterSelect) {
        const giftSet = new Set(state.giftsData.map(g => formatNFTName(g.name)));
        giftSet.forEach(gift => {
            const option = document.createElement('option');
            option.value = gift;
            option.textContent = gift;
            if (state.selectedGifts.has(gift)) {
                option.selected = true;
            }
            elements.giftFilterSelect.appendChild(option);
        });
    }
    
    // Model options
    if (elements.modelFilterSelect) {
        const modelSet = new Set(state.giftsData.map(g => g.model).filter(Boolean));
        modelSet.forEach(model => {
            const option = document.createElement('option');
            option.value = model;
            option.textContent = model;
            if (elements.modelFilter.value === model) {
                option.selected = true;
            }
            elements.modelFilterSelect.appendChild(option);
        });
    }
    
    // Symbol options
    if (elements.symbolFilterSelect) {
        const symbolSet = new Set(state.giftsData.map(g => g.symbol).filter(Boolean));
        symbolSet.forEach(symbol => {
            const option = document.createElement('option');
            option.value = symbol;
            option.textContent = symbol;
            if (elements.symbolFilter.value === symbol) {
                option.selected = true;
            }
            elements.symbolFilterSelect.appendChild(option);
        });
    }
    
    // Backdrop options
    if (elements.bgFilterSelect) {
        const bgSet = new Set(state.giftsData.map(g => g.background).filter(Boolean));
        bgSet.forEach(bg => {
            const option = document.createElement('option');
            option.value = bg;
            option.textContent = bg;
            if (elements.bgFilter.value === bg) {
                option.selected = true;
            }
            elements.bgFilterSelect.appendChild(option);
        });
    }
    
    // Max price
    if (elements.maxPriceFilter && elements.maxPrice.value) {
        elements.maxPriceFilter.value = elements.maxPrice.value;
    }
}

/**
 * Update filter panel selections
 */
function updateFilterPanelSelections() {
    if (!elements.giftFilterSelect) return;
    
    const options = Array.from(elements.giftFilterSelect.options);
    options.forEach(opt => {
        opt.selected = state.selectedGifts.has(opt.value);
    });
}

/**
 * Setup filter search functionality
 */
function setupFilterSearch(inputElement, selectElement) {
    if (!inputElement || !selectElement) return;
    
    inputElement.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        const options = selectElement.options;
        
        for (let i = 0; i < options.length; i++) {
            const option = options[i];
            const text = option.textContent.toLowerCase();
            option.style.display = text.includes(searchTerm) ? '' : 'none';
        }
    });
}

/**
 * Apply filters from filter panel
 */
function applyFilters() {
    // Clear existing selected gifts
    state.selectedGifts.clear();
    if (elements.giftSelected) {
        elements.giftSelected.innerHTML = '';
    }
    
    // Get selected gifts
    if (elements.giftFilterSelect) {
        Array.from(elements.giftFilterSelect.selectedOptions).forEach(option => {
            addGiftBubble(option.value);
        });
    }
    
    // Get selected model
    if (elements.modelFilterSelect) {
        const selectedModels = Array.from(elements.modelFilterSelect.selectedOptions).map(opt => opt.value);
        elements.modelFilter.value = selectedModels.length > 0 ? selectedModels[0] : '';
    }
    
    // Get selected symbol
    if (elements.symbolFilterSelect) {
        const selectedSymbols = Array.from(elements.symbolFilterSelect.selectedOptions).map(opt => opt.value);
        elements.symbolFilter.value = selectedSymbols.length > 0 ? selectedSymbols[0] : '';
    }
    
    // Get selected backdrop
    if (elements.bgFilterSelect) {
        const selectedBgs = Array.from(elements.bgFilterSelect.selectedOptions).map(opt => opt.value);
        elements.bgFilter.value = selectedBgs.length > 0 ? selectedBgs[0] : '';
    }
    
    // Get max price
    if (elements.maxPriceFilter && elements.maxPrice) {
        elements.maxPrice.value = elements.maxPriceFilter.value || '';
    }
    
    filterNFT();
    closeFilterPanelFunc();
}

/**
 * Reset all filters
 */
function resetFilters() {
    // Clear filter panel selections
    if (elements.giftFilterSelect) elements.giftFilterSelect.selectedIndex = -1;
    if (elements.modelFilterSelect) elements.modelFilterSelect.selectedIndex = -1;
    if (elements.symbolFilterSelect) elements.symbolFilterSelect.selectedIndex = -1;
    if (elements.bgFilterSelect) elements.bgFilterSelect.selectedIndex = -1;
    if (elements.maxPriceFilter) elements.maxPriceFilter.value = '';
    
    // Clear filter search inputs
    if (elements.giftSearchFilter) elements.giftSearchFilter.value = '';
    if (elements.modelSearchFilter) elements.modelSearchFilter.value = '';
    if (elements.symbolSearchFilter) elements.symbolSearchFilter.value = '';
    if (elements.bgSearchFilter) elements.bgSearchFilter.value = '';
    
    // Clear main filters
    elements.modelFilter.value = '';
    elements.symbolFilter.value = '';
    elements.bgFilter.value = '';
    elements.maxPrice.value = '';
    
    // Clear selected gifts
    state.selectedGifts.clear();
    if (elements.giftSelected) {
        elements.giftSelected.innerHTML = '';
    }
    
    // Clear search input
    if (elements.giftSearchInput) {
        elements.giftSearchInput.value = '';
    }
    
    // Show all gifts
    state.filteredGifts = [...state.giftsData];
    renderGrid(state.filteredGifts);
    closeFilterPanelFunc();
}

// ===== FILTER MODAL FUNCTIONS (OLD - COMPATIBILITY) =====

/**
 * Open filter modal
 */
function openFilterModal(items, type) {
    if (!elements.filterBubbleBoard) return;
    
    elements.filterBubbleBoard.innerHTML = '';
    
    items.forEach(item => {
        const bubble = document.createElement('div');
        bubble.className = 'filter-bubble';
        bubble.textContent = item;
        
        bubble.addEventListener('click', () => {
            switch(type) {
                case "gift": 
                    addGiftBubble(item); 
                    break;
                case "model": 
                    elements.modelFilter.value = item; 
                    filterNFT(); 
                    break;
                case "symbol": 
                    elements.symbolFilter.value = item; 
                    filterNFT(); 
                    break;
                case "bg": 
                    elements.bgFilter.value = item; 
                    filterNFT(); 
                    break;
                case "sort": 
                    applySort(item); 
                    break;
            }
            closeFilterModal();
        });
        
        elements.filterBubbleBoard.appendChild(bubble);
    });
    
    if (elements.filterOverlay) {
        elements.filterOverlay.style.display = 'flex';
    }
}

/**
 * Close filter modal
 */
function closeFilterModal() {
    if (elements.filterOverlay) {
        elements.filterOverlay.style.display = 'none';
    }
}

// ===== SORT FUNCTIONS =====

/**
 * Apply sorting
 */
function applySort(sortTypeText) {
    const sortTypeMap = {
        "⏰ Lasted": "lasted",
        "💸 Low To High": "low",
        "💸 High To Low": "high",
        "🆔 ID Ascending": "idAsc",
        "🆔 ID Descending": "idDesc"
    };
    
    const sortType = sortTypeMap[sortTypeText] || sortTypeText;
    state.sortType = sortType;
    
    const sorted = [...state.giftsData];
    
    switch(sortType) {
        case 'lasted':
            sorted.sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0));
            break;
        case 'low':
            sorted.sort((a, b) => (a.price || 0) - (b.price || 0));
            break;
        case 'high':
            sorted.sort((a, b) => (b.price || 0) - (a.price || 0));
            break;
        case 'idAsc':
            sorted.sort((a, b) => (a.id || 0) - (b.id || 0));
            break;
        case 'idDesc':
            sorted.sort((a, b) => (b.id || 0) - (a.id || 0));
            break;
        default:
            return;
    }
    
    state.giftsData = sorted;
    state.filteredGifts = sorted;
    renderGrid(state.filteredGifts);
}

// ===== DETAIL PANEL FUNCTIONS =====

/**
 * Open detail panel
 */
function openPanel() {
    elements.panel.classList.add('active');
    elements.overlay.classList.add('active');
}

/**
 * Close detail panel
 */
function closePanel() {
    elements.panel.classList.remove('active');
    elements.overlay.classList.remove('active');
    elements.panel.style.bottom = '';
}

// ===== DROPDOWN FUNCTIONS =====

/**
 * Show search dropdown
 */
function showDropdown(suggestions) {
    if (!elements.giftDropdown) return;
    
    elements.giftDropdown.innerHTML = '';
    
    suggestions.forEach(g => {
        const div = document.createElement('div');
        div.textContent = g;
        div.addEventListener('click', () => addGiftBubble(g));
        elements.giftDropdown.appendChild(div);
    });
    
    elements.giftDropdown.style.display = suggestions.length ? 'block' : 'none';
    elements.giftDropdown.classList.toggle('active', suggestions.length > 0);
}

/**
 * Hide search dropdown
 */
function hideDropdown() {
    if (elements.giftDropdown) {
        elements.giftDropdown.style.display = 'none';
        elements.giftDropdown.classList.remove('active');
    }
}

// ===== SEARCH FUNCTIONS =====

/**
 * Search gifts
 */
function searchGifts() {
    filterNFT();
    hideDropdown();
}

// ===== EVENT LISTENERS =====

/**
 * Setup all event listeners
 */
function setupEventListeners() {
    // Close panel on overlay click
    if (elements.overlay) {
        elements.overlay.addEventListener('click', closePanel);
    }
    
    // Scroll to top button
    window.addEventListener('scroll', () => {
        if (window.scrollY > 300) {
            elements.scrollTopBtn.classList.add('visible');
        } else {
            elements.scrollTopBtn.classList.remove('visible');
        }
    });
    
    if (elements.scrollTopBtn) {
        elements.scrollTopBtn.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }
    
    // Search input
    if (elements.giftSearchInput) {
        elements.giftSearchInput.addEventListener('input', () => {
            const val = elements.giftSearchInput.value.toLowerCase();
            
            if (!val) {
                hideDropdown();
                return;
            }
            
            const filtered = state.giftList.filter(g => 
                g.toLowerCase().includes(val) && !state.selectedGifts.has(g)
            );
            
            showDropdown(filtered);
        });
        
        elements.giftSearchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                searchGifts();
            }
        });
    }
    
    // Search button
    if (elements.giftSearchBtn) {
        elements.giftSearchBtn.addEventListener('click', searchGifts);
    }
    
    // Grid click
    if (elements.grid) {
        elements.grid.addEventListener('click', (e) => {
            const card = e.target.closest('.gift-card');
            if (!card) return;
            
            const nftId = card.dataset.id;
            const nft = state.giftsData.find(g => String(g.id) === nftId);
            if (!nft) return;
            
            // Update detail panel
            elements.detailImg.src = getPreviewImage(nft);
            elements.detailImg.alt = formatNFTName(nft.name);
            elements.detailTitle.textContent = `${formatNFTName(nft.name)} #${nft.id}`;
            elements.detailModel.textContent = nft.model || '-';
            elements.detailBg.textContent = nft.bg || nft.background || '-';
            elements.detailSymbol.textContent = nft.symbol || '-';
            elements.detailPrice.textContent = formatIDR(nft.price);
            
            // Generate Telegram links
            const baseUrl = "https://t.me/marketaldibot?start=";
            const slug = (nft.name || '').replace(/\s+/g, "") + "_" + nft.id;
            
            if (elements.btnBeli) {
                elements.btnBeli.href = baseUrl + "beli_" + slug;
            }
            
            if (elements.btnNego) {
                elements.btnNego.href = baseUrl + "nego_" + slug;
            }
            
            openPanel();
        });
    }
    
    // Close panel button
    const closeBtn = document.getElementById("closePanel");
    if (closeBtn) {
        closeBtn.addEventListener("click", closePanel);
    }
    
    // Filter inputs
    [elements.giftSearchInput, elements.modelFilter, elements.symbolFilter, elements.bgFilter, elements.maxPrice].forEach(el => {
        if (el && el.addEventListener) {
            el.addEventListener("input", filterNFT);
        }
    });
    
    // Click outside dropdown
    document.addEventListener('click', (e) => {
        if (elements.giftSearchInput && 
            !elements.giftSearchInput.contains(e.target) && 
            elements.giftDropdown && 
            !elements.giftDropdown.contains(e.target)) {
            hideDropdown();
        }
    });
    
    // Filter Overlay click
    if (elements.filterOverlay) {
        elements.filterOverlay.addEventListener('click', (e) => {
            if (e.target === elements.filterOverlay) {
                closeFilterModal();
            }
        });
    }
    
    // Old filter buttons (compatibility)
    if (elements.btnAllGifts) {
        elements.btnAllGifts.addEventListener('click', () => {
            const gifts = [...new Set(state.giftsData.map(g => formatNFTName(g.name)))];
            openFilterModal(gifts, "gift");
        });
    }
    
    if (elements.btnAllModels) {
        elements.btnAllModels.addEventListener('click', () => {
            const models = [...new Set(state.giftsData.map(g => g.model).filter(Boolean))];
            openFilterModal(models, "model");
        });
    }
    
    if (elements.btnAllSymbols) {
        elements.btnAllSymbols.addEventListener('click', () => {
            const symbols = [...new Set(state.giftsData.map(g => g.symbol).filter(Boolean))];
            openFilterModal(symbols, "symbol");
        });
    }
    
    if (elements.btnAllBackdrops) {
        elements.btnAllBackdrops.addEventListener('click', () => {
            const bgs = [...new Set(state.giftsData.map(g => g.background).filter(Boolean))];
            openFilterModal(bgs, "bg");
        });
    }
    
    if (elements.btnSort) {
        elements.btnSort.addEventListener('click', () => {
            const sorts = ["⏰ Lasted", "💸 Low To High", "💸 High To Low", "🆔 ID Ascending", "🆔 ID Descending"];
            openFilterModal(sorts, "sort");
        });
    }
    
    // Sort options
    if (elements.sortOptions && elements.sortOptions.children.length) {
        Array.from(elements.sortOptions.querySelectorAll('div')).forEach(opt => {
            opt.addEventListener('click', () => {
                const sortType = opt.dataset.sort;
                applySort(sortType);
                elements.sortOptions.style.display = 'none';
            });
        });
    }
    
    // ===== NEW FILTER PANEL EVENT LISTENERS =====
    if (elements.filterToggleBtn) {
        elements.filterToggleBtn.addEventListener('click', openFilterPanel);
    }
    
    if (elements.closeFilterPanel) {
        elements.closeFilterPanel.addEventListener('click', closeFilterPanelFunc);
    }
    
    if (elements.applyFilterBtn) {
        elements.applyFilterBtn.addEventListener('click', applyFilters);
    }
    
    if (elements.cancelFilterBtn) {
        elements.cancelFilterBtn.addEventListener('click', resetFilters);
    }
    
    // Setup filter search
    setupFilterSearch(elements.giftSearchFilter, elements.giftFilterSelect);
    setupFilterSearch(elements.modelSearchFilter, elements.modelFilterSelect);
    setupFilterSearch(elements.symbolSearchFilter, elements.symbolFilterSelect);
    setupFilterSearch(elements.bgSearchFilter, elements.bgFilterSelect);
    
    // Close filter panel on outside click
    if (elements.filterPanel) {
        elements.filterPanel.addEventListener('click', (e) => {
            if (e.target === elements.filterPanel) {
                closeFilterPanelFunc();
            }
        });
    }
}

// ===== PANEL DRAGGING (TOUCH) =====

let startY = 0, currentY = 0, isDragging = false;

if (elements.panel) {
    elements.panel.addEventListener('touchstart', (e) => {
        if (e.target.closest('a') || e.target.closest('.close-panel')) return;
        startY = e.touches[0].clientY;
        isDragging = true;
        elements.panel.classList.add('dragging');
    });
    
    elements.panel.addEventListener('touchmove', (e) => {
        if (!isDragging) return;
        e.preventDefault();
        currentY = e.touches[0].clientY;
        const diff = currentY - startY;
        if (diff > 0) {
            elements.panel.style.bottom = `-${diff}px`;
        }
    });
    
    elements.panel.addEventListener('touchend', () => {
        if (!isDragging) return;
        elements.panel.classList.remove('dragging');
        const diff = currentY - startY;
        if (diff > 120) {
            closePanel();
        } else {
            elements.panel.style.bottom = '0';
        }
        isDragging = false;
        startY = currentY = 0;
    });
}

// ===== INITIAL LOAD =====

/**
 * Initialize the app
 */
async function initApp() {
    try {
        const response = await fetch("export/data.json");
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        state.giftsData = Array.isArray(data) ? data : [];
        state.filteredGifts = [...state.giftsData];
        
        // Create gift list without numbers
        const set = new Set();
        state.giftsData.forEach(g => {
            const giftName = formatNFTName(g.name);
            if (giftName) set.add(giftName);
        });
        state.giftList = Array.from(set);
        
        // Render grid
        renderGrid(state.giftsData);
        
        // Build bubbles
        buildBubbles();
        
        // Populate filter options
        populateFilterOptions();
        
        // Hide old filter buttons
        if (elements.btnAllGifts) elements.btnAllGifts.style.display = 'none';
        if (elements.btnAllModels) elements.btnAllModels.style.display = 'none';
        if (elements.btnAllSymbols) elements.btnAllSymbols.style.display = 'none';
        if (elements.btnAllBackdrops) elements.btnAllBackdrops.style.display = 'none';
        
        // Hide loader
        setTimeout(() => {
            if (elements.pageLoader) {
                elements.pageLoader.classList.add('hide');
            }
        }, 500);
        
    } catch (error) {
        console.error("Failed to load data:", error);
        
        // Show error in grid
        if (elements.grid) {
            elements.grid.innerHTML = `
                <div class="error-state">
                    <div class="error-icon">⚠️</div>
                    <h3>Gagal Memuat Data</h3>
                    <p>${error.message || 'Periksa koneksi internet Anda'}</p>
                    <button onclick="location.reload()" class="btn btn-primary">
                        Coba Lagi
                    </button>
                </div>
            `;
        }
        
        // Hide loader
        if (elements.pageLoader) {
            elements.pageLoader.classList.add('hide');
        }
    }
}

// ===== GLOBAL FUNCTIONS =====

/**
 * Clear all filters
 */
window.clearAllFilters = function() {
    resetFilters();
};

/**
 * Show all gifts
 */
window.showAllGifts = function() {
    if (elements.giftSearchInput) elements.giftSearchInput.value = '';
    resetFilters();
    filterNFT();
};

// ===== START APP =====
document.addEventListener('DOMContentLoaded', () => {
    initApp();
    setupEventListeners();
});
