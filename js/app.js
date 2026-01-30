// ===== ELEMENT REFERENCES =====
const giftFilter = document.getElementById("giftFilter") || { value: "" };
const modelFilter = document.getElementById("modelFilter") || { value: "" };
const symbolFilter = document.getElementById("symbolFilter") || { value: "" };
const bgFilter = document.getElementById("bgFilter") || { value: "" };
const maxPrice = document.getElementById("maxPrice") || { value: "" };
const grid = document.getElementById("giftGrid") || document.createElement("div");
const giftSearchInput = document.getElementById("giftSearchInput") || { value: "" };
const giftDropdown = document.getElementById("giftDropdown") || { style: {}, innerHTML: "" };
const giftSelected = document.getElementById("giftSelected") || document.createElement("div");
const panel = document.getElementById("giftDetailPanel") || document.createElement("div");
const overlay = document.getElementById("panelOverlay") || document.createElement("div");
const btnBeli = document.getElementById("btnBeli") || document.createElement("a");
const btnNego = document.getElementById("btnNego") || document.createElement("a");
const pageLoader = document.getElementById("pageLoader") || document.createElement("div");
const scrollTopBtn = document.getElementById("scrollTopBtn") || document.createElement("div");
const btnAllGifts = document.getElementById("btnAllGifts") || document.createElement("button");
const btnAllModels = document.getElementById("btnAllModels") || document.createElement("button");
const btnAllSymbols = document.getElementById("btnAllSymbols") || document.createElement("button");
const btnAllBackdrops = document.getElementById("btnAllBackdrops") || document.createElement("button");
const btnSort = document.getElementById("btnSort") || document.createElement("button");
const sortOptions = document.getElementById("sortOptions") || document.createElement("div");
const subFilters = document.getElementById("subFilters") || document.createElement("div");
const giftBubbleBoard = document.getElementById("giftBubbleBoard");
const filterOverlay = document.getElementById("filterOverlay");
const filterBubbleBoard = document.getElementById("filterBubbleBoard");

// ===== NEW ELEMENTS FOR FILTER PANEL =====
const filterToggleBtn = document.getElementById("filterToggleBtn") || document.createElement("button");
const filterPanel = document.getElementById("filterPanel") || document.createElement("div");
const closeFilterPanel = document.getElementById("closeFilterPanel") || document.createElement("button");
const applyFilterBtn = document.getElementById("applyFilterBtn") || document.createElement("button");
const cancelFilterBtn = document.getElementById("cancelFilterBtn") || document.createElement("button");

// Filter select elements
const giftFilterSelect = document.getElementById("giftFilterSelect") || document.createElement("select");
const modelFilterSelect = document.getElementById("modelFilterSelect") || document.createElement("select");
const symbolFilterSelect = document.getElementById("symbolFilterSelect") || document.createElement("select");
const bgFilterSelect = document.getElementById("bgFilterSelect") || document.createElement("select");
const maxPriceFilter = document.getElementById("maxPriceFilter") || document.createElement("input");

// Search inputs for filter
const giftSearchFilter = document.getElementById("giftSearchFilter") || document.createElement("input");
const modelSearchFilter = document.getElementById("modelSearchFilter") || document.createElement("input");
const symbolSearchFilter = document.getElementById("symbolSearchFilter") || document.createElement("input");
const bgSearchFilter = document.getElementById("bgSearchFilter") || document.createElement("input");

// Detail Panel Elements
const detailImg = document.getElementById("detailImg") || document.createElement("img");
const detailTitle = document.getElementById("detailTitle") || document.createElement("div");
const detailModel = document.getElementById("detailModel") || document.createElement("b");
const detailBg = document.getElementById("detailBg") || document.createElement("b");
const detailSymbol = document.getElementById("detailSymbol") || document.createElement("b");
const detailPrice = document.getElementById("detailPrice") || document.createElement("b");

// ===== VARIABLES =====
let giftsData = [];
let cards = [];
let giftList = [];
let filteredGifts = [];
let selectedGifts = new Set();
let selectedGift = null;

// ===== FORMATTING FUNCTIONS =====
function formatIDR(number) {
    return "Rp" + Number(number || 0).toLocaleString("id-ID");
}

