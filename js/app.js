const giftFilter = document.getElementById("giftFilter");
const modelFilter = document.getElementById("modelFilter");
const symbolFilter = document.getElementById("symbolFilter");
const bgFilter = document.getElementById("bgFilter");
const maxPrice = document.getElementById("maxPrice");
const grid = document.getElementById("giftGrid");
const giftSearchInput = document.getElementById("giftSearchInput");
const giftDropdown = document.getElementById("giftDropdown");
const giftSelected = document.getElementById("giftSelected");

let cards = [];
let giftList = [];
let selectedGifts = new Set();

/* FORMAT RUPIAH */
function formatIDR(number) {
  return "Rp" + Number(number || 0).toLocaleString("id-ID");
}

/* =========================
   IMAGE HANDLER (NO IMGUR)
   ========================= */
function getPreviewImage(nft) {
  // 1️⃣ pakai dari data.json (GitHub Pages)
  if (nft.image && nft.image.includes("/previews/")) {
    return nft.image;
  }

  // 2️⃣ fallback langsung ke folder previews
  return `previews/${nft.slug}.jpg`;
}

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


fetch("export/data.json")
  .then(res => res.json())
  .then(data => {
    // 1️⃣ Buat giftList
    const set = new Set();
    data.forEach(g => {
      const nameOnly = g.name.replace(/ #\d+$/, '');
      set.add(nameOnly);
    });
    giftList = Array.from(set);

    // 2️⃣ Buat NFT cards
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
          <img src="${getPreviewImage(nft)}" alt="${nft.name}" 
          onerror="this.src='https://via.placeholder.com/300?text=No+Preview'">
        </a>
        <h3>${nft.name}</h3>
        <p>#${nft.id}</p>
        <span class="price">💰 ${formatIDR(nft.price)}</span>
        <p style="margin-top:6px;font-size:12px;opacity:.7">Saldo: <b>${formatIDR(nft.saldo)}</b></p>
        <a href="${nft.posting}" target="_blank" style="display:inline-block;margin-top:6px;font-size:12px;color:#4da3ff;text-decoration:none">🔗 Posting</a>
      `;
      grid.appendChild(div);
    });

    cards = document.querySelectorAll(".card");
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

function filterNFT() {
  const search = searchInput.value.toLowerCase();
  const gift = giftFilter.value.toLowerCase();
  const model = modelFilter.value;
  const symbol = symbolFilter.value;
  const bg = bgFilter.value;
  const max = maxPrice.value ? parseFloat(maxPrice.value) : Infinity;

  cards.forEach(card => {
    let show = true;

    // cek bubble gift
    if (selectedGifts.size > 0) {
      let matched = false;
      selectedGifts.forEach(g => {
        if (card.dataset.name.includes(g.toLowerCase())) matched = true;
      });
      if (!matched) show = false;
    }

    if (model && model !== card.dataset.model) show = false;
    if (symbol && symbol !== card.dataset.symbol) show = false;
    if (bg && bg !== card.dataset.bg) show = false;
    if (parseFloat(card.dataset.price) > max) show = false;

    card.style.display = show ? "block" : "none";
  });
}

[searchInput, modelFilter, symbolFilter, bgFilter, maxPrice].forEach(el => {
  el.addEventListener("input", filterNFT);
});
