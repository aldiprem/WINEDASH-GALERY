// ===== SIMPLE VARIABLES =====
let gifts = [];
let filteredGifts = [];
let selectedGifts = new Set();
let currentSort = 'newest';

// ===== DOM ELEMENTS =====
const grid = document.getElementById('giftGrid');
const searchInput = document.getElementById('giftSearchInput');
const searchDropdown = document.getElementById('giftDropdown');
const selectedContainer = document.getElementById('giftSelected');
const detailPanel = document.getElementById('giftDetailPanel');
const overlay = document.getElementById('panelOverlay');
const pageLoader = document.getElementById('pageLoader');

// ===== START APP =====
document.addEventListener('DOMContentLoaded', () => {
  console.log('🎁 Loading gifts...');
  loadGifts();
  setupEventListeners();
});

// ===== LOAD DATA =====
async function loadGifts() {
  try {
    console.log('📥 Fetching data.json...');
    
    const response = await fetch('export/data.json');
    
    if (!response.ok) {
      throw new Error(`Failed to load data.json (${response.status})`);
    }
    
    const data = await response.json();
    
    if (!Array.isArray(data)) {
      throw new Error('data.json should contain an array');
    }
    
    console.log(`✅ Loaded ${data.length} gifts`);
    
    // Simple data processing
    gifts = data.map(gift => ({
      id: gift.id || 0,
      name: gift.name || `Gift #${gift.id}`,
      slug: gift.slug || `gift-${gift.id}`,
      model: gift.model || 'Unknown',
      symbol: gift.symbol || 'None',
      bg: gift.bg || gift.background || 'Default',
      price: Number(gift.price) || 0,
      image: gift.image || `previews/${gift.slug || gift.id}.jpg`,
      created_at: gift.created_at || new Date().toISOString()
    }));
    
    filteredGifts = [...gifts];
    
    // Hide loader immediately
    setTimeout(() => {
      if (pageLoader) pageLoader.classList.add('hide');
    }, 300);
    
    // Render grid
    renderGrid();
    
  } catch (error) {
    console.error('❌ Error:', error);
    showError(error.message);
  }
}

// ===== RENDER FUNCTIONS =====
function renderGrid() {
  if (!grid) return;
  
  grid.innerHTML = '';
  
  if (filteredGifts.length === 0) {
    grid.innerHTML = `
      <div style="grid-column: 1/-1; text-align:center; padding:40px; color:#aaa;">
        <h3>😔 No gifts found</h3>
        <p>Try different search or filter</p>
      </div>
    `;
    return;
  }
  
  // Sort before rendering
  const sortedGifts = sortGifts([...filteredGifts]);
  
  sortedGifts.forEach(gift => {
    const card = createCard(gift);
    grid.appendChild(card);
  });
}

function createCard(gift) {
  const div = document.createElement('div');
  div.className = 'card';
  
  const name = formatName(gift.name);
  const price = formatPrice(gift.price);
  const imageSrc = getImage(gift);
  
  div.innerHTML = `
    <div class="card-image">
      <img src="${imageSrc}" alt="${name}" 
           onerror="this.src='https://via.placeholder.com/300/2c2c2e/ffffff?text=Image'">
      <span class="card-badge">#${gift.id}</span>
    </div>
    <div class="card-content">
      <h3 class="card-title">${name}</h3>
      <p class="card-id">ID: ${gift.id}</p>
      <div class="card-price">
        <span class="price-amount">${price}</span>
        <button class="btn-view" onclick="showDetail(${gift.id})">
          <i class="fas fa-eye"></i> View
        </button>
      </div>
    </div>
  `;
  
  return div;
}

