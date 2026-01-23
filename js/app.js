const searchInput = document.getElementById("searchInput");
const nameFilter = document.getElementById("nameFilter");
const modelFilter = document.getElementById("modelFilter");
const symbolFilter = document.getElementById("symbolFilter");
const bgFilter = document.getElementById("bgFilter");
const maxPrice = document.getElementById("maxPrice");
const grid = document.getElementById("giftGrid");

let gifts = [];

/* FORMAT RUPIAH */
function formatIDR(number) {
  return "Rp" + Number(number || 0).toLocaleString("id-ID");
}

function getPreviewImage(nft) {
  if (nft.image && nft.image.trim() !== "") return nft.image;
  return `previews/${nft.slug}.jpg`;
}

/* =========================
   LOAD JSON
   ========================= */
async function loadGifts() {
  try {
    const res = await fetch("export/data.json");
    if (!res.ok) throw new Error("JSON not found");
    const data = await res.json();

    // Ambil nama gift unik (hapus #ID)
    const giftsMap = {};
    data.forEach(g => {
      const nameOnly = g.name.replace(/ #\d+$/, '');
      if (!giftsMap[nameOnly]) giftsMap[nameOnly] = {...g, name: nameOnly};
    });
    gifts = Object.values(giftsMap);

    // Populate dropdown filter
    const nameSet = new Set(), modelSet = new Set(), symbolSet = new Set(), bgSet = new Set();
    gifts.forEach(g => {
      nameSet.add(g.name);
      if (g.model) modelSet.add(g.model);
      if (g.symbol) symbolSet.add(g.symbol);
      if (g.bg) bgSet.add(g.bg);
    });

    nameSet.forEach(n => nameFilter.innerHTML += `<option value="${n}">${n}</option>`);
    modelSet.forEach(m => modelFilter.innerHTML += `<option value="${m}">${m}</option>`);
    symbolSet.forEach(s => symbolFilter.innerHTML += `<option value="${s}">${s}</option>`);
    bgSet.forEach(b => bgFilter.innerHTML += `<option value="${b}">${b}</option>`);

    renderGifts(); // render awal
  } catch (err) {
    console.error("FETCH ERROR:", err);
    grid.innerHTML = "<p style='color:red'>Gagal load data</p>";
  }
}

/* =========================
   FILTER & RENDER
   ========================= */
function renderGifts() {
  const search = searchInput.value.toLowerCase();
  const name = nameFilter.value;
  const model = modelFilter.value;
  const symbol = symbolFilter.value;
  const bg = bgFilter.value;
  const max = maxPrice.value ? parseFloat(maxPrice.value) : Infinity;

  grid.innerHTML = "";

  const filtered = gifts.filter(g => {
    if (search && !(
      g.name.toLowerCase().includes(search) ||
      g.slug.toLowerCase().includes(search) ||
      String(g.id).includes(search)
    )) return false;
    if (name && g.name !== name) return false;
    if (model && g.model !== model) return false;
    if (symbol && g.symbol !== symbol) return false;
    if (bg && g.bg !== bg) return false;
    if (g.price > max) return false;
    return true;
  });

  filtered.forEach(g => {
    const div = document.createElement("div");
    div.className = "card";
    div.innerHTML = `
      <img src="${getPreviewImage(g)}" alt="${g.name}" 
           onerror="this.src='https://via.placeholder.com/300?text=No+Preview'">

      <h3>${g.name}</h3>
      <p>#${g.id}</p>

      <span class="price">
        💰 ${formatIDR(g.price)}
      </span>

      <p style="margin-top:6px;font-size:12px;opacity:.7">
        Saldo: <b>${formatIDR(g.saldo)}</b>
      </p>

      <a href="${g.posting}" target="_blank"
         style="display:inline-block;margin-top:6px;
         font-size:12px;color:#4da3ff;text-decoration:none">
         🔗 Posting
      </a>
    `;
    grid.appendChild(div);
  });
}

/* =========================
   EVENT LISTENER
   ========================= */
[searchInput, nameFilter, modelFilter, symbolFilter, bgFilter, maxPrice].forEach(el => {
  el.addEventListener("input", renderGifts);
});

loadGifts();
