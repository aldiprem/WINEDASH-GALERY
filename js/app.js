// ===== VARIABLES & DOM ELEMENTS =====
const giftFilter = document.getElementById("giftFilter");
const modelFilter = document.getElementById("modelFilter") || { value: "" };
const symbolFilter = document.getElementById("symbolFilter") || { value: "" };
const bgFilter = document.getElementById("bgFilter") || { value: "" };
const maxPrice = document.getElementById("maxPrice");
const grid = document.getElementById("giftGrid");
const giftSearchInput = document.getElementById("giftSearchInput");
const giftDropdown = document.getElementById("giftDropdown");
const giftSelected = document.getElementById("giftSelected");
const panel = document.getElementById("giftDetailPanel");
const overlay = document.getElementById("panelOverlay");
const btnBeli = document.getElementById("btnBeli");
const btnNego = document.getElementById("btnNego");
const pageLoader = document.getElementById("pageLoader");
const scrollTopBtn = document.getElementById("scrollTopBtn");
const btnAllGifts = document.getElementById("btnAllGifts");
const btnAllModels = document.getElementById("btnAllModels");
const btnAllSymbols = document.getElementById("btnAllSymbols");
const btnAllBackdrops = document.getElementById("btnAllBackdrops");
const sortOptions = document.getElementById("sortOptions");
const subFilters = document.getElementById("subFilters");
const loaderStatus = document.getElementById("loaderStatus");

// ===== GLOBAL VARIABLES =====
let giftsData = [];
let cards = [];
let giftList = [];
let filteredGifts = [];
let selectedGifts = new Set();
let selectedGift = null;
let allGiftsDropdown = null;
let isAllGiftsOpen = false;
let fetchTimeout = null;
let loadStartTime = null;

// ===== LOADER STATUS FUNCTIONS =====
function updateLoaderStatus(text) {
  if (loaderStatus) {
    loaderStatus.innerHTML = text;
  }
  console.log("Loader:", text);
}

function showLoaderTime() {
  if (loadStartTime) {
    const loadTime = Date.now() - loadStartTime;
    updateLoaderStatus(`Loaded in ${loadTime}ms`);
  }
}

// ===== UTILITY FUNCTIONS =====
function formatIDR(number) {
  return "Rp" + Number(number || 0).toLocaleString("id-ID");
}