// ===== FILTER & SORT =====
function filterGifts() {
  const searchTerm = searchInput ? searchInput.value.toLowerCase() : '';
  const maxPrice = document.getElementById('maxPrice') ? document.getElementById('maxPrice').value : '';
  const modelFilter = document.getElementById('modelFilter') ? document.getElementById('modelFilter').value : '';
  const symbolFilter = document.getElementById('symbolFilter') ? document.getElementById('symbolFilter').value : '';
  const bgFilter = document.getElementById('bgFilter') ? document.getElementById('bgFilter').value : '';
  
  filteredGifts = gifts.filter(gift => {
    // Search by name or ID
    if (searchTerm && !gift.name.toLowerCase().includes(searchTerm) && 
        !gift.id.toString().includes(searchTerm)) {
      return false;
    }
    
    // Max price filter
    if (maxPrice && gift.price > parseFloat(maxPrice)) {
      return false;
    }
    
    // Model filter
    if (modelFilter && gift.model !== modelFilter) {
      return false;
    }
    
    // Symbol filter
    if (symbolFilter && gift.symbol !== symbolFilter) {
      return false;
    }
    
    // Background filter
    if (bgFilter && gift.bg !== bgFilter) {
      return false;
    }
    
    // Selected gifts filter
    if (selectedGifts.size > 0) {
      const baseName = gift.name.replace(/#\d+$/, '').trim();
      const hasMatch = Array.from(selectedGifts).some(selected => 
        baseName.toLowerCase().includes(selected.toLowerCase())
      );
      if (!hasMatch) return false;
    }
    
    return true;
  });
  
  renderGrid();
}

function sortGifts(giftsArray) {
  switch (currentSort) {
    case 'price-low':
      return giftsArray.sort((a, b) => a.price - b.price);
    case 'price-high':
      return giftsArray.sort((a, b) => b.price - a.price);
    case 'id-asc':
      return giftsArray.sort((a, b) => a.id - b.id);
    case 'id-desc':
      return giftsArray.sort((a, b) => b.id - a.id);
    case 'oldest':
      return giftsArray.sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
    case 'newest':
    default:
      return giftsArray.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
  }
}

// ===== SEARCH DROPDOWN =====
function updateSearchDropdown() {
  if (!searchInput || !searchDropdown) return;
  
  const searchTerm = searchInput.value.toLowerCase().trim();
  
  if (!searchTerm) {
    searchDropdown.style.display = 'none';
    return;
  }
  
  // Get unique gift names (without IDs)
  const uniqueNames = [...new Set(gifts.map(g => g.name.replace(/#\d+$/, '').trim()))];
  
  const filtered = uniqueNames.filter(name => 
    name.toLowerCase().includes(searchTerm) && !selectedGifts.has(name)
  );
  
  if (filtered.length === 0) {
    searchDropdown.style.display = 'none';
    return;
  }
  
  searchDropdown.innerHTML = '';
  filtered.forEach(name => {
    const div = document.createElement('div');
    div.textContent = name;
    div.onclick = () => addSelectedGift(name);
    searchDropdown.appendChild(div);
  });
  
  searchDropdown.style.display = 'block';
}

function addSelectedGift(giftName) {
  if (selectedGifts.has(giftName)) return;
  
  selectedGifts.add(giftName);
  
  const bubble = document.createElement('div');
  bubble.className = 'gift-bubble';
  bubble.innerHTML = `${giftName} <span class="remove-bubble">×</span>`;
  
  bubble.onclick = () => {
    selectedGifts.delete(giftName);
    bubble.remove();
    filterGifts();
  };
  
  if (selectedContainer) {
    selectedContainer.appendChild(bubble);
  }
  
  if (searchInput) searchInput.value = '';
  if (searchDropdown) searchDropdown.style.display = 'none';
  
  filterGifts();
}

// ===== DETAIL PANEL =====
function showDetail(giftId) {
  const gift = gifts.find(g => g.id === giftId);
  if (!gift || !detailPanel || !overlay) return;
  
  // Update panel content
  document.getElementById('detailImg').src = getImage(gift);
  document.getElementById('detailTitle').textContent = formatName(gift.name);
  document.getElementById('detailModel').textContent = gift.model || '-';
  document.getElementById('detailBg').textContent = gift.bg || '-';
  document.getElementById('detailSymbol').textContent = gift.symbol || '-';
  document.getElementById('detailPrice').textContent = formatPrice(gift.price);
  document.getElementById('detailId').textContent = `#${gift.id}`;
  
  // Update buttons
  const baseUrl = 'https://t.me/marketaldibot?start=';
  const slug = gift.name.replace(/\s+/g, '') + '_' + gift.id;
  document.getElementById('btnBeli').href = baseUrl + 'beli_' + slug;
  document.getElementById('btnNego').href = baseUrl + 'nego_' + slug;
  
  // Show panel
  detailPanel.classList.add('active');
  overlay.classList.add('active');
  document.body.style.overflow = 'hidden';
}

function closeDetail() {
  if (detailPanel && overlay) {
    detailPanel.classList.remove('active');
    overlay.classList.remove('active');
    document.body.style.overflow = '';
  }
}

// ===== UTILITY FUNCTIONS =====
function formatPrice(price) {
  return `Rp${Number(price).toLocaleString('id-ID')}`;
}

function formatName(name) {
  return name.replace(/#\d+$/, '').trim();
}

function getImage(gift) {
  if (gift.image && (gift.image.startsWith('http') || gift.image.includes('/'))) {
    return gift.image;
  }
  return `previews/${gift.slug || gift.id}.jpg`;
}

function showError(message) {
  console.error('Error:', message);
  
  if (grid) {
    grid.innerHTML = `
      <div style="grid-column: 1/-1; text-align:center; padding:40px; color:#ff6b6b;">
        <h3>⚠️ Error Loading Data</h3>
        <p>${message}</p>
        <p style="font-size:14px; color:#aaa; margin-top:20px;">
          Make sure <strong>export/data.json</strong> exists and has correct format
        </p>
        <button onclick="location.reload()" style="
          margin-top:20px;
          padding:10px 20px;
          background:#7cf9ff;
          color:#000;
          border:none;
          border-radius:8px;
          cursor:pointer;
          font-weight:bold;
        ">
          🔄 Try Again
        </button>
      </div>
    `;
  }
  
  if (pageLoader) pageLoader.classList.add('hide');
}

// ===== EVENT LISTENERS =====
function setupEventListeners() {
  // Search input
  if (searchInput) {
    let searchTimeout;
    searchInput.addEventListener('input', () => {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(() => {
        updateSearchDropdown();
        filterGifts();
      }, 300);
    });
  }
  
  // Close search dropdown when clicking outside
  document.addEventListener('click', (e) => {
    if (searchDropdown && !searchInput.contains(e.target) && !searchDropdown.contains(e.target)) {
      searchDropdown.style.display = 'none';
    }
  });
  
  // Filter inputs
  const filterInputs = ['maxPrice', 'modelFilter', 'symbolFilter', 'bgFilter'];
  filterInputs.forEach(id => {
    const input = document.getElementById(id);
    if (input) {
      input.addEventListener('change', filterGifts);
      input.addEventListener('input', filterGifts);
    }
  });
  
  // Sort buttons
  const sortButtons = document.querySelectorAll('[data-sort]');
  sortButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      currentSort = btn.dataset.sort;
      filterGifts();
    });
  });
  
  // Close detail panel
  if (overlay) overlay.addEventListener('click', closeDetail);
  
  const closeBtn = document.getElementById('closePanel');
  if (closeBtn) closeBtn.addEventListener('click', closeDetail);
  
  // Clear filters button
  const clearBtn = document.getElementById('clearFilters');
  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      selectedGifts.clear();
      if (selectedContainer) selectedContainer.innerHTML = '';
      if (searchInput) searchInput.value = '';
      
      filterInputs.forEach(id => {
        const input = document.getElementById(id);
        if (input) input.value = '';
      });
      
      filterGifts();
    });
  }
  
  // Scroll to top button
  const scrollTopBtn = document.getElementById('scrollTopBtn');
  if (scrollTopBtn) {
    window.addEventListener('scroll', () => {
      if (window.scrollY > 500) {
        scrollTopBtn.classList.add('show');
      } else {
        scrollTopBtn.classList.remove('show');
      }
    });
    
    scrollTopBtn.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }
  
  // Escape key closes detail panel
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && detailPanel.classList.contains('active')) {
      closeDetail();
    }
  });
}

// ===== EXPORT TO WINDOW =====
window.showDetail = showDetail;
window.closeDetail = closeDetail;
