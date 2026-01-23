const searchInput = document.getElementById("searchInput");
const modelFilter = document.getElementById("modelFilter");
const symbolFilter = document.getElementById("symbolFilter");
const bgFilter = document.getElementById("bgFilter");
const maxPrice = document.getElementById("maxPrice");
const grid = document.getElementById("giftGrid");

let cards = [];

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
  return previews/${nft.slug}.jpg;
}

/* =========================
   LOAD JSON
   ========================= */
fetch("export/data.json")
  .then(res => {
    if (!res.ok) throw new Error("JSON not found");
    return res.json();
  })
  .then(data => {
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

      const imgSrc = getPreviewImage(nft);

      div.innerHTML = `
        <img 
          src="${imgSrc}"
          alt="${nft.name}"
          onerror="this.src='https://via.placeholder.com/300?text=No+Preview'"
        >

        <h3>${nft.name}</h3>
        <p>#${nft.id}</p>

        <span class="price">
          💰 ${formatIDR(nft.price)}
        </span>

        <p style="margin-top:6px;font-size:12px;opacity:.7">
          Saldo: <b>${formatIDR(nft.saldo)}</b>
        </p>

        <a href="${nft.posting}" target="_blank"
          style="display:inline-block;margin-top:6px;
          font-size:12px;color:#4da3ff;text-decoration:none">
          🔗 Posting
        </a>
      `;

      grid.appendChild(div);
    });

    cards = document.querySelectorAll(".card");
  })
  .catch(err => {
    console.error("FETCH ERROR:", err);
    grid.innerHTML = "<p style='color:red'>Gagal load data</p>";
  });

/* =========================
   FILTER
   ========================= */
function filterNFT() {
  const search = searchInput.value.toLowerCase();
  const model = modelFilter.value;
  const symbol = symbolFilter.value;
  const bg = bgFilter.value;
  const max = maxPrice.value ? parseFloat(maxPrice.value) : Infinity;

  cards.forEach(card => {
    let show = true;

    if (search && !(
      card.dataset.id.includes(search) ||
      card.dataset.name.includes(search) ||
      card.dataset.slug.includes(search)
    )) show = false;

    if (model && model !== card.dataset.model) show = false;
    if (symbol && symbol !== card.dataset.symbol) show = false;
    if (bg && bg !== card.dataset.bg) show = false;
    if (parseFloat(card.dataset.price) > max) show = false;

    card.style.display = show ? "block" : "none";
  });
}

document.querySelectorAll("input, select").forEach(el => {
  el.addEventListener("input", filterNFT);
});
