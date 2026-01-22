const searchInput = document.getElementById("searchInput");
const modelFilter = document.getElementById("modelFilter");
const symbolFilter = document.getElementById("symbolFilter");
const bgFilter = document.getElementById("bgFilter");
const maxPrice = document.getElementById("maxPrice");
const grid = document.getElementById("giftGrid");

let cards = [];

fetch("data.json")
  .then(res => res.json())
  .then(data => {
    grid.innerHTML = "";
    data.forEach(nft => {
      const div = document.createElement("div");
      div.className = "card";
      div.dataset.id = nft.id;
      div.dataset.name = nft.name.toLowerCase();
      div.dataset.slug = nft.slug;
      div.dataset.model = nft.model;
      div.dataset.symbol = nft.symbol;
      div.dataset.bg = nft.bg;
      div.dataset.price = nft.price;

      div.innerHTML = `
        <img src="${nft.image}">
        <h3>${nft.name}</h3>
        <p>#${nft.id}</p>
        <span class="price">💎 ${nft.price} TON</span>
      `;
      grid.appendChild(div);
    });
    cards = document.querySelectorAll(".card");
  });

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

document.querySelectorAll("input, select").forEach(el =>
  el.addEventListener("input", filterNFT)
);
