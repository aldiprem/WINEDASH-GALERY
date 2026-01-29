// ===== VARIABLES =====
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
const btnSort = document.getElementById("btnSort");
const sortOptions = document.getElementById("sortOptions");
const maxPrice = document.getElementById("maxPrice");
const loaderStatus = document.getElementById("loaderStatus");

let giftsData = [];
let cards = [];
let giftList = [];
let selectedGifts = new Set();

// ===== LOADER FUNCTIONS =====
function updateLoaderStatus(text) {
  if (loaderStatus) {
    loaderStatus.innerHTML = text;
  }
  console.log("Loader:", text);
}

// ===== BASIC FUNCTIONS =====
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
  document.body.style.overflow = '';
}

function getPreviewImage(nft) {
  if (nft.image && nft.image.includes("/previews/")) {
    return nft.image;
  }
  return `previews/${nft.slug || 'default'}.jpg`;
}

// ===== RENDER GRID - SIMPLE VERSION =====
function renderGrid(data) {
  console.log("Rendering grid with", data.length, "items");
  updateLoaderStatus(`Rendering ${data.length} gifts...`);
  
  grid.innerHTML = "";
  
  if (!data || data.length === 0) {
    grid.innerHTML = '<p style="color:#ccc; text-align:center; padding:40px;">No gifts found</p>';
    cards = [];
    return;
  }
  
  // Render langsung tanpa batch untuk simplicity
  data.forEach((nft, index) => {
    const div = document.createElement("div");
    div.className = "card";
    div.dataset.id = String(nft.id);
    div.dataset.name = (nft.name || "").toLowerCase();
    div.dataset.slug = (nft.slug || "").toLowerCase();
    div.dataset.price = nft.price || 0;
    
    const nftName = formatNFTName(nft.name || "Unnamed");
    const price = formatIDR(nft.price);
    
    div.innerHTML = `
      <a href="https://t.me/nft/${nft.slug || nft.id}" target="_blank">
        <img src="${getPreviewImage(nft)}" alt="${nftName}" 
             onerror="this.src='https://via.placeholder.com/300?text=No+Preview'">
      </a>
      <h3>${nftName}</h3>
      <p>#${nft.id}</p>
      <span class="price open-panel">💰 ${price}</span>
    `;
    
    // Event listener untuk detail panel
    div.querySelector(".open-panel").addEventListener("click", (e) => {
      e.preventDefault();
      openNFTDetailPanel(nft);
    });
    
    grid.appendChild(div);
  });
  
  cards = document.querySelectorAll(".card");
  
  // Hide loader setelah render selesai
  setTimeout(() => {
    pageLoader.classList.add("hide");
    updateLoaderStatus("Ready!");
    console.log("Grid rendered with", cards.length, "cards");
  }, 500);
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

// ===== LOAD DATA - SIMPLE VERSION =====
function loadData() {
  updateLoaderStatus("Loading data...");
  
  // Timeout 10 detik
  const timeout = setTimeout(() => {
    showError("Loading timeout. Check console for details.");
  }, 10000);
  
  fetch("export/data.json")
    .then(res => {
      clearTimeout(timeout);
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${res.statusText}`);
      }
      return res.json();
    })
    .then(data => {
      console.log("✅ Data loaded:", data.length, "items");
      
      if (!Array.isArray(data)) {
        throw new Error("Data is not an array");
      }
      
      giftsData = data;
      
      // Create gift list
      const set = new Set();
      data.forEach(g => {
        if (g && g.name) {
          const baseName = g.name.replace(/ #\d+$/, '').trim();
          if (baseName) set.add(baseName);
        }
      });
      giftList = Array.from(set);
      
      renderGrid(data);
    })
    .catch(err => {
      clearTimeout(timeout);
      console.error("❌ Fetch error:", err);
      showError(err.message);
    });
}

function showError(message) {
  console.error("Error:", message);
  grid.innerHTML = `
    <div style="text-align:center; padding:40px; color:#ff6b6b;">
      <h3>⚠️ Error</h3>
      <p>${message}</p>
      <button onclick="location.reload()" style="
        margin-top:20px;
        padding:10px 20px;
        background:#7cf9ff;
        color:#000;
        border:none;
        border-radius:8px;
        cursor:pointer;
      ">Refresh</button>
    </div>
  `;
  pageLoader.classList.add("hide");
}

// ===== FILTER FUNCTIONS =====
function filterNFT() {
  if (cards.length === 0) return;
  
  const searchText = giftSearchInput.value.toLowerCase().trim();
  const max = maxPrice.value ? parseFloat(maxPrice.value) : Infinity;
  
  cards.forEach(card => {
    let show = true;
    const cardName = card.dataset.name || "";
    const cardPrice = parseFloat(card.dataset.price) || 0;
    
    if (searchText && !cardName.includes(searchText)) show = false;
    
    if (selectedGifts.size > 0) {
      let matched = false;
      selectedGifts.forEach(gift => {
        if (cardName.includes(gift.toLowerCase())) matched = true;
      });
      if (!matched) show = false;
    }
    
    if (cardPrice > max) show = false;
    
    card.style.display = show ? "block" : "none";
  });
}

function addGiftBubble(gift) {
  if (selectedGifts.has(gift)) return;
  selectedGifts.add(gift);
  
  const bubble = document.createElement("div");
  bubble.className = "gift-bubble";
  bubble.textContent = gift + " ×";
  bubble.addEventListener("click", () => {
    selectedGifts.delete(gift);
    bubble.remove();
    filterNFT();
  });
  
  if (giftSelected) {
    giftSelected.appendChild(bubble);
  }
  
  giftSearchInput.value = "";
  giftDropdown.style.display = "none";
  filterNFT();
}

// ===== EVENT LISTENERS =====
overlay.addEventListener("click", closePanel);

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

if (btnSort && sortOptions) {
  btnSort.addEventListener("click", () => {
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
}

document.addEventListener('click', (e) => {
  // Close dropdowns
  if (sortOptions && !sortOptions.contains(e.target) && btnSort && !btnSort.contains(e.target)) {
    sortOptions.style.display = "none";
  }
  
  if (!giftSearchInput.contains(e.target) && !giftDropdown.contains(e.target)) {
    giftDropdown.style.display = "none";
  }
});

if (giftSearchInput) giftSearchInput.addEventListener("input", filterNFT);
if (maxPrice) maxPrice.addEventListener("input", filterNFT);

// Close panel button
const closeBtn = document.getElementById("closePanel");
if (closeBtn) {
  closeBtn.addEventListener("click", closePanel);
}

// Scroll to top
window.addEventListener("scroll", () => {
  if (window.scrollY > 500) {
    scrollTopBtn.classList.add("show");
  } else {
    scrollTopBtn.classList.remove("show");
  }
});

if (scrollTopBtn) {
  scrollTopBtn.addEventListener("click", () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  });
}

// ===== INITIALIZE =====
document.addEventListener('DOMContentLoaded', function() {
  console.log("DOM Ready - Starting app...");
  updateLoaderStatus("Starting app...");
  
  // Start loading data
  setTimeout(() => {
    loadData();
  }, 100);
});
