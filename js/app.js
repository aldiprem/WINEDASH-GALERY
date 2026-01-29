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

overlay.addEventListener("click", closePanel);

let modelFilterValue = "";
let symbolFilterValue = "";
let bgFilterValue = "";
let giftsData = [];
let cards = [];
let giftList = [];
let filteredGifts = [];
let selectedGifts = new Set();
let selectedGift = null;

function formatIDR(number) {
  return "Rp" + Number(number || 0).toLocaleString("id-ID");
}

function formatNFTName(name) {
  if (!name) return "";

  return name
    .replace(/[\s#_-]*\d+$/g, "")
    .trim();
}

function openPanel() {
  panel.classList.add("active");
  overlay.classList.add("active");
}

function closePanel() {
  panel.classList.remove("active");
  overlay.classList.remove("active");
  panel.style.bottom = "";
}

function getPreviewImage(nft) {
  if (nft.image && nft.image.includes("/previews/")) {
    return nft.image;
  }

  return `previews/${nft.slug}.jpg`;
}

function renderGrid(data) {
  grid.innerHTML = "";
  data.forEach(nft => {
    const div = document.createElement("div");
    div.className = "card";
    div.dataset.id = String(nft.id);
    div.dataset.name = nft.name.toLowerCase();
    div.dataset.slug = nft.slug.toLowerCase();
    div.dataset.model = nft.model || "";
    div.dataset.symbol = nft.symbol || "";
    div.dataset.bg = nft.bg || "";
    div.dataset.price = nft.price || 0;

    div.innerHTML = `
      <a href="https://t.me/nft/${nft.slug}" target="_blank">
        <img src="${getPreviewImage(nft)}" alt="${formatNFTName(nft.name)}" onerror="this.src='https://via.placeholder.com/300?text=No+Preview'">
      </a>
      <h3>${formatNFTName(nft.name)}</h3>
      <p>#${nft.id}</p>
      <span class="price open-panel">💰 ${formatIDR(nft.price)}</span>
    `;
    grid.appendChild(div);

    div.querySelector(".open-panel").addEventListener("click", (e) => {
      e.stopPropagation();
      e.preventDefault();
      document.getElementById("detailImg").src = getPreviewImage(nft);
      document.getElementById("detailTitle").textContent = `${formatNFTName(nft.name)} #${nft.id}`;
      document.getElementById("detailModel").textContent = nft.model || "-";
      document.getElementById("detailBg").textContent = nft.bg || "-";
      document.getElementById("detailSymbol").textContent = nft.symbol || "-";
      document.getElementById("detailPrice").textContent = formatIDR(nft.price);

      const baseUrl = "https://t.me/marketaldibot?start=";
      const slug = nft.name.replace(/\s+/g, "") + "_" + nft.id;
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

giftSearchInput.addEventListener("input", () => {
  const val = giftSearchInput.value.toLowerCase();
  giftDropdown.innerHTML = "";

  if (!val) { giftDropdown.style.display = "none"; return; }

  const filtered = giftList.filter(g => g.toLowerCase().includes(val) && !selectedGifts.has(g));
  filtered.forEach(g => {
    const div = document.createElement("div");
    div.textContent = g;
    div.addEventListener("click", () => addGiftBubble(g));
    giftDropdown.appendChild(div);
  });

  giftDropdown.style.display = filtered.length ? "block" : "none";
});

btnAllGifts.addEventListener('click', () => {
  subFilters.style.display = 'flex';
  const counts = {};
  giftsData.forEach(g => counts[g.slug] = (counts[g.slug] || 0) + 1);
  btnAllGifts.innerHTML = 'All Gifts ⬇<br>' + Object.entries(counts).map(([slug, count]) => `${slug} (${count})`).join('<br>');
  selectedGift = null;
  renderGrid(giftsData);
});

// ===== SUBFILTERS =====
btnAllModels.addEventListener('click', () => {
  const models = [...new Set(giftsData.map(g => g.model).filter(Boolean))];
  btnAllModels.innerHTML = 'All Models ⬇<br>' + models.join('<br>');
});

btnAllSymbols.addEventListener('click', () => {
  const symbols = [...new Set(giftsData.map(g => g.symbol).filter(Boolean))];
  btnAllSymbols.innerHTML = 'All Symbols ⬇<br>' + symbols.join('<br>');
});

btnAllBackdrops.addEventListener('click', () => {
  const bgs = [...new Set(giftsData.map(g => g.background).filter(Boolean))];
  btnAllBackdrops.innerHTML = 'All Backdrops ⬇<br>' + bgs.join('<br>');
});

// ===== SORT =====
btnSort.addEventListener('click', () => {
  sortOptions.style.display = sortOptions.style.display === 'block' ? 'none' : 'block';
});

sortOptions.querySelectorAll('div').forEach(opt => {
  opt.addEventListener('click', () => {
    const sortType = opt.dataset.sort;
    let sorted = [...giftsData];

    switch (sortType) {
      case 'lasted':
        sorted.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
        break;
      case 'low':
        sorted.sort((a, b) => a.price - b.price);
        break;
      case 'high':
        sorted.sort((a, b) => b.price - a.price);
        break;
      case 'idAsc':
        sorted.sort((a, b) => a.id - b.id);
        break;
      case 'idDesc':
        sorted.sort((a, b) => b.id - a.id);
        break;
    }

    renderGrid(sorted);
    sortOptions.style.display = 'none';
  });
});

fetch("export/data.json")
  .then(res => res.json())
  .then(data => {
    giftsData = data;
    filteredGifts = [...giftsData];

    const set = new Set();
    giftsData.forEach(g => set.add(g.name.replace(/ #\d+$/, '')));
    giftList = Array.from(set);

    renderGrid(giftsData);
    setTimeout(() => pageLoader.classList.add("hide"), 400);
  })
  .catch(err => {
    console.error("FETCH ERROR:", err);
    grid.innerHTML = "<p style='color:red'>Gagal load data</p>";
  });

function addGiftBubble(gift) {
  if (selectedGifts.has(gift)) return;
  selectedGifts.add(gift);

  const bubble = document.createElement("div");
  bubble.className = "gift-bubble";
  bubble.textContent = gift;
  bubble.addEventListener("click", () => {
    selectedGifts.delete(gift);
    bubble.remove();
    filterNFT();
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
  const model = modelFilter ? modelFilter.value : modelFilterValue;
  const symbol = symbolFilter ? symbolFilter.value : symbolFilterValue;
  const bg = bgFilter ? bgFilter.value : bgFilterValue;
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

const filterElements = [
  giftSearchInput,
  modelFilter,
  symbolFilter,
  bgFilter,
  maxPrice
].filter(el => el !== null);

filterElements.forEach(el => {
  el.addEventListener("input", filterNFT);
});

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
