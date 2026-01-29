// ===== GLOBAL VARIABLES =====
let giftsData = [];
let filteredData = [];
let cards = [];
let giftList = [];
let selectedGifts = new Set();
let currentFilter = 'all';
let currentSort = 'newest';
let isLoading = false;

// ===== DOM ELEMENTS =====
const elements = {
  grid: document.getElementById('giftGrid'),
  giftSearchInput: document.getElementById('giftSearchInput'),
  giftDropdown: document.getElementById('giftDropdown'),
  giftSelected: document.getElementById('giftSelected'),
  panel: document.getElementById('giftDetailPanel'),
  overlay: document.getElementById('panelOverlay'),
  btnBeli: document.getElementById('btnBeli'),
  btnNego: document.getElementById('btnNego'),
  pageLoader: document.getElementById('pageLoader'),
  scrollTopBtn: document.getElementById('scrollTopBtn'),
  loaderStatus: document.getElementById('loaderStatus'),
  loaderBar: document.getElementById('loaderBar'),
  totalGifts: document.getElementById('totalGifts'),
  uniqueTypes: document.getElementById('uniqueTypes'),
  priceRange: document.getElementById('priceRange'),
  headerStats: document.getElementById('headerStats'),
  gridTitle: document.getElementById('gridTitle'),
  gridCount: document.getElementById('gridCount'),
  noResults: document.getElementById('noResults'),
  clearFilters: document.getElementById('clearFilters'),
  
  // Filter buttons
  btnAllGifts: document.getElementById('btnAllGifts'),
  btnFilterModel: document.getElementById('btnFilterModel'),
  btnFilterSymbol: document.getElementById('btnFilterSymbol'),
  btnFilterBackground: document.getElementById('btnFilterBackground'),
  
  // Filter selects
  modelFilter: document.getElementById('modelFilter'),
  symbolFilter: document.getElementById('symbolFilter'),
  bgFilter: document.getElementById('bgFilter'),
  maxPrice: document.getElementById('maxPrice'),
  
  // Filter containers
  modelFilterContainer: document.getElementById('modelFilterContainer'),
  symbolFilterContainer: document.getElementById('symbolFilterContainer'),
  bgFilterContainer: document.getElementById('bgFilterContainer'),
  
  // Sort
  btnSort: document.getElementById('btnSort'),
  sortOptions: document.getElementById('sortOptions'),
  
  // Detail panel elements
  detailImg: document.getElementById('detailImg'),
  detailTitle: document.getElementById('detailTitle'),
  detailModel: document.getElementById('detailModel'),
  detailBg: document.getElementById('detailBg'),
  detailSymbol: document.getElementById('detailSymbol'),
  detailPrice: document.getElementById('detailPrice'),
  detailId: document.getElementById('detailId'),
  detailIdText: document.getElementById('detailIdText'),
  detailPriceBadge: document.getElementById('detailPriceBadge'),
  closePanel: document.getElementById('closePanel'),
  btnShare: document.getElementById('btnShare')
};

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', async () => {
  console.log('🚀 Initializing WINEDASH GIFT Marketplace...');
  updateLoaderStatus('Checking dependencies...');
  
  // Initialize event listeners
  initEventListeners();
  
  // Load data with progress indication
  await loadDataWithProgress();
  
  // Final setup
  setTimeout(() => {
    updateLoaderStatus('Ready!');
    setTimeout(() => {
      elements.pageLoader.classList.add('hide');
    }, 500);
  }, 300);
});

// ===== LOADER FUNCTIONS =====
function updateLoaderStatus(text) {
  if (elements.loaderStatus) {
    elements.loaderStatus.textContent = text;
  }
  console.log('📢', text);
}

function updateLoaderProgress(percent) {
  if (elements.loaderBar) {
    elements.loaderBar.style.width = `${percent}%`;
  }
}

