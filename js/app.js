const giftFilter = document.getElementById("giftFilter");
const modelFilter = document.getElementById("modelFilter");
const symbolFilter = document.getElementById("symbolFilter");
const bgFilter = document.getElementById("bgFilter");
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
const giftSearchBtn = document.getElementById("giftSearchBtn");

overlay.addEventListener("click", closePanel);

let giftsData = [];
let cards = [];
let giftList = [];
let filteredGifts = [];
let selectedGifts = new Set();
let selectedGift = null;

// Variabel untuk dropdown All Gifts
let allGiftsDropdown = null;
let isAllGiftsOpen = false;

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
  document.body.style.overflow = 'hidden'; // Mencegah scroll
}

function closePanel() {
  panel.classList.remove("active");
  overlay.classList.remove("active");
  panel.style.bottom = "";
  document.body.style.overflow = ''; // Kembalikan scroll
}

function getPreviewImage(nft) {
  if (nft.image && nft.image.includes("/previews/")) {
    return nft.image;
  }
  return `previews/${nft.slug}.jpg`;
}

function renderGrid(data) {
  grid.innerHTML = "";
  if (!data || data.length === 0) {
    grid.innerHTML = '<p style="color:#ccc; text-align:center; padding:40px;">No gifts found</p>';
    cards = [];
    return;
  }
  
  data.forEach(nft => {
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
      <a href="https://t.me/nft/${nft.slug}" target="_blank">
        <img src="${getPreviewImage(nft)}" alt="${nftName}" onerror="this.src='https://via.placeholder.com/300?text=No+Preview'">
      </a>
      <h3>${nftName}</h3>
      <p>#${nft.id}</p>
      <span class="price open-panel">💰 ${price}</span>
    `;
    
    grid.appendChild(div);

    div.querySelector(".open-panel").addEventListener("click", (e) => {
      e.stopPropagation();
      e.preventDefault();
      document.getElementById("detailImg").src = getPreviewImage(nft);
      document.getElementById("detailTitle").textContent = `${nftName} #${nft.id}`;
      document.getElementById("detailModel").textContent = nft.model || "-";
      document.getElementById("detailBg").textContent = nft.bg || "-";
      document.getElementById("detailSymbol").textContent = nft.symbol || "-";
      document.getElementById("detailPrice").textContent = formatIDR(nft.price);

      const baseUrl = "https://t.me/marketaldibot?start=";
      const slug = (nft.name || "").replace(/\s+/g, "") + "_" + nft.id;
      btnBeli.href = baseUrl + "beli_" + slug;
      btnNego.href = baseUrl + "nego_" + slug;

      openPanel();
    });
  });
  
  cards = document.querySelectorAll(".card");
}

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

// Fungsi untuk membuat dropdown All Gifts
function createAllGiftsDropdown() {
  // Hapus dropdown yang lama jika ada
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
    item.innerHTML = `<span class="gift-name">${slug}</span> <span class="gift-count">(${count})</span>`;
    item.addEventListener("click", () => {
      // Tambahkan bubble dan search
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

// Event listener untuk All Gifts
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
  alert("Models:\n" + models.join("\n"));
});

btnAllSymbols.addEventListener('click', () => {
  const symbols = [...new Set(giftsData.map(g => g.symbol).filter(Boolean))];
  alert("Symbols:\n" + symbols.join("\n"));
});

btnAllBackdrops.addEventListener('click', () => {
  const bgs = [...new Set(giftsData.map(g => g.bg).filter(Boolean))];
  alert("Backdrops:\n" + bgs.join("\n"));
});

// Search input
giftSearchInput.addEventListener("input", () => {
  const val = giftSearchInput.value.toLowerCase();
  giftDropdown.innerHTML = "";

  if (!val) { 
    giftDropdown.style.display = "none"; 
    return; 
  }

  const filtered = giftList.filter(g => g.toLowerCase().includes(val) && !selectedGifts.has(g));
  filtered.forEach(g => {
    const div = document.createElement("div");
    div.textContent = g;
    div.addEventListener("click", () => addGiftBubble(g));
    giftDropdown.appendChild(div);
  });

  giftDropdown.style.display = filtered.length ? "block" : "none";
});

// Search button
if (giftSearchBtn) {
  giftSearchBtn.addEventListener("click", () => {
    filterNFT();
  });
}

// Sort functionality
document.addEventListener('click', (e) => {
  // Tutup dropdown All Gifts jika klik di luar
  if (allGiftsDropdown && !allGiftsDropdown.contains(e.target) && !btnAllGifts.contains(e.target)) {
    closeAllGiftsDropdown();
  }
  
  // Tutup sort dropdown jika klik di luar
  if (sortOptions && !sortOptions.contains(e.target) && !btnSort.contains(e.target)) {
    sortOptions.style.display = "none";
  }
});

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

// Load data
fetch("export/data.json")
  .then(res => {
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  })
  .then(data => {
    console.log("Data loaded:", data.length, "items");
    
    giftsData = data;
    filteredGifts = [...giftsData];

    const set = new Set();
    giftsData.forEach(g => {
      if (g && g.name) {
        set.add(g.name.replace(/ #\d+$/, '').trim());
      }
    });
    giftList = Array.from(set);

    renderGrid(giftsData);
    setTimeout(() => {
      pageLoader.classList.add("hide");
    }, 500);
  })
  .catch(err => {
    console.error("FETCH ERROR:", err);
    grid.innerHTML = "<p style='color:red; padding:20px; text-align:center;'>Gagal load data. Pastikan file export/data.json ada.</p>";
    setTimeout(() => pageLoader.classList.add("hide"), 500);
  });

function addGiftBubble(gift) {
  if (selectedGifts.has(gift)) return;
  selectedGifts.add(gift);

  const bubble = document.createElement("div");
  bubble.className = "gift-bubble";
  bubble.innerHTML = `${gift} <span class="remove-bubble">×</span>`;
  
  bubble.addEventListener("click", (e) => {
    if (e.target.classList.contains("remove-bubble") || e.target === bubble) {
      selectedGifts.delete(gift);
      bubble.remove();
      filterNFT();
    }
  });

  giftSelected.appendChild(bubble);
  giftSearchInput.value = "";
  giftDropdown.style.display = "none";

  filterNFT();
}

document.addEventListener("click", e => {
  if (!giftSearchInput.contains(e.target) && !giftDropdown.contains(e.target)) {
    giftDropdown.style.display = "none";
  }
});

const closeBtn = document.getElementById("closePanel");
if (closeBtn) {
  closeBtn.addEventListener("click", closePanel);
}

function filterNFT() {
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

// Event listeners untuk filter
if (giftSearchInput) giftSearchInput.addEventListener("input", filterNFT);
if (maxPrice) maxPrice.addEventListener("input", filterNFT);

// Panel drag functionality
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

// Prevent zoom on mobile
document.addEventListener('touchmove', function (e) {
  if (e.scale !== 1) { e.preventDefault(); }
}, { passive: false });