function formatNFTName(name) {
    if (!name) return "";
    // Hapus angka dan karakter khusus di akhir nama
    return name.replace(/\s*#\d+$/, "").trim();
}

function getPreviewImage(nft) {
    // Prioritaskan gambar dari data jika ada
    if (nft.image && (nft.image.includes("/previews/") || nft.image.includes("http"))) {
        return nft.image;
    }
    // Fallback ke file preview berdasarkan slug atau ID
    if (nft.slug) {
        return `previews/${nft.slug}.jpg`;
    }
    return `previews/${nft.id}.jpg`;
}

// ===== PANEL FUNCTIONS =====
function openPanel() {
    panel.classList.add("active");
    overlay.classList.add("active");
}

function closePanel() {
    panel.classList.remove("active");
    overlay.classList.remove("active");
    panel.style.bottom = "";
}

// ===== GRID FUNCTIONS =====
function renderGrid(data) {
    grid.innerHTML = "";
    
    data.forEach(nft => {
        const div = document.createElement("div");
        div.className = "card";
        div.dataset.id = nft.id;
        div.dataset.name = nft.name.toLowerCase();
        div.dataset.model = nft.model || "";
        div.dataset.symbol = nft.symbol || "";
        div.dataset.bg = nft.bg || nft.background || "";
        div.dataset.price = nft.price || 0;
        
        // Format data untuk ditampilkan
        const giftName = formatNFTName(nft.name);
        const giftId = nft.id;
        const giftPrice = formatIDR(nft.price);
        const previewImage = getPreviewImage(nft);
        
        div.innerHTML = `
            <div class="card-image-container">
                <img src="${previewImage}" alt="${giftName}" 
                     onerror="this.src='https://via.placeholder.com/400x300?text=No+Preview'">
            </div>
            <div class="card-content">
                <div class="card-text">
                    <h3 class="gift-name">${giftName}</h3>
                    <p class="gift-id">#${giftId}</p>
                </div>
                <span class="price-bubble">${giftPrice}</span>
            </div>
        `;
        
        grid.appendChild(div);
    });

    cards = Array.from(document.querySelectorAll(".card"));
    filterNFT(); // Apply any existing filters after rendering
}

// ===== FILTER FUNCTIONS =====
function filterNFT() {
    const searchText = giftSearchInput.value.toLowerCase().trim();
    const model = modelFilter.value || "";
    const symbol = symbolFilter.value || "";
    const bg = bgFilter.value || "";
    const max = maxPrice.value ? parseFloat(maxPrice.value) : Infinity;

    cards.forEach(card => {
        let show = true;
        const cardName = card.dataset.name || "";
        const cardModel = card.dataset.model || "";
        const cardSymbol = card.dataset.symbol || "";
        const cardBg = card.dataset.bg || "";
        const cardPrice = parseFloat(card.dataset.price) || 0;

        // Search by name
        if (searchText && !cardName.includes(searchText)) show = false;

        // Filter by selected gifts
        if (selectedGifts.size > 0) {
            let matched = false;
            selectedGifts.forEach(gift => {
                if (cardName.includes(gift.toLowerCase())) matched = true;
            });
            if (!matched) show = false;
        }

        // Filter by model
        if (model && cardModel !== model) show = false;
        
        // Filter by symbol
        if (symbol && cardSymbol !== symbol) show = false;
        
        // Filter by backdrop
        if (bg && cardBg !== bg) show = false;
        
        // Filter by max price
        if (cardPrice > max) show = false;

        card.style.display = show ? "block" : "none";
    });
}

function updateSubFiltersForSelectedGifts() {
    let relevantGifts = giftsData;
    
    if (selectedGifts.size > 0) {
        relevantGifts = giftsData.filter(g => {
            for (let gift of selectedGifts) {
                if (g.name.replace(/ #\d+$/, '') === gift) return true;
            }
            return false;
        });
    }

    const models = [...new Set(relevantGifts.map(g => g.model).filter(Boolean))];
    const symbols = [...new Set(relevantGifts.map(g => g.symbol).filter(Boolean))];
    const bgs = [...new Set(relevantGifts.map(g => g.background).filter(Boolean))];

    if (btnAllModels) btnAllModels.innerHTML = 'All Models ⬇<br>' + models.join('<br>');
    if (btnAllSymbols) btnAllSymbols.innerHTML = 'All Symbols ⬇<br>' + symbols.join('<br>');
    if (btnAllBackdrops) btnAllBackdrops.innerHTML = 'All Backdrops ⬇<br>' + bgs.join('<br>');
}

// ===== GIFT BUBBLE FUNCTIONS =====
function addGiftBubble(gift) {
    if (selectedGifts.has(gift)) return;
    selectedGifts.add(gift);

    // Create bubble element
    const bubble = document.createElement("div");
    bubble.className = "gift-bubble";
    bubble.textContent = gift;
    
    // Add close button
    const closeBtn = document.createElement("span");
    closeBtn.textContent = " ×";
    closeBtn.style.cursor = "pointer";
    closeBtn.style.fontWeight = "bold";
    bubble.appendChild(closeBtn);

    // Add click event to remove bubble
    bubble.addEventListener("click", (e) => {
        if (e.target === closeBtn || e.target === bubble) {
            selectedGifts.delete(gift);
            bubble.remove();
            filterNFT();
            updateSubFiltersForSelectedGifts();
        }
    });

    if (giftSelected) {
        giftSelected.appendChild(bubble);
    }
    
    giftSearchInput.value = "";
    if (giftDropdown) giftDropdown.style.display = "none";
    filterNFT();
    updateSubFiltersForSelectedGifts();
}

function createBubble(name, count = "", type = "gift") {
    const bubble = document.createElement("div");
    bubble.className = "gift-bubble";
    bubble.textContent = count ? `${name} (${count})` : name;
    bubble.dataset.type = type;

    bubble.addEventListener("click", () => {
        switch (type) {
            case "gift":
                addGiftBubble(name);
                break;
            case "model":
                modelFilter.value = modelFilter.value === name ? "" : name;
                filterNFT();
                break;
            case "symbol":
                symbolFilter.value = symbolFilter.value === name ? "" : name;
                filterNFT();
                break;
            case "bg":
                bgFilter.value = bgFilter.value === name ? "" : name;
                filterNFT();
                break;
        }
    });

    return bubble;
}

function buildBubbles() {
    if (giftBubbleBoard) {
        giftBubbleBoard.innerHTML = "";

        // Gifts
        const giftCounts = {};
        giftsData.forEach(g => {
            const name = g.name.replace(/ #\d+$/, '');
            giftCounts[name] = (giftCounts[name] || 0) + 1;
        });
        
        Object.entries(giftCounts).forEach(([name, count]) => {
            const bubble = createBubble(name, count, "gift");
            giftBubbleBoard.appendChild(bubble);
        });

        // Models
        const modelsSet = new Set(giftsData.map(g => g.model).filter(Boolean));
        modelsSet.forEach(m => {
            const bubble = createBubble(m, "", "model");
            giftBubbleBoard.appendChild(bubble);
        });

        // Symbols
        const symbolsSet = new Set(giftsData.map(g => g.symbol).filter(Boolean));
        symbolsSet.forEach(s => {
            const bubble = createBubble(s, "", "symbol");
            giftBubbleBoard.appendChild(bubble);
        });

        // Backdrops
        const bgsSet = new Set(giftsData.map(g => g.background).filter(Boolean));
        bgsSet.forEach(b => {
            const bubble = createBubble(b, "", "bg");
            giftBubbleBoard.appendChild(bubble);
        });
    }
}

// ===== FILTER PANEL FUNCTIONS =====
function openFilterPanel() {
    if (filterPanel) {
        filterPanel.classList.add("active");
        document.body.style.overflow = "hidden";
    }
}

function closeFilterPanelFunc() {
    if (filterPanel) {
        filterPanel.classList.remove("active");
        document.body.style.overflow = "";
    }
}

function populateFilterOptions() {
    // Clear existing options
    if (giftFilterSelect) giftFilterSelect.innerHTML = "";
    if (modelFilterSelect) modelFilterSelect.innerHTML = "";
    if (symbolFilterSelect) symbolFilterSelect.innerHTML = "";
    if (bgFilterSelect) bgFilterSelect.innerHTML = "";

    // Populate gift options
    if (giftFilterSelect) {
        const giftSet = new Set(giftsData.map(g => g.name.replace(/ #\d+$/, '')));
        giftSet.forEach(gift => {
            const option = document.createElement("option");
            option.value = gift;
            option.textContent = gift;
            
            if (selectedGifts.has(gift)) {
                option.selected = true;
            }
            
            giftFilterSelect.appendChild(option);
        });
    }

    // Populate model options
    if (modelFilterSelect) {
        const modelSet = new Set(giftsData.map(g => g.model).filter(Boolean));
        modelSet.forEach(model => {
            const option = document.createElement("option");
            option.value = model;
            option.textContent = model;
            
            if (modelFilter.value === model) {
                option.selected = true;
            }
            
            modelFilterSelect.appendChild(option);
        });
    }

    // Populate symbol options
    if (symbolFilterSelect) {
        const symbolSet = new Set(giftsData.map(g => g.symbol).filter(Boolean));
        symbolSet.forEach(symbol => {
            const option = document.createElement("option");
            option.value = symbol;
            option.textContent = symbol;
            
            if (symbolFilter.value === symbol) {
                option.selected = true;
            }
            
            symbolFilterSelect.appendChild(option);
        });
    }

    // Populate backdrop options
    if (bgFilterSelect) {
        const bgSet = new Set(giftsData.map(g => g.background).filter(Boolean));
        bgSet.forEach(bg => {
            const option = document.createElement("option");
            option.value = bg;
            option.textContent = bg;
            
            if (bgFilter.value === bg) {
                option.selected = true;
            }
            
            bgFilterSelect.appendChild(option);
        });
    }

    // Set max price
    if (maxPriceFilter && maxPrice.value) {
        maxPriceFilter.value = maxPrice.value;
    }
}

function setupFilterSearch(inputElement, selectElement) {
    if (inputElement && selectElement) {
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
}

function applyFilters() {
    // Clear existing selected gifts
    selectedGifts.clear();
    if (giftSelected) giftSelected.innerHTML = "";

    // Get selected gifts from filter panel
    if (giftFilterSelect) {
        Array.from(giftFilterSelect.selectedOptions).forEach(option => {
            addGiftBubble(option.value);
        });
    }

    // Get selected model
    if (modelFilterSelect) {
        const selectedModels = Array.from(modelFilterSelect.selectedOptions).map(opt => opt.value);
        modelFilter.value = selectedModels.length > 0 ? selectedModels[0] : "";
    }

    // Get selected symbol
    if (symbolFilterSelect) {
        const selectedSymbols = Array.from(symbolFilterSelect.selectedOptions).map(opt => opt.value);
        symbolFilter.value = selectedSymbols.length > 0 ? selectedSymbols[0] : "";
    }

    // Get selected backdrop
    if (bgFilterSelect) {
        const selectedBgs = Array.from(bgFilterSelect.selectedOptions).map(opt => opt.value);
        bgFilter.value = selectedBgs.length > 0 ? selectedBgs[0] : "";
    }

    // Get max price
    if (maxPriceFilter && maxPrice) {
        maxPrice.value = maxPriceFilter.value || "";
    }

    // Apply filters
    filterNFT();
    closeFilterPanelFunc();
}

function resetFilters() {
    // Clear all selections in filter panel
    if (giftFilterSelect) giftFilterSelect.selectedIndex = -1;
    if (modelFilterSelect) modelFilterSelect.selectedIndex = -1;
    if (symbolFilterSelect) symbolFilterSelect.selectedIndex = -1;
    if (bgFilterSelect) bgFilterSelect.selectedIndex = -1;
    if (maxPriceFilter) maxPriceFilter.value = "";
    
    // Clear search inputs in filter panel
    if (giftSearchFilter) giftSearchFilter.value = "";
    if (modelSearchFilter) modelSearchFilter.value = "";
    if (symbolSearchFilter) symbolSearchFilter.value = "";
    if (bgSearchFilter) bgSearchFilter.value = "";
    
    // Reset main filter inputs
    modelFilter.value = "";
    symbolFilter.value = "";
    bgFilter.value = "";
    maxPrice.value = "";
    
    // Reset selected gifts
    selectedGifts.clear();
    if (giftSelected) giftSelected.innerHTML = "";
    
    // Reset search input
    if (giftSearchInput) giftSearchInput.value = "";
    
    // Show all gifts
    filterNFT();
    closeFilterPanelFunc();
}

// ===== FILTER MODAL FUNCTIONS (KEEPING OLD FUNCTIONALITY) =====
function openFilterModal(items, type) {
    if (filterBubbleBoard) {
        filterBubbleBoard.innerHTML = "";
        
        items.forEach(item => {
            const bubble = document.createElement("div");
            bubble.className = "filter-bubble";
            bubble.textContent = item;

            bubble.addEventListener("click", () => {
                switch(type) {
                    case "gift": 
                        addGiftBubble(item); 
                        break;
                    case "model": 
                        modelFilter.value = item; 
                        filterNFT(); 
                        break;
                    case "symbol": 
                        symbolFilter.value = item; 
                        filterNFT(); 
                        break;
                    case "bg": 
                        bgFilter.value = item; 
                        filterNFT(); 
                        break;
                    case "sort": 
                        applySort(item); 
                        break;
                }
                closeFilterModal();
            });

            filterBubbleBoard.appendChild(bubble);
        });

        if (filterOverlay) {
            filterOverlay.style.display = "flex";
        }
    }
}

function closeFilterModal() {
    if (filterOverlay) {
        filterOverlay.style.display = "none";
    }
}

// ===== SORT FUNCTIONS =====
function applySort(sortTypeText) {
    const sortTypeMap = {
        "⏰ Lasted": "lasted",
        "💸 Low To High": "low",
        "💸 High To Low": "high",
        "🆔 ID Ascending": "idAsc",
        "🆔 ID Descending": "idDesc"
    };
    const sortType = sortTypeMap[sortTypeText];

    const sorted = [...giftsData];
    switch(sortType) {
        case 'lasted': 
            sorted.sort((a,b) => new Date(b.created_at || 0) - new Date(a.created_at || 0)); 
            break;
        case 'low': 
            sorted.sort((a,b) => (a.price || 0) - (b.price || 0)); 
            break;
        case 'high': 
            sorted.sort((a,b) => (b.price || 0) - (a.price || 0)); 
            break;
        case 'idAsc': 
            sorted.sort((a,b) => (a.id || 0) - (b.id || 0)); 
            break;
        case 'idDesc': 
            sorted.sort((a,b) => (b.id || 0) - (a.id || 0)); 
            break;
    }
    renderGrid(sorted);
}

// ===== EVENT LISTENERS =====
if (overlay) {
    overlay.addEventListener("click", closePanel);
}

window.addEventListener("scroll", () => {
    const card = document.querySelector(".card");
    if (!card) return;
    const threshold = card.offsetHeight * 3;
    if (scrollTopBtn) {
        scrollTopBtn.classList.toggle("visible", window.scrollY > threshold);
    }
});

if (scrollTopBtn) {
    scrollTopBtn.addEventListener("click", () => {
        window.scrollTo({ top: 0, behavior: "smooth" });
    });
}

if (giftSearchInput) {
    giftSearchInput.addEventListener("input", () => {
        const val = giftSearchInput.value.toLowerCase();
        if (giftDropdown) {
            giftDropdown.innerHTML = "";
            
            if (!val) { 
                giftDropdown.style.display = "none"; 
                return; 
            }

            const filtered = giftList.filter(g => 
                g.toLowerCase().includes(val) && !selectedGifts.has(g)
            );
            
            filtered.forEach(g => {
                const div = document.createElement("div");
                div.textContent = g;
                div.addEventListener("click", () => addGiftBubble(g));
                giftDropdown.appendChild(div);
            });

            giftDropdown.style.display = filtered.length ? "block" : "none";
        }
    });
}

// Filter Buttons (old - kept for compatibility)
if (btnAllGifts) {
    btnAllGifts.addEventListener('click', () => {
        const gifts = [...new Set(giftsData.map(g => g.name.replace(/ #\d+$/, '')))];
        openFilterModal(gifts, "gift");
    });
}

if (btnAllModels) {
    btnAllModels.addEventListener('click', () => {
        const models = [...new Set(giftsData.map(g => g.model).filter(Boolean))];
        openFilterModal(models, "model");
    });
}

if (btnAllSymbols) {
    btnAllSymbols.addEventListener('click', () => {
        const symbols = [...new Set(giftsData.map(g => g.symbol).filter(Boolean))];
        openFilterModal(symbols, "symbol");
    });
}

if (btnAllBackdrops) {
    btnAllBackdrops.addEventListener('click', () => {
        const bgs = [...new Set(giftsData.map(g => g.background).filter(Boolean))];
        openFilterModal(bgs, "bg");
    });
}

// Sort Button
if (btnSort) {
    btnSort.addEventListener('click', () => {
        const sorts = ["⏰ Lasted", "💸 Low To High", "💸 High To Low", "🆔 ID Ascending", "🆔 ID Descending"];
        openFilterModal(sorts, "sort");
    });
}

// Sort Options
if (sortOptions && sortOptions.children.length) {
    sortOptions.querySelectorAll('div').forEach(opt => {
        opt.addEventListener('click', () => {
            const sortType = opt.dataset.sort;
            const sorted = [...giftsData];
            
            switch (sortType) {
                case 'lasted': 
                    sorted.sort((a,b) => new Date(b.created_at || 0) - new Date(a.created_at || 0)); 
                    break;
                case 'low': 
                    sorted.sort((a,b) => (a.price || 0) - (b.price || 0)); 
                    break;
                case 'high': 
                    sorted.sort((a,b) => (b.price || 0) - (a.price || 0)); 
                    break;
                case 'idAsc': 
                    sorted.sort((a,b) => (a.id || 0) - (b.id || 0)); 
                    break;
                case 'idDesc': 
                    sorted.sort((a,b) => (b.id || 0) - (a.id || 0)); 
                    break;
            }
            
            renderGrid(sorted);
            sortOptions.style.display = 'none';

            if (giftBubbleBoard) {
                giftBubbleBoard.innerHTML = "";
                const bubble = document.createElement("div");
                bubble.className = "gift-bubble";
                bubble.textContent = `Sorted: ${opt.textContent}`;
                giftBubbleBoard.appendChild(bubble);
            }
        });
    });
}

// Grid Click Event
if (grid) {
    grid.addEventListener("click", e => {
        const card = e.target.closest(".card");
        if (!card) return;

        const nftId = card.dataset.id;
        const nft = giftsData.find(g => String(g.id) === nftId);
        if (!nft) return;

        // Update detail panel with NFT data
        if (detailImg) {
            detailImg.src = getPreviewImage(nft);
            detailImg.alt = formatNFTName(nft.name);
        }
        
        if (detailTitle) detailTitle.textContent = `${formatNFTName(nft.name)} #${nft.id}`;
        if (detailModel) detailModel.textContent = nft.model || "-";
        if (detailBg) detailBg.textContent = nft.bg || nft.background || "-";
        if (detailSymbol) detailSymbol.textContent = nft.symbol || "-";
        if (detailPrice) detailPrice.textContent = formatIDR(nft.price);

        // Generate Telegram links
        const baseUrl = "https://t.me/marketaldibot?start=";
        const slug = nft.name.replace(/\s+/g, "") + "_" + nft.id;
        
        if (btnBeli) {
            btnBeli.href = baseUrl + "beli_" + slug;
            btnBeli.textContent = "BELI";
        }
        
        if (btnNego) {
            btnNego.href = baseUrl + "nego_" + slug;
            btnNego.textContent = "NEGO";
        }

        openPanel();
    });
}

// Filter Overlay
if (filterOverlay) {
    filterOverlay.addEventListener("click", e => {
        if(e.target === filterOverlay) closeFilterModal();
    });
}

// Click Outside Dropdown
document.addEventListener("click", e => {
    if (giftSearchInput && !giftSearchInput.contains(e.target) && giftDropdown && !giftDropdown.contains(e.target)) {
        if (giftDropdown.style) {
            giftDropdown.style.display = "none";
        }
    }
});

// Button Prevent Default
document.querySelectorAll('button').forEach(btn => {
    btn.addEventListener('click', e => e.preventDefault());
});

// Close Panel Button
const closeBtn = document.getElementById("closePanel");
if (closeBtn) closeBtn.addEventListener("click", closePanel);

// Filter Inputs
[giftSearchInput, modelFilter, symbolFilter, bgFilter, maxPrice].forEach(el => {
    if(el && el.addEventListener) el.addEventListener("input", filterNFT);
});

// Search Button Event
if (document.getElementById("giftSearchBtn")) {
    document.getElementById("giftSearchBtn").addEventListener("click", filterNFT);
}

// ===== NEW FILTER PANEL EVENT LISTENERS =====
if (filterToggleBtn) {
    filterToggleBtn.addEventListener('click', openFilterPanel);
}

if (closeFilterPanel) {
    closeFilterPanel.addEventListener('click', closeFilterPanelFunc);
}

if (applyFilterBtn) {
    applyFilterBtn.addEventListener('click', applyFilters);
}

if (cancelFilterBtn) {
    cancelFilterBtn.addEventListener('click', resetFilters);
}

// Setup search for filter select boxes
if (giftSearchFilter && giftFilterSelect) {
    setupFilterSearch(giftSearchFilter, giftFilterSelect);
}

if (modelSearchFilter && modelFilterSelect) {
    setupFilterSearch(modelSearchFilter, modelFilterSelect);
}

if (symbolSearchFilter && symbolFilterSelect) {
    setupFilterSearch(symbolSearchFilter, symbolFilterSelect);
}

if (bgSearchFilter && bgFilterSelect) {
    setupFilterSearch(bgSearchFilter, bgFilterSelect);
}

// Close filter panel when clicking outside
if (filterPanel) {
    filterPanel.addEventListener('click', (e) => {
        if (e.target === filterPanel) {
            closeFilterPanelFunc();
        }
    });
}

// ===== PANEL DRAGGING (TOUCH) =====
let startY = 0, currentY = 0, isDragging = false;
if (panel) {
    panel.addEventListener("touchstart", e => {
        if (e.target.closest("a") || e.target.closest(".close-panel")) return;
        startY = e.touches[0].clientY;
        isDragging = true;
        panel.classList.add("dragging");
    });

    panel.addEventListener("touchmove", e => {
        if (!isDragging) return;
        e.preventDefault();
        currentY = e.touches[0].clientY;
        const diff = currentY - startY;
        if (diff > 0) panel.style.bottom = `-${diff}px`;
    });

    panel.addEventListener("touchend", e => {
        if (!isDragging) return;
        panel.classList.remove("dragging");
        const diff = currentY - startY;
        if (diff > 120) closePanel(); 
        else panel.style.bottom = "0";
        isDragging = false;
        startY = currentY = 0;
    });
}

// ===== INITIAL LOAD =====
fetch("export/data.json")
    .then(res => {
        if (!res.ok) {
            throw new Error(`HTTP error! status: ${res.status}`);
        }
        return res.json();
    })
    .then(data => {
        giftsData = Array.isArray(data) ? data : [];
        filteredGifts = [...giftsData];

        // Create gift list without numbers
        const set = new Set();
        giftsData.forEach(g => {
            const giftName = g.name.replace(/ #\d+$/, '');
            if (giftName) set.add(giftName);
        });
        giftList = Array.from(set);

        renderGrid(giftsData);
        buildBubbles();
        populateFilterOptions();
        
        // Hide old filter buttons if they exist
        if (btnAllGifts) btnAllGifts.style.display = 'none';
        if (btnAllModels) btnAllModels.style.display = 'none';
        if (btnAllSymbols) btnAllSymbols.style.display = 'none';
        if (btnAllBackdrops) btnAllBackdrops.style.display = 'none';
        
        if (pageLoader) {
            pageLoader.classList.add("hide");
        }
    })
    .catch(err => {
        console.error("FETCH ERROR:", err);
        
        // Show error message in grid
        if (grid) {
            grid.innerHTML = `
                <div style="grid-column: 1 / -1; text-align: center; padding: 3rem; color: var(--accent);">
                    <h3>⚠️ Gagal Memuat Data</h3>
                    <p>Periksa koneksi internet Anda atau file data.json</p>
                    <button onclick="location.reload()" style="
                        margin-top: 1rem;
                        padding: 0.75rem 1.5rem;
                        background: var(--gradient);
                        border: none;
                        border-radius: var(--radius);
                        color: var(--darker);
                        font-weight: bold;
                        cursor: pointer;
                    ">
                        Coba Lagi
                    </button>
                </div>
            `;
        }
        
        if (pageLoader) {
            pageLoader.classList.add("hide");
        }
    });

// ===== UTILITY FUNCTIONS =====
// Function to handle Enter key in search input
if (giftSearchInput) {
    giftSearchInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            filterNFT();
        }
    });
}

// Function to clear all filters
window.clearAllFilters = function() {
    resetFilters();
};

// Function to show all gifts
window.showAllGifts = function() {
    if (giftSearchInput) giftSearchInput.value = "";
    resetFilters();
    filterNFT();
};