// ===== DATA LOADING =====
async function loadDataWithProgress() {
  try {
    isLoading = true;
    updateLoaderStatus('Fetching data from server...');
    updateLoaderProgress(10);
    
    const response = await fetch('export/data.json', {
      cache: 'no-cache',
      headers: {
        'Accept': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    updateLoaderStatus('Parsing JSON data...');
    updateLoaderProgress(30);
    
    const data = await response.json();
    
    if (!Array.isArray(data)) {
      throw new Error('Invalid data format: Expected array');
    }
    
    updateLoaderStatus(`Processing ${data.length} gifts...`);
    updateLoaderProgress(60);
    
    // Process data
    giftsData = data.map(item => ({
      ...item,
      slug: item.slug || `gift-${item.id}`,
      model: item.model || 'Unknown',
      symbol: item.symbol || 'None',
      bg: item.bg || item.background || 'Default',
      price: Number(item.price) || 0,
      created_at: item.created_at || new Date().toISOString()
    }));
    
    filteredData = [...giftsData];
    
    updateLoaderStatus('Building filters and indexes...');
    updateLoaderProgress(80);
    
    // Initialize filters and lists
    initializeFilters();
    buildGiftList();
    updateStats();
    
    updateLoaderStatus('Rendering gift grid...');
    updateLoaderProgress(90);
    
    // Initial render
    renderGrid();
    
    updateLoaderProgress(100);
    isLoading = false;
    
    console.log(`✅ Successfully loaded ${giftsData.length} gifts`);
    
  } catch (error) {
    console.error('❌ Failed to load data:', error);
    showError(`Failed to load data: ${error.message}`);
    isLoading = false;
  }
}

// ===== INITIALIZATION FUNCTIONS =====
function initializeFilters() {
  // Get unique values for filters
  const models = [...new Set(giftsData.map(g => g.model).filter(Boolean))].sort();
  const symbols = [...new Set(giftsData.map(g => g.symbol).filter(Boolean))].sort();
  const backgrounds = [...new Set(giftsData.map(g => g.bg).filter(Boolean))].sort();
  
  // Populate model filter
  if (elements.modelFilter) {
    models.forEach(model => {
      const option = document.createElement('option');
      option.value = model;
      option.textContent = model;
      elements.modelFilter.appendChild(option);
    });
  }
  
  // Populate symbol filter
  if (elements.symbolFilter) {
    symbols.forEach(symbol => {
      const option = document.createElement('option');
      option.value = symbol;
      option.textContent = symbol;
      elements.symbolFilter.appendChild(option);
    });
  }
  
  // Populate background filter
  if (elements.bgFilter) {
    backgrounds.forEach(bg => {
      const option = document.createElement('option');
      option.value = bg;
      option.textContent = bg;
      elements.bgFilter.appendChild(option);
    });
  }
}

function buildGiftList() {
  const set = new Set();
  giftsData.forEach(gift => {
    if (gift.name) {
      const baseName = gift.name.replace(/\s*#\d+$/, '').trim();
      if (baseName) set.add(baseName);
    }
  });
  giftList = Array.from(set).sort();
}

function updateStats() {
  if (!giftsData.length) return;
  
  const total = giftsData.length;
  const unique = new Set(giftsData.map(g => g.name?.replace(/\s*#\d+$/, ''))).size;
  const prices = giftsData.map(g => g.price).filter(p => p > 0);
  const minPrice = prices.length ? Math.min(...prices) : 0;
  const maxPrice = prices.length ? Math.max(...prices) : 0;
  
  if (elements.totalGifts) {
    elements.totalGifts.textContent = total.toLocaleString();
  }
  
  if (elements.uniqueTypes) {
    elements.uniqueTypes.textContent = unique.toLocaleString();
  }
  
  if (elements.priceRange) {
    elements.priceRange.textContent = `Rp${minPrice.toLocaleString()} - Rp${maxPrice.toLocaleString()}`;
  }
  
  if (elements.headerStats) {
    elements.headerStats.innerHTML = `
      <i class="fas fa-sync-alt"></i> Updated: ${new Date().toLocaleTimeString()}
    `;
  }
}

// ===== RENDERING FUNCTIONS =====
function renderGrid() {
  if (!elements.grid) return;
  
  // Clear grid
  elements.grid.innerHTML = '';
  
  // Update grid info
  if (elements.gridTitle) {
    elements.gridTitle.textContent = getGridTitle();
  }
  
  if (elements.gridCount) {
    elements.gridCount.textContent = `${filteredData.length} ${filteredData.length === 1 ? 'item' : 'items'}`;
  }
  
  // Show/hide no results
  if (elements.noResults) {
    elements.noResults.style.display = filteredData.length ? 'none' : 'flex';
  }
  
  // If no data, show message
  if (!filteredData.length) {
    elements.grid.innerHTML = `
      <div class="no-results" style="grid-column: 1 / -1;">
        <i class="fas fa-search"></i>
        <h3>No gifts found</h3>
        <p>Try adjusting your filters or search terms</p>
      </div>
    `;
    cards = [];
    return;
  }
  
  // Render cards
  const fragment = document.createDocumentFragment();
  
  filteredData.forEach(nft => {
    const card = createCard(nft);
    fragment.appendChild(card);
  });
  
  elements.grid.appendChild(fragment);
  cards = Array.from(elements.grid.querySelectorAll('.card'));
}

function createCard(nft) {
  const div = document.createElement('div');
  div.className = 'card';
  div.dataset.id = nft.id;
  div.dataset.name = (nft.name || '').toLowerCase();
  div.dataset.model = nft.model || '';
  div.dataset.symbol = nft.symbol || '';
  div.dataset.bg = nft.bg || '';
  div.dataset.price = nft.price || 0;
  
  const name = formatNFTName(nft.name || `Gift #${nft.id}`);
  const price = formatIDR(nft.price);
  const imageUrl = getPreviewImage(nft);
  
  div.innerHTML = `
    <div class="card-image">
      <img src="${imageUrl}" alt="${name}" loading="lazy"
           onerror="this.src='https://via.placeholder.com/300/2c2c2e/ffffff?text=No+Image'">
      <div class="card-badge">#${nft.id}</div>
    </div>
    <div class="card-content">
      <h3 class="card-title">${name}</h3>
      <div class="card-id">ID: ${nft.id}</div>
      <div class="card-price">
        <span class="price-amount">${price}</span>
        <button class="btn-view open-panel">
          <i class="fas fa-eye"></i> View
        </button>
      </div>
    </div>
  `;
  
  // Add event listener for detail panel
  div.querySelector('.open-panel').addEventListener('click', (e) => {
    e.preventDefault();
    openNFTDetailPanel(nft);
  });
  
  return div;
}

function getGridTitle() {
  const filters = [];
  
  if (selectedGifts.size > 0) {
    filters.push(`${selectedGifts.size} selected`);
  }
  
  if (elements.modelFilter && elements.modelFilter.value) {
    filters.push(`Model: ${elements.modelFilter.value}`);
  }
  
  if (elements.symbolFilter && elements.symbolFilter.value) {
    filters.push(`Symbol: ${elements.symbolFilter.value}`);
  }
  
  if (elements.bgFilter && elements.bgFilter.value) {
    filters.push(`BG: ${elements.bgFilter.value}`);
  }
  
  if (elements.maxPrice && elements.maxPrice.value) {
    filters.push(`Max: Rp${parseInt(elements.maxPrice.value).toLocaleString()}`);
  }
  
  return filters.length > 0 ? `Gifts (${filters.join(', ')})` : 'All Gifts';
}

// ===== FILTER FUNCTIONS =====
function filterData() {
  if (!giftsData.length) return;
  
  let result = [...giftsData];
  
  // Text search
  const searchText = elements.giftSearchInput.value.toLowerCase().trim();
  if (searchText) {
    result = result.filter(nft => {
      const name = (nft.name || '').toLowerCase();
      const id = nft.id.toString();
      return name.includes(searchText) || id.includes(searchText);
    });
  }
  
  // Selected gifts filter
  if (selectedGifts.size > 0) {
    result = result.filter(nft => {
      const baseName = nft.name?.replace(/\s*#\d+$/, '').trim() || '';
      return Array.from(selectedGifts).some(gift => 
        baseName.toLowerCase().includes(gift.toLowerCase())
      );
    });
  }
  
  // Model filter
  if (elements.modelFilter && elements.modelFilter.value) {
    result = result.filter(nft => nft.model === elements.modelFilter.value);
  }
  
  // Symbol filter
  if (elements.symbolFilter && elements.symbolFilter.value) {
    result = result.filter(nft => nft.symbol === elements.symbolFilter.value);
  }
  
  // Background filter
  if (elements.bgFilter && elements.bgFilter.value) {
    result = result.filter(nft => nft.bg === elements.bgFilter.value);
  }
  
  // Max price filter
  if (elements.maxPrice && elements.maxPrice.value) {
    const maxPrice = parseFloat(elements.maxPrice.value);
    if (!isNaN(maxPrice) && maxPrice > 0) {
      result = result.filter(nft => nft.price <= maxPrice);
    }
  }
  
  // Apply sorting
  result = sortData(result, currentSort);
  
  filteredData = result;
  renderGrid();
}

function sortData(data, sortType) {
  const sorted = [...data];
  
  switch (sortType) {
    case 'newest':
      sorted.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
      break;
    case 'oldest':
      sorted.sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
      break;
    case 'price-low':
      sorted.sort((a, b) => (a.price || 0) - (b.price || 0));
      break;
    case 'price-high':
      sorted.sort((a, b) => (b.price || 0) - (a.price || 0));
      break;
    case 'id-asc':
      sorted.sort((a, b) => (a.id || 0) - (b.id || 0));
      break;
    case 'id-desc':
      sorted.sort((a, b) => (b.id || 0) - (a.id || 0));
      break;
  }
  
  return sorted;
}

// ===== UTILITY FUNCTIONS =====
function formatIDR(number) {
  return `Rp${Number(number || 0).toLocaleString('id-ID')}`;
}

function formatNFTName(name) {
  if (!name) return 'Unnamed Gift';
  return name.replace(/\s*#\d+$/, '').trim();
}

function getPreviewImage(nft) {
  if (nft.image && (nft.image.includes('/previews/') || nft.image.startsWith('http'))) {
    return nft.image;
  }
  return `previews/${nft.slug || nft.id}.jpg`;
}

// ===== DETAIL PANEL FUNCTIONS =====
function openNFTDetailPanel(nft) {
  if (!elements.panel || !elements.overlay) return;
  
  // Update panel content
  elements.detailImg.src = getPreviewImage(nft);
  elements.detailImg.alt = nft.name || `Gift #${nft.id}`;
  elements.detailTitle.textContent = formatNFTName(nft.name || `Gift #${nft.id}`);
  elements.detailModel.textContent = nft.model || '-';
  elements.detailBg.textContent = nft.bg || '-';
  elements.detailSymbol.textContent = nft.symbol || '-';
  elements.detailPrice.textContent = formatIDR(nft.price);
  elements.detailId.textContent = `#${nft.id}`;
  elements.detailIdText.textContent = `#${nft.id}`;
  elements.detailPriceBadge.textContent = formatIDR(nft.price);
  
  // Update action links
  const baseUrl = 'https://t.me/marketaldibot?start=';
  const slug = (nft.name || `Gift${nft.id}`).replace(/\s+/g, '') + '_' + nft.id;
  elements.btnBeli.href = baseUrl + 'beli_' + slug;
  elements.btnNego.href = baseUrl + 'nego_' + slug;
  
  // Share button
  if (elements.btnShare) {
    elements.btnShare.onclick = () => shareNFT(nft);
  }
  
  // Open panel
  elements.panel.classList.add('active');
  elements.overlay.classList.add('active');
  document.body.style.overflow = 'hidden';
}

function closePanel() {
  if (elements.panel && elements.overlay) {
    elements.panel.classList.remove('active');
    elements.overlay.classList.remove('active');
    document.body.style.overflow = '';
  }
}

function shareNFT(nft) {
  const url = window.location.href;
  const text = `Check out this NFT: ${formatNFTName(nft.name)} #${nft.id} - ${formatIDR(nft.price)}`;
  
  if (navigator.share) {
    navigator.share({
      title: 'WINEDASH GIFT',
      text: text,
      url: url
    });
  } else {
    // Fallback: Copy to clipboard
    navigator.clipboard.writeText(`${text}\n${url}`)
      .then(() => alert('Link copied to clipboard!'))
      .catch(err => console.error('Failed to copy:', err));
  }
}

// ===== SEARCH & FILTER UI FUNCTIONS =====
function addGiftBubble(gift) {
  if (selectedGifts.has(gift)) return;
  selectedGifts.add(gift);
  
  const bubble = document.createElement('div');
  bubble.className = 'filter-chip';
  bubble.innerHTML = `
    ${gift}
    <i class="fas fa-times remove-bubble"></i>
  `;
  
  bubble.addEventListener('click', (e) => {
    if (e.target.classList.contains('remove-bubble') || e.target === bubble) {
      selectedGifts.delete(gift);
      bubble.remove();
      filterData();
    }
  });
  
  if (elements.giftSelected) {
    elements.giftSelected.appendChild(bubble);
  }
  
  elements.giftSearchInput.value = '';
  elements.giftDropdown.classList.remove('active');
  filterData();
}

function showGiftDropdown() {
  const searchText = elements.giftSearchInput.value.toLowerCase().trim();
  
  if (!searchText || !elements.giftDropdown) {
    elements.giftDropdown.classList.remove('active');
    return;
  }
  
  const filtered = giftList.filter(g => 
    g.toLowerCase().includes(searchText) && !selectedGifts.has(g)
  );
  
  if (!filtered.length) {
    elements.giftDropdown.classList.remove('active');
    return;
  }
  
  elements.giftDropdown.innerHTML = '';
  filtered.forEach(gift => {
    const item = document.createElement('div');
    item.className = 'gift-dropdown-item';
    item.textContent = gift;
    item.addEventListener('click', () => addGiftBubble(gift));
    elements.giftDropdown.appendChild(item);
  });
  
  elements.giftDropdown.classList.add('active');
}

function clearAllFilters() {
  // Clear selected gifts
  selectedGifts.clear();
  if (elements.giftSelected) {
    elements.giftSelected.innerHTML = '';
  }
  
  // Clear search input
  if (elements.giftSearchInput) {
    elements.giftSearchInput.value = '';
  }
  
  // Clear filter selects
  if (elements.modelFilter) elements.modelFilter.value = '';
  if (elements.symbolFilter) elements.symbolFilter.value = '';
  if (elements.bgFilter) elements.bgFilter.value = '';
  if (elements.maxPrice) elements.maxPrice.value = '';
  
  // Reset filter buttons
  setActiveFilterButton('all');
  
  // Hide filter dropdowns
  hideAllFilterDropdowns();
  
  // Reset sort
  currentSort = 'newest';
  
  // Re-filter and render
  filterData();
}

function setActiveFilterButton(filterType) {
  const buttons = [
    elements.btnAllGifts,
    elements.btnFilterModel,
    elements.btnFilterSymbol,
    elements.btnFilterBackground
  ];
  
  buttons.forEach(btn => {
    if (btn) {
      btn.classList.remove('active');
    }
  });
  
  const activeBtn = elements[`btnFilter${filterType.charAt(0).toUpperCase() + filterType.slice(1)}`] || elements.btnAllGifts;
  if (activeBtn) {
    activeBtn.classList.add('active');
  }
  
  currentFilter = filterType;
}

function showFilterDropdown(filterType) {
  // Hide all dropdowns first
  hideAllFilterDropdowns();
  
  // Show selected dropdown
  const container = elements[`${filterType}FilterContainer`];
  if (container) {
    container.style.display = 'block';
  }
  
  setActiveFilterButton(filterType);
}

function hideAllFilterDropdowns() {
  const containers = [
    elements.modelFilterContainer,
    elements.symbolFilterContainer,
    elements.bgFilterContainer
  ];
  
  containers.forEach(container => {
    if (container) {
      container.style.display = 'none';
    }
  });
}

// ===== EVENT LISTENERS =====
function initEventListeners() {
  // Search input
  if (elements.giftSearchInput) {
    let searchTimeout;
    elements.giftSearchInput.addEventListener('input', () => {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(() => {
        showGiftDropdown();
        filterData();
      }, 300); // Debounce 300ms
    });
    
    elements.giftSearchInput.addEventListener('focus', showGiftDropdown);
  }
  
  // Filter inputs
  const filterInputs = [
    elements.modelFilter,
    elements.symbolFilter,
    elements.bgFilter,
    elements.maxPrice
  ];
  
  filterInputs.forEach(input => {
    if (input) {
      input.addEventListener('change', filterData);
      input.addEventListener('input', filterData);
    }
  });
  
  // Filter buttons
  if (elements.btnAllGifts) {
    elements.btnAllGifts.addEventListener('click', () => {
      hideAllFilterDropdowns();
      setActiveFilterButton('all');
      filterData();
    });
  }
  
  if (elements.btnFilterModel) {
    elements.btnFilterModel.addEventListener('click', () => showFilterDropdown('model'));
  }
  
  if (elements.btnFilterSymbol) {
    elements.btnFilterSymbol.addEventListener('click', () => showFilterDropdown('symbol'));
  }
  
  if (elements.btnFilterBackground) {
    elements.btnFilterBackground.addEventListener('click', () => showFilterDropdown('bg'));
  }
  
  // Clear filters button
  if (elements.clearFilters) {
    elements.clearFilters.addEventListener('click', clearAllFilters);
  }
  
  // Sort functionality
  if (elements.btnSort && elements.sortOptions) {
    elements.btnSort.addEventListener('click', () => {
      elements.sortOptions.classList.toggle('active');
    });
    
    const sortOptions = elements.sortOptions.querySelectorAll('.sort-option');
    sortOptions.forEach(option => {
      option.addEventListener('click', () => {
        currentSort = option.dataset.sort;
        elements.sortOptions.classList.remove('active');
        filterData();
        
        // Update sort button text
        const icon = option.querySelector('i').cloneNode(true);
        const text = option.textContent.trim();
        elements.btnSort.innerHTML = '';
        elements.btnSort.appendChild(icon);
        elements.btnSort.appendChild(document.createTextNode(' ' + text));
      });
    });
  }
  
  // Close dropdowns when clicking outside
  document.addEventListener('click', (e) => {
    // Close gift dropdown
    if (elements.giftDropdown && !elements.giftSearchInput.contains(e.target) && !elements.giftDropdown.contains(e.target)) {
      elements.giftDropdown.classList.remove('active');
    }
    
    // Close sort dropdown
    if (elements.sortOptions && elements.btnSort && 
        !elements.btnSort.contains(e.target) && !elements.sortOptions.contains(e.target)) {
      elements.sortOptions.classList.remove('active');
    }
  });
  
  // Detail panel
  if (elements.overlay) {
    elements.overlay.addEventListener('click', closePanel);
  }
  
  if (elements.closePanel) {
    elements.closePanel.addEventListener('click', closePanel);
  }
  
  // Scroll to top
  if (elements.scrollTopBtn) {
    window.addEventListener('scroll', () => {
      if (window.scrollY > 500) {
        elements.scrollTopBtn.classList.add('show');
      } else {
        elements.scrollTopBtn.classList.remove('show');
      }
    });
    
    elements.scrollTopBtn.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }
  
  // Prevent zoom on mobile
  document.addEventListener('touchmove', (e) => {
    if (e.scale !== 1) {
      e.preventDefault();
    }
  }, { passive: false });
  
  // Keyboard shortcuts
  document.addEventListener('keydown', (e) => {
    // Escape closes panel
    if (e.key === 'Escape' && elements.panel.classList.contains('active')) {
      closePanel();
    }
    
    // Clear filters with Ctrl+Shift+C
    if (e.ctrlKey && e.shiftKey && e.key === 'C') {
      clearAllFilters();
    }
    
    // Focus search with Ctrl+K
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      if (elements.giftSearchInput) {
        elements.giftSearchInput.focus();
      }
    }
  });
  
  // Auto-refresh data every 5 minutes
  setInterval(async () => {
    if (!isLoading) {
      console.log('🔄 Auto-refreshing data...');
      await refreshData();
    }
  }, 5 * 60 * 1000); // 5 minutes
  
  // Add loading state to images
  document.addEventListener('DOMContentLoaded', () => {
    const images = document.querySelectorAll('img');
    images.forEach(img => {
      img.addEventListener('load', () => {
        img.classList.add('loaded');
      });
    });
  });
}

// ===== DATA REFRESH FUNCTIONS =====
async function refreshData() {
  try {
    updateLoaderStatus('Refreshing data...');
    elements.pageLoader.classList.remove('hide');
    
    const response = await fetch('export/data.json?t=' + Date.now(), {
      cache: 'no-cache'
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    
    if (!Array.isArray(data)) {
      throw new Error('Invalid data format: Expected array');
    }
    
    // Process new data
    const newData = data.map(item => ({
      ...item,
      slug: item.slug || `gift-${item.id}`,
      model: item.model || 'Unknown',
      symbol: item.symbol || 'None',
      bg: item.bg || item.background || 'Default',
      price: Number(item.price) || 0,
      created_at: item.created_at || new Date().toISOString()
    }));
    
    // Check if data has changed
    const hasChanged = JSON.stringify(giftsData) !== JSON.stringify(newData);
    
    if (hasChanged) {
      console.log('🔄 Data updated, refreshing UI...');
      giftsData = newData;
      filteredData = [...giftsData];
      
      // Rebuild filters and lists
      rebuildFilters();
      buildGiftList();
      updateStats();
      
      // Re-apply current filters
      filterData();
      
      // Show notification
      showNotification('Data updated successfully!', 'success');
    } else {
      console.log('✅ Data is already up-to-date');
    }
    
  } catch (error) {
    console.error('❌ Failed to refresh data:', error);
    showNotification('Failed to refresh data', 'error');
  } finally {
    elements.pageLoader.classList.add('hide');
    updateLoaderStatus('Ready');
  }
}

function rebuildFilters() {
  // Clear existing options
  [elements.modelFilter, elements.symbolFilter, elements.bgFilter].forEach(select => {
    if (select) {
      while (select.options.length > 1) {
        select.remove(1);
      }
    }
  });
  
  // Rebuild with new data
  initializeFilters();
}

// ===== NOTIFICATION SYSTEM =====
function showNotification(message, type = 'info') {
  // Create notification element
  const notification = document.createElement('div');
  notification.className = `notification notification-${type}`;
  notification.innerHTML = `
    <div class="notification-content">
      <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
      <span>${message}</span>
    </div>
    <button class="notification-close">
      <i class="fas fa-times"></i>
    </button>
  `;
  
  // Add to DOM
  document.body.appendChild(notification);
  
  // Add close button event
  notification.querySelector('.notification-close').addEventListener('click', () => {
    notification.remove();
  });
  
  // Auto-remove after 5 seconds
  setTimeout(() => {
    if (notification.parentNode) {
      notification.remove();
    }
  }, 5000);
  
  // Add CSS for notifications if not already present
  if (!document.querySelector('#notification-styles')) {
    const style = document.createElement('style');
    style.id = 'notification-styles';
    style.textContent = `
      .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--gray-dark);
        border-left: 4px solid;
        padding: 1rem;
        border-radius: var(--radius);
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        min-width: 300px;
        max-width: 400px;
        box-shadow: var(--shadow-lg);
        z-index: 9999;
        animation: slideIn 0.3s ease-out;
      }
      
      .notification-success {
        border-color: var(--success);
      }
      
      .notification-error {
        border-color: var(--danger);
      }
      
      .notification-info {
        border-color: var(--primary);
      }
      
      .notification-content {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        flex: 1;
      }
      
      .notification-content i {
        font-size: 1.25rem;
      }
      
      .notification-success .notification-content i {
        color: var(--success);
      }
      
      .notification-error .notification-content i {
        color: var(--danger);
      }
      
      .notification-info .notification-content i {
        color: var(--primary);
      }
      
      .notification-close {
        background: transparent;
        border: none;
        color: rgba(255, 255, 255, 0.5);
        cursor: pointer;
        padding: 0.25rem;
        border-radius: 4px;
        transition: var(--transition);
      }
      
      .notification-close:hover {
        background: rgba(255, 255, 255, 0.1);
        color: var(--light);
      }
      
      @keyframes slideIn {
        from {
          transform: translateX(100%);
          opacity: 0;
        }
        to {
          transform: translateX(0);
          opacity: 1;
        }
      }
    `;
    document.head.appendChild(style);
  }
}

// ===== ERROR HANDLING =====
function showError(message) {
  console.error('💥 Error:', message);
  
  // Show error in UI
  showNotification(`Error: ${message}`, 'error');
  
  if (elements.grid) {
    elements.grid.innerHTML = `
      <div class="no-results" style="grid-column: 1 / -1;">
        <i class="fas fa-exclamation-triangle"></i>
        <h3>Error Loading Data</h3>
        <p>${message}</p>
        <div style="display: flex; gap: 1rem; margin-top: 1rem;">
          <button onclick="location.reload()" class="btn-action btn-primary">
            <i class="fas fa-redo"></i> Reload Page
          </button>
          <button onclick="refreshData()" class="btn-action btn-secondary">
            <i class="fas fa-sync-alt"></i> Retry
          </button>
        </div>
      </div>
    `;
  }
  
  if (elements.pageLoader) {
    elements.pageLoader.classList.add('hide');
  }
}

// ===== PERFORMANCE OPTIMIZATIONS =====
// Debounce function for expensive operations
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Throttle function for scroll events
function throttle(func, limit) {
  let inThrottle;
  return function() {
    const args = arguments;
    const context = this;
    if (!inThrottle) {
      func.apply(context, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}

// Image lazy loading helper
function lazyLoadImages() {
  const images = document.querySelectorAll('img[loading="lazy"]');
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        img.src = img.dataset.src;
        observer.unobserve(img);
      }
    });
  });
  
  images.forEach(img => {
    if (img.dataset.src) {
      observer.observe(img);
    }
  });
}

// Virtual scrolling for large datasets
function setupVirtualScroll() {
  const grid = elements.grid;
  if (!grid || filteredData.length < 100) return;
  
  let visibleItems = 50;
  let startIndex = 0;
  
  function renderVisibleItems() {
    const visibleData = filteredData.slice(startIndex, startIndex + visibleItems);
    grid.innerHTML = '';
    
    const fragment = document.createDocumentFragment();
    visibleData.forEach(nft => {
      const card = createCard(nft);
      fragment.appendChild(card);
    });
    
    grid.appendChild(fragment);
    cards = Array.from(grid.querySelectorAll('.card'));
  }
  
  // Update on scroll
  window.addEventListener('scroll', throttle(() => {
    const scrollPosition = window.scrollY;
    const viewportHeight = window.innerHeight;
    const gridTop = grid.offsetTop;
    const gridHeight = grid.offsetHeight;
    
    if (scrollPosition + viewportHeight > gridTop + gridHeight * 0.7) {
      startIndex = Math.min(startIndex + 20, filteredData.length - visibleItems);
      renderVisibleItems();
    }
  }, 100));
}

// ===== LOCAL STORAGE FOR USER PREFERENCES =====
function saveUserPreferences() {
  const preferences = {
    selectedGifts: Array.from(selectedGifts),
    modelFilter: elements.modelFilter?.value || '',
    symbolFilter: elements.symbolFilter?.value || '',
    bgFilter: elements.bgFilter?.value || '',
    maxPrice: elements.maxPrice?.value || '',
    currentSort: currentSort,
    currentFilter: currentFilter
  };
  
  localStorage.setItem('winedashPreferences', JSON.stringify(preferences));
}

function loadUserPreferences() {
  try {
    const saved = localStorage.getItem('winedashPreferences');
    if (!saved) return;
    
    const preferences = JSON.parse(saved);
    
    // Restore selected gifts
    if (preferences.selectedGifts && Array.isArray(preferences.selectedGifts)) {
      preferences.selectedGifts.forEach(gift => addGiftBubble(gift));
    }
    
    // Restore filter values
    if (elements.modelFilter && preferences.modelFilter) {
      elements.modelFilter.value = preferences.modelFilter;
    }
    
    if (elements.symbolFilter && preferences.symbolFilter) {
      elements.symbolFilter.value = preferences.symbolFilter;
    }
    
    if (elements.bgFilter && preferences.bgFilter) {
      elements.bgFilter.value = preferences.bgFilter;
    }
    
    if (elements.maxPrice && preferences.maxPrice) {
      elements.maxPrice.value = preferences.maxPrice;
    }
    
    // Restore sort and filter
    currentSort = preferences.currentSort || 'newest';
    currentFilter = preferences.currentFilter || 'all';
    
    // Apply restored preferences
    filterData();
    setActiveFilterButton(currentFilter);
    
  } catch (error) {
    console.error('Failed to load preferences:', error);
  }
}

// Update initialization to load preferences
document.addEventListener('DOMContentLoaded', async () => {
  console.log('🚀 Initializing WINEDASH GIFT Marketplace...');
  updateLoaderStatus('Checking dependencies...');
  
  // Initialize event listeners
  initEventListeners();
  
  // Load user preferences
  loadUserPreferences();
  
  // Load data with progress indication
  await loadDataWithProgress();
  
  // Setup performance optimizations
  lazyLoadImages();
  setupVirtualScroll();
  
  // Final setup
  setTimeout(() => {
    updateLoaderStatus('Ready!');
    setTimeout(() => {
      elements.pageLoader.classList.add('hide');
    }, 500);
  }, 300);
});

// Save preferences before page unload
window.addEventListener('beforeunload', saveUserPreferences);

// Auto-save preferences periodically
setInterval(saveUserPreferences, 30 * 1000); // Every 30 seconds

// ===== EXPORT FUNCTIONS FOR GLOBAL ACCESS =====
window.openNFTDetailPanel = openNFTDetailPanel;
window.closePanel = closePanel;
window.clearAllFilters = clearAllFilters;
window.refreshData = refreshData;
window.shareNFT = shareNFT;

// Debug helper
window.debug = {
  getData: () => giftsData,
  getFilteredData: () => filteredData,
  getSelectedGifts: () => Array.from(selectedGifts),
  getStats: () => ({
    total: giftsData.length,
    filtered: filteredData.length,
    selected: selectedGifts.size,
    currentSort,
    currentFilter
  }),
  reset: () => {
    clearAllFilters();
    localStorage.clear();
    location.reload();
  }
};

console.log('✅ WINEDASH GIFT Marketplace initialized successfully!');
