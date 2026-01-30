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
    return name.replace(/[\s#_-]*\d+$/g, "").trim();
}

function getPreviewImage(nft) {
    if (nft.image && nft.image.includes("/previews/")) return nft.image;
    return `previews/${nft.slug}.jpg`;
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
        
        div.innerHTML = `
            <a href="https://t.me/nft/${nft.slug}" target="_blank">
                <img src="${getPreviewImage(nft)}" alt="${formatNFTName(nft.name)}" 
                     onerror="this.src='https://via.placeholder.com/300?text=No+Preview'">
            </a>
            <h3>${formatNFTName(nft.name)}</h3>
            <p>#${nft.id}</p>
            <span class="price">💰 ${formatIDR(nft.price)}</span>
        `;
        grid.appendChild(div);
    });

    cards = Array.from(document.querySelectorAll(".card"));
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

        if (searchText && !cardName.includes(searchText)) show = false;

        if (selectedGifts.size > 0) {
            let matched = false;
            selectedGifts.forEach(gift => {
                if (cardName.includes(gift.toLowerCase())) matched = true;
            });
            if (!matched) show = false;
        }

        if (model && cardModel !== model) show = false;
        if (symbol && cardSymbol !== symbol) show = false;
        if (bg && cardBg !== bg) show = false;
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

    btnAllModels.innerHTML = 'All Models ⬇<br>' + models.join('<br>');
    btnAllSymbols.innerHTML = 'All Symbols ⬇<br>' + symbols.join('<br>');
    btnAllBackdrops.innerHTML = 'All Backdrops ⬇<br>' + bgs.join('<br>');
}

// ===== GIFT BUBBLE FUNCTIONS =====
function addGiftBubble(gift) {
    if (selectedGifts.has(gift)) return;
    selectedGifts.add(gift);

    const nft = giftsData.find(g => g.name.replace(/ #\d+$/, '') === gift);
    const priceText = nft ? ` 💰 ${formatIDR(nft.price)}` : "";

    const bubble = document.createElement("div");
    bubble.className = "gift-bubble";
    bubble.textContent = gift + priceText;
    bubble.addEventListener("click", () => {
        selectedGifts.delete(gift);
        bubble.remove();
        filterNFT();
        updateSubFiltersForSelectedGifts();
    });

    giftSelected.appendChild(bubble);
    giftSearchInput.value = "";
    giftDropdown.style.display = "none";
    filterNFT();
    updateSubFiltersForSelectedGifts();
}

function createBubble(name, count = "", type = "gift") {
    const bubble = document.createElement("div");
    bubble.className = "gift-bubble";
    bubble.textContent = count ? `${name} (${count})` : name;

    bubble.addEventListener("click", () => {
        switch (type) {
            case "gift":
                addGiftBubble(name);
                break;
            case "model":
                modelFilter.value = name;
                filterNFT();
                break;
            case "symbol":
                symbolFilter.value = name;
                filterNFT();
                break;
            case "bg":
                bgFilter.value = name;
                filterNFT();
                break;
        }
    });

    return bubble;
}

function buildBubbles() {
    if (!giftBubbleBoard) return;
    
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

// ===== FILTER MODAL FUNCTIONS =====
function openFilterModal(items, type) {
    if (!filterBubbleBoard) return;
    
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
            sorted.sort((a,b) => new Date(b.created_at) - new Date(a.created_at)); 
            break;
        case 'low': 
            sorted.sort((a,b) => a.price - b.price); 
            break;
        case 'high': 
            sorted.sort((a,b) => b.price - a.price); 
            break;
        case 'idAsc': 
            sorted.sort((a,b) => a.id - b.id); 
            break;
        case 'idDesc': 
            sorted.sort((a,b) => b.id - a.id); 
            break;
    }
    renderGrid(sorted);
}

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
        giftDropdown.innerHTML = "";
        
        if (!val) { 
            if (giftDropdown.style) {
                giftDropdown.style.display = "none"; 
            }
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

        if (giftDropdown.style) {
            giftDropdown.style.display = filtered.length ? "block" : "none";
        }
    });
}

// Filter Buttons
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
                    sorted.sort((a,b) => new Date(b.created_at) - new Date(a.created_at)); 
                    break;
                case 'low': 
                    sorted.sort((a,b) => a.price - b.price); 
                    break;
                case 'high': 
                    sorted.sort((a,b) => b.price - a.price); 
                    break;
                case 'idAsc': 
                    sorted.sort((a,b) => a.id - b.id); 
                    break;
                case 'idDesc': 
                    sorted.sort((a,b) => b.id - a.id); 
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

        const detailImg = document.getElementById("detailImg");
        const detailTitle = document.getElementById("detailTitle");
        const detailModel = document.getElementById("detailModel");
        const detailBg = document.getElementById("detailBg");
        const detailSymbol = document.getElementById("detailSymbol");
        const detailPrice = document.getElementById("detailPrice");

        if (detailImg) detailImg.src = getPreviewImage(nft);
        if (detailTitle) detailTitle.textContent = `${formatNFTName(nft.name)} #${nft.id}`;
        if (detailModel) detailModel.textContent = nft.model || "-";
        if (detailBg) detailBg.textContent = nft.bg || "-";
        if (detailSymbol) detailSymbol.textContent = nft.symbol || "-";
        if (detailPrice) detailPrice.textContent = formatIDR(nft.price);

        const baseUrl = "https://t.me/marketaldibot?start=";
        const slug = nft.name.replace(/\s+/g, "") + "_" + nft.id;
        if (btnBeli.href) btnBeli.href = baseUrl + "beli_" + slug;
        if (btnNego.href) btnNego.href = baseUrl + "nego_" + slug;

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
    .then(res => res.json())
    .then(data => {
        giftsData = data;
        filteredGifts = [...giftsData];

        const set = new Set();
        giftsData.forEach(g => set.add(g.name.replace(/ #\d+$/, '')));
        giftList = Array.from(set);

        renderGrid(giftsData);
        buildBubbles();
        if (pageLoader) pageLoader.classList.add("hide");
    })
    .catch(err => {
        console.error("FETCH ERROR:", err);
        grid.innerHTML = "<p style='color:red'>Gagal load data</p>";
        if (pageLoader) pageLoader.classList.add("hide");
    });