function formatNFTName(name) {
  if (!name) return "";
  return name.replace(/[\s#_-]*\d+$/g, "").trim();
}

function openPanel() {
  panel.classList.add("active");
  overlay.classList.add("active");
  document.body.style.overflow = 'hidden';
}

function closePanel() {
  panel.classList.remove("active");
  overlay.classList.remove("active");
  panel.style.bottom = "";
  document.body.style.overflow = '';
}

function getPreviewImage(nft) {
  if (nft.image && nft.image.includes("/previews/")) {
    return nft.image;
  }
  return `previews/${nft.slug || 'default'}.jpg`;
}

// ===== RENDER FUNCTIONS =====
function renderGrid(data) {
  console.time("renderGrid");
  updateLoaderStatus(`Rendering ${data.length} items...`);
  
  grid.innerHTML = "";
  
  if (!data || data.length === 0) {
    grid.innerHTML = '<p style="color:#ccc; text-align:center; padding:40px;">No gifts found</p>';
    cards = [];
    console.timeEnd("renderGrid");
    return;
  }
  
  // Gunakan DocumentFragment untuk performa lebih baik
  const fragment = document.createDocumentFragment();
  const batchSize = 50; // Render dalam batch untuk menghindari blocking UI
  let renderedCount = 0;
  
  function renderBatch(startIndex) {
    const endIndex = Math.min(startIndex + batchSize, data.length);
    
    for (let i = startIndex; i < endIndex; i++) {
      const nft = data[i];
      if (!nft || !nft.id) continue;
      
      const div = document.createElement("div");
      div.className = "card";
      div.dataset.id = String(nft.id);
      div.dataset.name = (nft.name || "").toLowerCase();
      div.dataset.slug = (nft.slug || "").toLowerCase();
      div.dataset.model = nft.model || "";
      div.dataset.symbol = nft.symbol || "";
      div.dataset.bg = nft.bg || "";
      div.dataset.price = nft.price || 0;

      const nftName = formatNFTName(nft.name || "Unnamed");
      const price = formatIDR(nft.price);
      
      div.innerHTML = `
        <a href="https://t.me/nft/${nft.slug || nft.id}" target="_blank">
          <img src="${getPreviewImage(nft)}" alt="${nftName}" 
               loading="lazy"
               onerror="this.src='https://via.placeholder.com/300?text=No+Preview'; this.onerror=null;">
        </a>
        <h3>${nftName}</h3>
        <p>#${nft.id}</p>
        <span class="price open-panel">💰 ${price}</span>
      `;
      
      // Event listener untuk panel detail
      div.querySelector(".open-panel").addEventListener("click", (e) => {
        e.stopPropagation();
        e.preventDefault();
        openNFTDetailPanel(nft);
      });
      
      fragment.appendChild(div);
      renderedCount++;
    }
    
    // Update progress
    if (loaderStatus) {
      loaderStatus.innerHTML = `Rendering... ${renderedCount}/${data.length}`;
    }
    
    // Jika masih ada item, render batch berikutnya di next frame
    if (endIndex < data.length) {
      requestAnimationFrame(() => renderBatch(endIndex));
    } else {
      // Semua item selesai di-render
      grid.appendChild(fragment);
      cards = document.querySelectorAll(".card");
      console.timeEnd("renderGrid");
      console.log(`✅ Rendered ${renderedCount} items`);
      
      // Hide loader setelah delay kecil
      setTimeout(() => {
        pageLoader.classList.add("hide");
        showLoaderTime();
        updateLoaderStatus("Ready!");
      }, 300);
    }
  }
  
  // Mulai render batch pertama
  renderBatch(0);
}

function openNFTDetailPanel(nft) {
  document.getElementById("detailImg").src = getPreviewImage(nft);
  document.getElementById("detailTitle").textContent = `${formatNFTName(nft.name || "")} #${nft.id}`;
  document.getElementById("detailModel").textContent = nft.model || "-";
  document.getElementById("detailBg").textContent = nft.bg || "-";
  document.getElementById("detailSymbol").textContent = nft.symbol || "-";
  document.getElementById("detailPrice").textContent = formatIDR(nft.price);

  const baseUrl = "https://t.me/marketaldibot?start=";
  const slug = (nft.name || "").replace(/\s+/g, "") + "_" + nft.id;
  btnBeli.href = baseUrl + "beli_" + slug;
  btnNego.href = baseUrl + "nego_" + slug;

  openPanel();
}

// ===== ALL GIFTS DROPDOWN =====
function createAllGiftsDropdown() {
  // Hapus dropdown lama jika ada
  if (allGiftsDropdown) {
    allGiftsDropdown.remove();
  }
  
  // Buat dropdown baru
  allGiftsDropdown = document.createElement("div");
  allGiftsDropdown.className = "all-gifts-dropdown";
  
  // Hitung jumlah per slug
  const counts = {};
  giftsData.forEach(g => {
    if (g.slug) {
      counts[g.slug] = (counts[g.slug] || 0) + 1;
    }
  });
  
  // Tambahkan item ke dropdown
  Object.entries(counts).forEach(([slug, count]) => {
    const item = document.createElement("div");
    item.className = "gift-dropdown-item";
    item.innerHTML = `
      <span class="gift-name">${slug}</span>
      <span class="gift-count">(${count})</span>
    `;
    item.addEventListener("click", () => {
      addGiftBubble(slug);
      closeAllGiftsDropdown();
    });
    allGiftsDropdown.appendChild(item);
  });
  
  // Tambahkan ke body
  document.body.appendChild(allGiftsDropdown);
  
  // Posisikan di bawah tombol All Gifts
  const btnRect = btnAllGifts.getBoundingClientRect();
  allGiftsDropdown.style.position = "fixed";
  allGiftsDropdown.style.top = `${btnRect.bottom + window.scrollY}px`;
  allGiftsDropdown.style.left = `${btnRect.left}px`;
  allGiftsDropdown.style.width = `${btnRect.width}px`;
  allGiftsDropdown.style.maxHeight = "300px";
  allGiftsDropdown.style.overflowY = "auto";
  allGiftsDropdown.style.display = "block";
  
  isAllGiftsOpen = true;
}

function closeAllGiftsDropdown() {
  if (allGiftsDropdown) {
    allGiftsDropdown.remove();
    allGiftsDropdown = null;
  }
  isAllGiftsOpen = false;
}

// ===== EVENT LISTENERS =====
overlay.addEventListener("click", closePanel);

window.addEventListener("scroll", () => {
  const card = document.querySelector(".card");
  if (!card) return;

  const cardHeight = card.offsetHeight;
  const threshold = cardHeight * 3;

  if (window.scrollY > threshold) {
    scrollTopBtn.classList.add("show");
  } else {
    scrollTopBtn.classList.remove("show");
  }
});

scrollTopBtn.addEventListener("click", () => {
  window.scrollTo({
    top: 0,
    behavior: "smooth"
  });
});

// Gift search input
giftSearchInput.addEventListener("input", () => {
  const val = giftSearchInput.value.toLowerCase();
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
});

// All Gifts button
btnAllGifts.addEventListener('click', (e) => {
  e.stopPropagation();
  
  if (isAllGiftsOpen) {
    closeAllGiftsDropdown();
  } else {
    createAllGiftsDropdown();
  }
});

// Subfilter buttons
btnAllModels.addEventListener('click', () => {
  const models = [...new Set(giftsData.map(g => g.model).filter(Boolean))];
  alert("Available Models:\n" + models.join("\n"));
});

btnAllSymbols.addEventListener('click', () => {
  const symbols = [...new Set(giftsData.map(g => g.symbol).filter(Boolean))];
  alert("Available Symbols:\n" + symbols.join("\n"));
});

btnAllBackdrops.addEventListener('click', () => {
  const bgs = [...new Set(giftsData.map(g => g.bg).filter(Boolean))];
  alert("Available Backdrops:\n" + bgs.join("\n"));
});

// Sort functionality
btnSort.addEventListener('click', (e) => {
  e.stopPropagation();
  sortOptions.style.display = sortOptions.style.display === 'block' ? 'none' : 'block';
});

sortOptions.querySelectorAll('div').forEach(opt => {
  opt.addEventListener('click', () => {
    const sortType = opt.dataset.sort;
    let sorted = [...giftsData];

    switch (sortType) {
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
    }

    renderGrid(sorted);
    sortOptions.style.display = 'none';
  });
});

// Close dropdowns when clicking outside
document.addEventListener('click', (e) => {
  // Close All Gifts dropdown
  if (allGiftsDropdown && !allGiftsDropdown.contains(e.target) && !btnAllGifts.contains(e.target)) {
    closeAllGiftsDropdown();
  }
  
  // Close sort dropdown
  if (sortOptions && !sortOptions.contains(e.target) && !btnSort.contains(e.target)) {
    sortOptions.style.display = "none";
  }
  
  // Close gift search dropdown
  if (!giftSearchInput.contains(e.target) && !giftDropdown.contains(e.target)) {
    giftDropdown.style.display = "none";
  }
});

// ===== DATA LOADING FUNCTIONS =====
function showError(message) {
  console.error("Error:", message);
  grid.innerHTML = `
    <div style="text-align:center; padding:40px; color:#ff6b6b;">
      <h3>⚠️ Error Loading Data</h3>
      <p style="margin:10px 0; color:#ccc;">${message}</p>
      <p style="font-size:12px; color:#888; margin:20px 0;">
        Check: export/data.json file exists and has valid JSON format
      </p>
      <button onclick="location.reload()" style="
        margin-top:10px;
        padding:10px 20px;
        background:linear-gradient(135deg, #7cf9ff, #9b7bff);
        color:#000;
        border:none;
        border-radius:8px;
        cursor:pointer;
        font-weight:bold;
        transition:transform 0.2s;
      " onmouseover="this.style.transform='scale(1.05)'" 
       onmouseout="this.style.transform='scale(1)'">
        🔄 Refresh Page
      </button>
    </div>
  `;
  pageLoader.classList.add("hide");
}

function loadData() {
  loadStartTime = Date.now();
  updateLoaderStatus("Starting data load...");
  
  // Set timeout 15 detik untuk data loading
  fetchTimeout = setTimeout(() => {
    updateLoaderStatus("Timeout - Checking connection...");
    showError("Loading timeout (15s). Data file might be too large or network issue.");
    console.error("⏰ Fetch timeout after 15 seconds");
  }, 15000);

  // Tambah timestamp untuk cache busting
  const url = `export/data.json?t=${Date.now()}`;
  console.log("📡 Fetching from:", url);
  
  fetch(url, {
    cache: 'no-cache',
    headers: {
      'Accept': 'application/json',
      'Cache-Control': 'no-cache'
    }
  })
    .then(res => {
      clearTimeout(fetchTimeout);
      
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${res.statusText}`);
      }
      
      updateLoaderStatus("Parsing JSON data...");
      return res.json();
    })
    .then(data => {
      clearTimeout(fetchTimeout);
      
      if (!Array.isArray(data)) {
        throw new Error("Data is not a valid array");
      }
      
      console.log(`✅ Data loaded: ${data.length} items`);
      updateLoaderStatus(`Processing ${data.length} gifts...`);
      
      giftsData = data;
      filteredGifts = [...giftsData];

      // Create gift list from unique names
      const set = new Set();
      giftsData.forEach(g => {
        if (g && g.name) {
          const baseName = g.name.replace(/ #\d+$/, '').trim();
          if (baseName) set.add(baseName);
        }
      });
      giftList = Array.from(set);
      
      console.log(`📋 Unique gift names: ${giftList.length}`);
      updateLoaderStatus(`Found ${giftList.length} unique gift types`);
      
      // Render grid with progressive loading
      renderGrid(giftsData);
    })
    .catch(err => {
      clearTimeout(fetchTimeout);
      console.error("❌ FETCH ERROR:", err);
      
      let errorMsg = "";
      if (err.message.includes("HTTP 404")) {
        errorMsg = "File 'export/data.json' not found.";
      } else if (err.message.includes("Unexpected token")) {
        errorMsg = "Invalid JSON format in data.json";
      } else if (err.message.includes("NetworkError")) {
        errorMsg = "Network error. Check connection.";
      } else if (err.message.includes("Failed to fetch")) {
        errorMsg = "Cannot fetch data. Check if server is running.";
      } else {
        errorMsg = err.message;
      }
      
      showError(errorMsg);
    });
}

// ===== FILTER FUNCTIONS =====
function addGiftBubble(gift) {
  if (selectedGifts.has(gift)) return;
  selectedGifts.add(gift);

  const bubble = document.createElement("div");
  bubble.className = "gift-bubble";
  bubble.innerHTML = `
    ${gift}
    <span class="remove-bubble" title="Remove">×</span>
  `;
  
  bubble.addEventListener("click", (e) => {
    if (e.target.classList.contains("remove-bubble") || e.target === bubble) {
      selectedGifts.delete(gift);
      bubble.remove();
      filterNFT();
    }
  });

  if (giftSelected) {
    giftSelected.appendChild(bubble);
  }
  
  giftSearchInput.value = "";
  giftDropdown.style.display = "none";
  filterNFT();
}

function filterNFT() {
  if (cards.length === 0) return;
  
  const searchText = giftSearchInput.value.toLowerCase().trim();
  const model = modelFilter.value;
  const symbol = symbolFilter.value;
  const bg = bgFilter.value;
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

// Add event listeners for filtering
const filterElements = [
  giftSearchInput,
  modelFilter,
  symbolFilter,
  bgFilter,
  maxPrice
].filter(el => el !== null && el !== undefined);

filterElements.forEach(el => {
  el.addEventListener("input", filterNFT);
});

// ===== PANEL DRAG FUNCTIONALITY =====
let startY = 0;
let currentY = 0;
let isDragging = false;

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
  if (diff > 0) {
    panel.style.bottom = `-${diff}px`;
  }
});

panel.addEventListener("touchend", e => {
  if (!isDragging) return;
  panel.classList.remove("dragging");
  const diff = currentY - startY;
  if (diff > 120) closePanel();
  else panel.style.bottom = "0";

  isDragging = false;
  startY = 0;
  currentY = 0;
});

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', function() {
  console.log("🚀 DOM Ready - Initializing...");
  updateLoaderStatus("Initializing app...");
  
  // Start loading data
  setTimeout(() => {
    loadData();
  }, 100);
});

// Close panel button
const closeBtn = document.getElementById("closePanel");
if (closeBtn) {
  closeBtn.addEventListener("click", closePanel);
}

// Prevent zoom on mobile
document.addEventListener('touchmove', function (e) {
  if (e.scale !== 1) { 
    e.preventDefault(); 
  }
}, { passive: false });

// Add window error handler
window.addEventListener('error', function(e) {
  console.error('Global error:', e.error);
  updateLoaderStatus("Error occurred - check console");
});
