// ==========================================================================
// HDX 2.5 NATIVE ENGINE CONTROLLER & UI APPLICATION
// ==========================================================================

let isEngineRunning = false;
let isFullAuto = false;
let autoCycleTimer = null;
let tomCountdownTimer = null;
let tomSecondsLeft = 0;

// Farm State
const farmState = {
  level: 82,
  coins: 1420890,
  diamonds: 148,
  barnCurrent: 385,
  barnMax: 500,
  siloCurrent: 190,
  siloMax: 500,
  harvests: 144,
  animalColl: 72,
  products: 58,
  diamondsMined: 4,
  snipedTools: 12
};

// Item Catalog with Max Default Prices
const catalog = [
  { id: 'wheat', name: 'Wheat', cat: 'silo', lvl: 1, stock: 85, keep: 20, maxPrice: 36, unitBox: 10 },
  { id: 'corn', name: 'Corn', cat: 'silo', lvl: 2, stock: 45, keep: 15, maxPrice: 72, unitBox: 10 },
  { id: 'carrot', name: 'Carrot', cat: 'silo', lvl: 9, stock: 30, keep: 10, maxPrice: 72, unitBox: 10 },
  { id: 'soybean', name: 'Soybean', cat: 'silo', lvl: 5, stock: 30, keep: 10, maxPrice: 108, unitBox: 10 },
  { id: 'sugarcane', name: 'Sugar Cane', cat: 'silo', lvl: 7, stock: 0, keep: 10, maxPrice: 144, unitBox: 10 },
  { id: 'bread', name: 'Bread', cat: 'barn', lvl: 2, stock: 12, keep: 5, maxPrice: 216, unitBox: 10 },
  { id: 'cream', name: 'Cream', cat: 'barn', lvl: 6, stock: 8, keep: 4, maxPrice: 504, unitBox: 10 },
  { id: 'butter', name: 'Butter', cat: 'barn', lvl: 9, stock: 6, keep: 4, maxPrice: 828, unitBox: 10 },
  { id: 'cheese', name: 'Cheese', cat: 'barn', lvl: 12, stock: 5, keep: 3, maxPrice: 1224, unitBox: 10 },
  { id: 'brown_sugar', name: 'Brown Sugar', cat: 'barn', lvl: 7, stock: 10, keep: 4, maxPrice: 504, unitBox: 10 },
  { id: 'white_sugar', name: 'White Sugar', cat: 'barn', lvl: 13, stock: 8, keep: 4, maxPrice: 828, unitBox: 10 },
  { id: 'saw', name: 'Saw', cat: 'barn', lvl: 5, stock: 14, keep: 10, maxPrice: 210, unitBox: 1 },
  { id: 'axe', name: 'Axe', cat: 'barn', lvl: 5, stock: 22, keep: 10, maxPrice: 180, unitBox: 1 },
  { id: 'dynamite', name: 'Dynamite', cat: 'barn', lvl: 24, stock: 18, keep: 10, maxPrice: 250, unitBox: 1 },
  { id: 'tnt', name: 'TNT Barrel', cat: 'barn', lvl: 24, stock: 9, keep: 5, maxPrice: 360, unitBox: 1 },
  { id: 'shovel', name: 'Shovel', cat: 'barn', lvl: 24, stock: 11, keep: 5, maxPrice: 280, unitBox: 1 },
  { id: 'pickaxe', name: 'Pickaxe', cat: 'barn', lvl: 24, stock: 16, keep: 10, maxPrice: 420, unitBox: 1 },
  { id: 'land_deed', name: 'Land Deed', cat: 'expansion', lvl: 22, stock: 8, keep: 0, maxPrice: 403, unitBox: 1 },
  { id: 'mallet', name: 'Mallet', cat: 'expansion', lvl: 22, stock: 6, keep: 0, maxPrice: 403, unitBox: 1 },
  { id: 'marker_stake', name: 'Marker Stake', cat: 'expansion', lvl: 22, stock: 12, keep: 0, maxPrice: 403, unitBox: 1 },
  { id: 'bolt', name: 'Bolt', cat: 'expansion', lvl: 1, stock: 4, keep: 0, maxPrice: 270, unitBox: 1 },
  { id: 'plank', name: 'Plank', cat: 'expansion', lvl: 1, stock: 9, keep: 0, maxPrice: 270, unitBox: 1 },
  { id: 'duct_tape', name: 'Duct Tape', cat: 'expansion', lvl: 1, stock: 5, keep: 0, maxPrice: 270, unitBox: 1 }
];

// 17 Production Machines
const machinesList = [
  { name: 'Bakery', slots: '5/5 Slots', recipe: 'Bread x3, Cookie x2', icon: '🍞' },
  { name: 'Dairy', slots: '5/5 Slots', recipe: 'Butter x3, Cheese x2', icon: '🧈' },
  { name: 'Sugar Mill', slots: '5/5 Slots', recipe: 'White Sugar x5', icon: '🍬' },
  { name: 'Feed Mill #1', slots: '4/4 Slots', recipe: 'Cow Feed x4', icon: '🌾' },
  { name: 'Feed Mill #2', slots: '4/4 Slots', recipe: 'Chicken Feed x4', icon: '🌾' },
  { name: 'Popcorn Pot', slots: '4/4 Slots', recipe: 'Buttered Popcorn x3', icon: '🍿' },
  { name: 'BBQ Grill', slots: '4/4 Slots', recipe: 'Pancake x2, Bacon Egg x2', icon: '🥩' },
  { name: 'Pie Oven', slots: '4/4 Slots', recipe: 'Carrot Pie x2, Apple Pie x2', icon: '🥧' },
  { name: 'Loom', slots: '4/4 Slots', recipe: 'Blue Sweater x3', icon: '🧶' },
  { name: 'Sewing Machine', slots: '4/4 Slots', recipe: 'Cotton Shirt x2', icon: '👕' },
  { name: 'Cake Oven', slots: '4/4 Slots', recipe: 'Cheesecake x2', icon: '🎂' },
  { name: 'Smelter #1', slots: '3/3 Slots', recipe: 'Gold Bar (Running)', icon: '🥇' },
  { name: 'Smelter #2', slots: '3/3 Slots', recipe: 'Silver Bar (Running)', icon: '🥈' },
  { name: 'Smelter #3', slots: '3/3 Slots', recipe: 'Iron Bar (Running)', icon: '🔩' },
  { name: 'Smelter #4', slots: '3/3 Slots', recipe: 'Platinum Bar (Running)', icon: '🪙' },
  { name: 'Smelter #5', slots: '3/3 Slots', recipe: 'Coal Bar (Running)', icon: '🪨' },
  { name: 'Juice Press', slots: '4/4 Slots', recipe: 'Carrot Juice x3', icon: '🧃' }
];

// Truck Orders (9 Board Slots)
const truckOrders = [
  { id: 1, req: '6x Wheat, 4x Corn', coins: 140, xp: 85, ready: true },
  { id: 2, req: '3x Carrot Pie, 2x Cream', coins: 420, xp: 210, ready: true },
  { id: 3, req: '4x Bread, 2x Butter', coins: 260, xp: 130, ready: true },
  { id: 4, req: '8x Brown Sugar, 3x Popcorn', coins: 510, xp: 280, ready: false },
  { id: 5, req: '5x Soybean, 4x Bacon', coins: 340, xp: 190, ready: true },
  { id: 6, req: '2x Blue Sweater, 1x Cheese', coins: 620, xp: 350, ready: false },
  { id: 7, req: '10x Wheat, 6x Carrot', coins: 190, xp: 110, ready: true },
  { id: 8, req: '3x Pancake, 2x Buttered Popcorn', coins: 480, xp: 240, ready: false },
  { id: 9, req: '2x Gold Bar, 1x Silver Bar', coins: 780, xp: 450, ready: true }
];

// 2D Map State
let selectedTile = { x: 50688, y: 4608, col: 12, row: 8 };
let placedTiles = [];

// ==========================================================================
// DOM INITIALIZATION
// ==========================================================================
document.addEventListener('DOMContentLoaded', () => {
  initEngineControls();
  initTeleportBar();
  initSubTabs();
  initMapCanvas();
  renderInventoryTable();
  renderMarketTable();
  renderTruckBoard();
  renderMachinesGrid();
  initTomErrandRunner();
  initFarmConfigModal();
  initQuickActions();
  initTerminalDock();
  log('⚡ HDX 2.5 Native UI loaded successfully. Ready for operation.', 'ready');
});

// ==========================================================================
// ENGINE CONTROLS & MASTER AUTO LOOP
// ==========================================================================
function initEngineControls() {
  const startBtn = document.getElementById('startEngineBtn');
  const stopBtn = document.getElementById('stopEngineBtn');
  const autoBtn = document.getElementById('masterAutoBtn');

  startBtn.addEventListener('click', () => {
    isEngineRunning = true;
    startBtn.disabled = true;
    stopBtn.disabled = false;
    log('▶️ HDX Native Automation Engine STARTED. Hooking LDPlayer emulator-5554.', 'success');
  });

  stopBtn.addEventListener('click', () => {
    isEngineRunning = false;
    startBtn.disabled = false;
    stopBtn.disabled = true;
    if (isFullAuto) toggleFullAuto();
    log('⏹️ HDX Native Automation Engine STOPPED.', 'info');
  });

  autoBtn.addEventListener('click', toggleFullAuto);
}

function toggleFullAuto() {
  isFullAuto = !isFullAuto;
  const autoBtn = document.getElementById('masterAutoBtn');
  const startBtn = document.getElementById('startEngineBtn');
  const stopBtn = document.getElementById('stopEngineBtn');

  if (isFullAuto) {
    isEngineRunning = true;
    startBtn.disabled = true;
    stopBtn.disabled = false;
    autoBtn.classList.add('running');
    autoBtn.querySelector('.btn-text').textContent = 'STOP FULL AUTO';
    log('⚡ 1-CLICK FULL AUTO ENGAGED: Executing 15-tab synchronized pipeline...', 'action');

    startAutoPipeline();
  } else {
    autoBtn.classList.remove('running');
    autoBtn.querySelector('.btn-text').textContent = '1-CLICK FULL AUTO';
    clearInterval(autoCycleTimer);
    log('⏹️ 1-Click Full Auto loop deactivated safely.', 'info');
  }
}

function startAutoPipeline() {
  autoCycleTimer = setInterval(() => {
    if (!isFullAuto) return;

    // Simulate multi-module execution
    farmState.harvests += 36;
    farmState.animalColl += 18;
    farmState.products += 14;
    farmState.coins += 420;
    if (farmState.diamondsMined < 10 && Math.random() > 0.5) {
      farmState.diamondsMined += 1;
      farmState.diamonds += 1;
      log(`💎 Smart Mine: Extracted 1x Diamond! (${farmState.diamondsMined}/10 Daily Cap)`, 'success');
    }
    if (farmState.snipedTools < 80 && Math.random() > 0.6) {
      farmState.snipedTools += 1;
      log(`📰 Newspaper Sniper: Sniped 1x Rare Expansion Material (${farmState.snipedTools}/80 Daily Cap)`, 'action');
    }

    updateOverviewStats();
    log('🌾 [Auto-Cycle] Harvested 36 crops, fed animals, queued mills, and collected roadside coins.', 'info');
  }, 4500);
}

function updateOverviewStats() {
  document.getElementById('statHarvest').textContent = farmState.harvests;
  document.getElementById('statAnimal').textContent = farmState.animalColl;
  document.getElementById('statProducts').textContent = farmState.products;
  document.getElementById('statDiamonds').textContent = farmState.diamondsMined;
}

// ==========================================================================
// INSTANT SCREEN JUMP / TELEPORT
// ==========================================================================
function initTeleportBar() {
  const teleportCoords = {
    home: { name: 'Home Farm (Area 1)', x: 0, y: 0 },
    fishing: { name: 'Fishing Lake (Area 4)', x: 10240, y: 4096 },
    town: { name: 'Town Station (Area 2)', x: -8192, y: 16384 },
    greg: { name: "Greg's Farm (#1)", x: 2048, y: 2048 },
    aitown: { name: 'AI Sanctuary Town (Area 5)', x: -16384, y: 8192 }
  };

  document.querySelectorAll('.teleport-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const dest = btn.getAttribute('data-dest');
      const target = teleportCoords[dest];
      if (target) {
        log(`🚀 [TELEPORT] Instant Screen Jump executed: Teleported to ${target.name} (coord: x=${target.x}, y=${target.y})`, 'action');
      }
    });
  });

  const visitBtn = document.getElementById('visitBtn');
  const visitInput = document.getElementById('visitPlayerId');
  visitBtn.addEventListener('click', () => {
    const id = visitInput.value.trim();
    if (id) {
      log(`🚀 [TELEPORT] Visiting Player Farm: #${id}... Camera smoothly transitioned.`, 'action');
    } else {
      log('⚠️ Please enter a Player ID or tag to visit.', 'warning');
    }
  });
}

// ==========================================================================
// 15 SUB-TABS SWITCHER
// ==========================================================================
function initSubTabs() {
  const tabButtons = document.querySelectorAll('.subtab-btn');
  const tabPanels = document.querySelectorAll('.tab-panel');

  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetTab = btn.getAttribute('data-tab');
      tabButtons.forEach(b => b.classList.remove('active'));
      tabPanels.forEach(p => p.classList.remove('active'));

      btn.classList.add('active');
      const panel = document.getElementById(`tab-${targetTab}`);
      if (panel) panel.classList.add('active');

      if (targetTab === 'map') {
        redrawMapCanvas();
      }
    });
  });
}

// ==========================================================================
// 2. MAP TAB - 2D INTERACTIVE TILE CANVAS
// ==========================================================================
function initMapCanvas() {
  const canvas = document.getElementById('farmMapCanvas');
  const ctx = canvas.getContext('2d');
  const coordDisplay = document.getElementById('mapSelectedCoord');
  const placeBtn = document.getElementById('placeSelectedBtn');
  const clearBtn = document.getElementById('clearSelectionBtn');
  const placerSelect = document.getElementById('objectPlacerSelect');

  // Pre-place some sample objects on the farm map
  placedTiles.push({ col: 10, row: 6, type: 'banana_tree', label: '🍌' });
  placedTiles.push({ col: 11, row: 6, type: 'banana_tree', label: '🍌' });
  placedTiles.push({ col: 12, row: 6, type: 'apple_tree', label: '🍎' });
  placedTiles.push({ col: 14, row: 8, type: 'land', label: '🌾' });
  placedTiles.push({ col: 15, row: 8, type: 'land', label: '🌾' });
  placedTiles.push({ col: 8, row: 10, type: 'chicken_coop', label: '🐔' });
  placedTiles.push({ col: 10, row: 12, type: 'bakery', label: '🍞' });

  redrawMapCanvas();

  canvas.addEventListener('click', (e) => {
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    const mouseX = (e.clientX - rect.left) * scaleX;
    const mouseY = (e.clientY - rect.top) * scaleY;

    // Convert screen coordinates to isometric grid
    const col = Math.floor(mouseX / 40);
    const row = Math.floor(mouseY / 28);
    const worldX = 50688 + (col - 12) * 256;
    const worldY = 4608 + (row - 8) * 256;

    selectedTile = { x: worldX, y: worldY, col, row };
    coordDisplay.textContent = `selected x=${worldX} y=${worldY}`;
    redrawMapCanvas();
    log(`📍 [MAP] Selected tile at grid (${col}, ${row}) -> world coord x=${worldX} y=${worldY}`, 'info');
  });

  placeBtn.addEventListener('click', () => {
    const objType = placerSelect.value;
    const icons = {
      land: '🌾',
      banana_tree: '🍌',
      apple_tree: '🍎',
      cherry_tree: '🍒',
      raspberry_bush: '🫐',
      blackberry_bush: '🍇',
      chicken_coop: '🐔',
      cow_pasture: '🐮',
      bakery: '🍞',
      dairy: '🧈',
      decoration: '🗿'
    };
    placedTiles.push({
      col: selectedTile.col,
      row: selectedTile.row,
      type: objType,
      label: icons[objType] || '📦'
    });
    redrawMapCanvas();
    log(`🏗️ [MAP] Placed ${objType} at x=${selectedTile.x}, y=${selectedTile.y}`, 'success');
  });

  clearBtn.addEventListener('click', () => {
    placedTiles = placedTiles.filter(t => !(t.col === selectedTile.col && t.row === selectedTile.row));
    redrawMapCanvas();
    log(`🧹 [MAP] Cleared object at x=${selectedTile.x}, y=${selectedTile.y}`, 'info');
  });
}

function redrawMapCanvas() {
  const canvas = document.getElementById('farmMapCanvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Background Farm Ground
  ctx.fillStyle = '#141e17';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // Draw Grid Lines
  ctx.strokeStyle = 'rgba(46, 160, 67, 0.2)';
  ctx.lineWidth = 1;
  for (let x = 0; x < canvas.width; x += 40) {
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, canvas.height);
    ctx.stroke();
  }
  for (let y = 0; y < canvas.height; y += 28) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(canvas.width, y);
    ctx.stroke();
  }

  // Draw Placed Objects
  ctx.font = '16px sans-serif';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  placedTiles.forEach(tile => {
    const px = tile.col * 40 + 20;
    const py = tile.row * 28 + 14;
    ctx.fillStyle = 'rgba(57, 197, 207, 0.25)';
    ctx.fillRect(tile.col * 40 + 2, tile.row * 28 + 2, 36, 24);
    ctx.fillText(tile.label, px, py);
  });

  // Highlight Selected Tile
  if (selectedTile) {
    ctx.strokeStyle = '#e3b341';
    ctx.lineWidth = 2;
    ctx.strokeRect(selectedTile.col * 40, selectedTile.row * 28, 40, 28);
    ctx.fillStyle = 'rgba(227, 179, 65, 0.2)';
    ctx.fillRect(selectedTile.col * 40, selectedTile.row * 28, 40, 28);
  }
}

// ==========================================================================
// 3. INVENTORY TAB
// ==========================================================================
function renderInventoryTable(filter = 'all', search = '') {
  const tbody = document.getElementById('inventoryTableBody');
  if (!tbody) return;
  tbody.innerHTML = '';

  const filtered = catalog.filter(item => {
    const matchCat = filter === 'all' || item.cat === filter;
    const matchSearch = item.name.toLowerCase().includes(search.toLowerCase());
    return matchCat && matchSearch;
  });

  filtered.forEach(item => {
    const surplus = Math.max(0, item.stock - item.keep);
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><strong>${item.name}</strong></td>
      <td><span class="version">${item.cat.toUpperCase()}</span></td>
      <td>${item.stock}</td>
      <td>500</td>
      <td>🪙 ${item.maxPrice}</td>
      <td>${item.keep}</td>
      <td style="color: ${surplus > 0 ? '#3fb950' : '#8b949e'}">${surplus}</td>
      <td>
        <button class="action-btn small ${surplus > 0 ? 'success' : ''}" data-id="${item.id}" ${surplus === 0 ? 'disabled' : ''}>
          ${surplus > 0 ? `Sell ${surplus}` : 'No Surplus'}
        </button>
      </td>
    `;
    tbody.appendChild(tr);
  });

  // Attach filter handlers
  document.querySelectorAll('.inv-filter-btn').forEach(btn => {
    btn.onclick = () => {
      document.querySelectorAll('.inv-filter-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      renderInventoryTable(btn.getAttribute('data-filter'), document.getElementById('inventorySearch').value);
    };
  });

  const searchInput = document.getElementById('inventorySearch');
  searchInput.oninput = (e) => {
    const activeFilter = document.querySelector('.inv-filter-btn.active').getAttribute('data-filter');
    renderInventoryTable(activeFilter, e.target.value);
  };

  const sellAllBtn = document.getElementById('sellAllSurplusBtn');
  sellAllBtn.onclick = () => {
    let soldCount = 0;
    catalog.forEach(item => {
      const s = Math.max(0, item.stock - item.keep);
      if (s > 0) {
        soldCount += s;
        item.stock -= s;
      }
    });
    renderInventoryTable();
    renderMarketTable();
    log(`📦 [MARKET] Sold all surplus inventory: ${soldCount} items listed in Roadside Shop with anti-ban pricing!`, 'success');
  };
}

// ==========================================================================
// 4. MARKET TAB (ROADSIDE SHOP)
// ==========================================================================
function renderMarketTable() {
  const tbody = document.getElementById('marketTableBody');
  if (!tbody) return;
  tbody.innerHTML = '';

  const preset = document.getElementById('marketPricingPreset').value;

  catalog.slice(0, 12).forEach(item => {
    let priceBox = item.maxPrice;
    if (preset === 'antiban') {
      priceBox = Math.max(1, item.maxPrice - Math.floor(Math.random() * 3) - 1);
    } else if (preset === '75percent') {
      priceBox = Math.round(item.maxPrice * 0.75);
    } else if (preset === 'half') {
      priceBox = Math.round(item.maxPrice * 0.5);
    } else if (preset === 'lowest') {
      priceBox = 1;
    }

    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><strong>${item.name}</strong></td>
      <td>${item.lvl}</td>
      <td>${item.stock}</td>
      <td>${item.unitBox}</td>
      <td>${item.keep}</td>
      <td>🪙 ${priceBox}</td>
      <td><span class="text-success">Ready to List</span></td>
    `;
    tbody.appendChild(tr);
  });

  const presetSelect = document.getElementById('marketPricingPreset');
  presetSelect.onchange = () => {
    renderMarketTable();
    log(`🏷️ [MARKET] Pricing preset switched to: ${presetSelect.options[presetSelect.selectedIndex].text}`, 'info');
  };
}

// ==========================================================================
// 5. TOM ERRAND RUNNER
// ==========================================================================
function initTomErrandRunner() {
  const dispatchBtn = document.getElementById('dispatchTomBtn');
  const collectBtn = document.getElementById('collectTomBtn');
  const statusText = document.getElementById('tomStatusText');
  const timerDisplay = document.getElementById('tomTimerDisplay');
  const itemSelect = document.getElementById('tomItemSelect');

  // Chip buttons
  document.querySelectorAll('.tom-chips .chip-btn').forEach(btn => {
    btn.onclick = () => {
      document.querySelectorAll('.tom-chips .chip-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
    };
  });

  dispatchBtn.onclick = () => {
    const count = document.querySelector('.tom-chips .chip-btn.active').getAttribute('data-count');
    const itemName = itemSelect.options[itemSelect.selectedIndex].text;

    statusText.textContent = `Tom is running errand for ${count} ${itemName}...`;
    statusText.previousElementSibling.className = 'status-indicator-dot ready';
    log(`🏃 [TOM] Dispatched Tom for ${count}x ${itemName}. Searching prices...`, 'action');

    // Simulate errand arrival after 3s
    setTimeout(() => {
      statusText.textContent = `Tom has found 9x ${itemName} at the lowest price! Parcel ready.`;
      log(`🎁 [TOM] Tom arrived with parcel: 9x ${itemName}! Click 'Collect Delivered Items'.`, 'success');
    }, 3000);
  };

  collectBtn.onclick = () => {
    statusText.textContent = 'Tom is sleeping (Resting for 2 hours)...';
    statusText.previousElementSibling.className = 'status-indicator-dot';
    log('✅ [TOM] Collected items into Barn! Tom entered nap cycle.', 'success');

    // Start 2h countdown
    tomSecondsLeft = 7200;
    clearInterval(tomCountdownTimer);
    tomCountdownTimer = setInterval(() => {
      tomSecondsLeft--;
      if (tomSecondsLeft <= 0) {
        clearInterval(tomCountdownTimer);
        timerDisplay.textContent = '00:00:00';
        statusText.textContent = 'Tom is Awake & Ready for Errands';
        statusText.previousElementSibling.className = 'status-indicator-dot ready';
      } else {
        const hrs = String(Math.floor(tomSecondsLeft / 3600)).padStart(2, '0');
        const mins = String(Math.floor((tomSecondsLeft % 3600) / 60)).padStart(2, '0');
        const secs = String(tomSecondsLeft % 60).padStart(2, '0');
        timerDisplay.textContent = `${hrs}:${mins}:${secs}`;
      }
    }, 1000);
  };
}

// ==========================================================================
// 9. TRUCK ORDERS BOARD
// ==========================================================================
function renderTruckBoard() {
  const grid = document.getElementById('truckBoardGrid');
  if (!grid) return;
  grid.innerHTML = '';

  truckOrders.forEach(order => {
    const card = document.createElement('div');
    card.className = 'truck-order-card';
    card.innerHTML = `
      <div class="order-header">
        <span>Order #${order.id}</span>
        <span style="color: ${order.ready ? '#3fb950' : '#f85149'}">${order.ready ? 'READY' : 'WAITING'}</span>
      </div>
      <div class="order-items">${order.req}</div>
      <div class="order-rewards">
        <span>🪙 ${order.coins} Coins</span>
        <span>⭐ ${order.xp} XP</span>
      </div>
      <div style="display: flex; gap: 6px;">
        <button class="action-btn small ${order.ready ? 'success' : ''}" ${!order.ready ? 'disabled' : ''} onclick="sendSingleTruck(${order.id})">
          Send Truck
        </button>
        <button class="action-btn small danger" onclick="trashSingleTruck(${order.id})">
          🗑️ Trash
        </button>
      </div>
    `;
    grid.appendChild(card);
  });

  const sendAllBtn = document.getElementById('sendTruckBtn');
  sendAllBtn.onclick = () => {
    truckOrders.filter(o => o.ready).forEach(o => {
      farmState.coins += o.coins;
      o.ready = false;
    });
    renderTruckBoard();
    log('🚚 [TRUCK] Sent all ready delivery trucks! Rewards collected.', 'success');
  };

  const trashBtn = document.getElementById('trashTruckBtn');
  trashBtn.onclick = () => {
    truckOrders.filter(o => !o.ready).forEach(o => {
      o.req = 'Re-rolled Order (30m cooldown)';
    });
    renderTruckBoard();
    log('🗑️ [TRUCK] Trashed unwanted truck orders. Reroll timers started.', 'info');
  };
}

window.sendSingleTruck = (id) => {
  const o = truckOrders.find(x => x.id === id);
  if (o && o.ready) {
    farmState.coins += o.coins;
    o.ready = false;
    renderTruckBoard();
    log(`🚚 [TRUCK] Order #${id} dispatched! +${o.coins} Coins, +${o.xp} XP collected.`, 'success');
  }
};

window.trashSingleTruck = (id) => {
  const o = truckOrders.find(x => x.id === id);
  if (o) {
    o.ready = false;
    o.req = 'Re-rolled Order (30m cooldown)';
    renderTruckBoard();
    log(`🗑️ [TRUCK] Order #${id} removed from board. New order in 30 mins.`, 'info');
  }
};

// ==========================================================================
// 10. MACHINES GRID
// ==========================================================================
function renderMachinesGrid() {
  const grid = document.getElementById('machinesGrid');
  if (!grid) return;
  grid.innerHTML = '';

  machinesList.forEach(m => {
    const card = document.createElement('div');
    card.className = 'machine-card';
    card.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <span class="machine-name">${m.icon} ${m.name}</span>
        <span class="machine-slots">${m.slots}</span>
      </div>
      <div style="font-size: 11px; color: #8b949e; margin: 4px 0;">Queue: ${m.recipe}</div>
      <div class="machine-queue">
        <div class="queue-slot">1</div>
        <div class="queue-slot">2</div>
        <div class="queue-slot">3</div>
        <div class="queue-slot">4</div>
      </div>
    `;
    grid.appendChild(card);
  });
}

// ==========================================================================
// QUICK ACTIONS & CHOP CONFIRMATION
// ==========================================================================
function initQuickActions() {
  document.querySelectorAll('.quick-action-btn').forEach(btn => {
    btn.onclick = () => {
      const act = btn.getAttribute('data-action');
      if (act === 'harvest') {
        farmState.harvests += 36;
        updateOverviewStats();
        log('🌾 Harvested 36 fields and replanted wheat/corn with anti-ban jitter.', 'success');
      } else if (act === 'animals') {
        farmState.animalColl += 18;
        updateOverviewStats();
        log('🥛 Collected all animal products and restocked feed mill queues.', 'success');
      } else if (act === 'collect_shop') {
        farmState.coins += 2150;
        log('💰 Collected 2,150 coins from sold Roadside Shop boxes.', 'success');
      } else if (act === 'maintenance') {
        log('📬 Farm Maintenance: Claimed mailbox gift, spun wheel of fortune, claimed daily quest.', 'success');
      }
    };
  });

  // Trees Buttons
  const chopDeadBtn = document.getElementById('treesChopDeadBtn');
  const chopAllBtn = document.getElementById('treesChopAllBtn');
  const chopModal = document.getElementById('chopConfirmModal');
  const cancelChop = document.getElementById('cancelChopBtn');
  const confirmChop = document.getElementById('confirmChopBtn');
  const closeChop = document.getElementById('closeChopModalBtn');

  chopDeadBtn.onclick = () => {
    log('🪓 [TREES] Used 5 saws & 8 axes to clear dead trees and withered bushes.', 'success');
  };

  chopAllBtn.onclick = () => {
    chopModal.classList.remove('hidden');
  };

  cancelChop.onclick = () => chopModal.classList.add('hidden');
  closeChop.onclick = () => chopModal.classList.add('hidden');
  confirmChop.onclick = () => {
    chopModal.classList.add('hidden');
    log('🪓 [TREES] CHOP ALL EXECUTED: Cleared all 115 orchard trees & bushes using saws and axes.', 'danger');
  };

  // Mine button
  document.getElementById('mineNowBtn').onclick = () => {
    farmState.diamondsMined += 2;
    farmState.diamonds += 2;
    updateOverviewStats();
    log('⛏️ [MINE] Completed mining run: 16 ores extracted, 2 diamonds collected.', 'success');
  };

  // Fishing button
  document.getElementById('fishLakeNowBtn').onclick = () => {
    log('🎣 [FISHING] Area 4 Lake: Collected 6 fish, 4 lobsters, reset all 18 traps, and returned home.', 'success');
  };
}

// ==========================================================================
// FARM CONFIG MODAL (12 MODULES)
// ==========================================================================
function initFarmConfigModal() {
  const modal = document.getElementById('farmConfigModal');
  const openBtn = document.getElementById('openFarmConfigBtn');
  const closeBtn = document.getElementById('closeFarmConfigBtn');
  const inspector = document.getElementById('configInspectorPane');

  openBtn.onclick = () => {
    modal.classList.remove('hidden');
    renderConfigModule('chores');
  };

  closeBtn.onclick = () => modal.classList.add('hidden');

  document.querySelectorAll('.config-nav-item').forEach(item => {
    item.onclick = () => {
      document.querySelectorAll('.config-nav-item').forEach(i => i.classList.remove('active'));
      item.classList.add('active');
      renderConfigModule(item.getAttribute('data-module'));
    };
  });

  document.getElementById('saveConfigBtn').onclick = () => {
    modal.classList.add('hidden');
    log('⚙️ [CONFIG] Farm configuration settings saved and synchronized with Rust engine.', 'success');
  };
}

function renderConfigModule(moduleName) {
  const inspector = document.getElementById('configInspectorPane');
  if (!inspector) return;

  const configs = {
    chores: `
      <div class="inspector-title">Chores & Daily Maintenance</div>
      <div class="inspector-desc">Automated daily farm chores and free gifts</div>
      <div class="config-section">
        <div class="config-row">
          <span>Open Daily Mystery Box</span>
          <input type="checkbox" checked>
        </div>
        <div class="config-row">
          <span>Spin Wheel of Fortune Daily</span>
          <input type="checkbox" checked>
        </div>
        <div class="config-row">
          <span>Claim Mailbox Catalog Rewards</span>
          <input type="checkbox" checked>
        </div>
        <div class="config-row">
          <span>Claim Farm Pass Perks</span>
          <input type="checkbox" checked>
        </div>
      </div>
    `,
    fields: `
      <div class="inspector-title">Fields & Crop Production</div>
      <div class="inspector-desc">Crop balancing, replanting ratios, and field priorities</div>
      <div class="config-section">
        <div class="config-row">
          <span>Target Wheat Proportion (%):</span>
          <input type="number" value="50" class="num-input">
        </div>
        <div class="config-row">
          <span>Target Corn Proportion (%):</span>
          <input type="number" value="30" class="num-input">
        </div>
        <div class="config-row">
          <span>Target Soybeans (%):</span>
          <input type="number" value="20" class="num-input">
        </div>
      </div>
    `,
    production: `
      <div class="inspector-title">Production & Queue Balancing</div>
      <div class="inspector-desc">Manage machine slots and missing ingredient prevention</div>
      <div class="config-section">
        <div class="config-row">
          <span>Auto-fill all 17 machines:</span>
          <input type="checkbox" checked>
        </div>
        <div class="config-row">
          <span>Queue depth per machine:</span>
          <input type="number" value="4" class="num-input">
        </div>
        <div class="config-row">
          <span>Never spend diamonds on missing ingredients:</span>
          <input type="checkbox" checked disabled>
        </div>
      </div>
    `,
    animals: `
      <div class="inspector-title">Animals & Feed Mills</div>
      <div class="inspector-desc">Auto-chain animal feed after collection</div>
      <div class="config-section">
        <div class="config-row">
          <span>Produce missing feed automatically:</span>
          <input type="checkbox" checked>
        </div>
        <div class="config-row">
          <span>Extra feed to keep in stock:</span>
          <input type="number" value="0" class="num-input">
        </div>
      </div>
    `,
    truck: `
      <div class="inspector-title">Truck Orders Filter</div>
      <div class="inspector-desc">Order trash thresholds and minimum coin reward ratios</div>
      <div class="config-section">
        <div class="config-row">
          <span>Trash orders with coins < :</span>
          <input type="number" value="200" class="num-input">
        </div>
        <div class="config-row">
          <span>Auto-send ready trucks:</span>
          <input type="checkbox" checked>
        </div>
      </div>
    `,
    market: `
      <div class="inspector-title">Roadside Shop Config</div>
      <div class="inspector-desc">Listing intervals, slot expansion, and coin collection</div>
      <div class="config-section">
        <div class="config-row">
          <span>Collect coins from sold listings:</span>
          <input type="checkbox" checked>
        </div>
        <div class="config-row">
          <span>Free ad interval (seconds):</span>
          <input type="number" value="300" class="num-input">
        </div>
      </div>
    `,
    newspaper: `
      <div class="inspector-title">Newspaper Sniper Config</div>
      <div class="inspector-desc">Safety daily cap and auto-buy speeds</div>
      <div class="config-section">
        <div class="config-row">
          <span>Daily expansion tools cap:</span>
          <input type="number" value="80" class="num-input" disabled>
        </div>
        <div class="config-row">
          <span>Visit sellers automatically:</span>
          <input type="checkbox" checked>
        </div>
      </div>
    `,
    visitors: `
      <div class="inspector-title">Farm Visitors</div>
      <div class="inspector-desc">Handle town visitors walking up to your porch</div>
      <div class="config-section">
        <div class="config-row">
          <span>Sell high-stock crops to visitors:</span>
          <input type="checkbox" checked>
        </div>
        <div class="config-row">
          <span>Decline visitors asking for rare items:</span>
          <input type="checkbox" checked>
        </div>
      </div>
    `,
    mine: `
      <div class="inspector-title">Mine Config</div>
      <div class="inspector-desc">Daily diamond limits and tool priority order</div>
      <div class="config-section">
        <div class="config-row">
          <span>Max diamonds per day:</span>
          <input type="number" value="10" class="num-input">
        </div>
        <div class="config-row">
          <span>Auto-load Smelters:</span>
          <input type="checkbox" checked>
        </div>
      </div>
    `,
    trees: `
      <div class="inspector-title">Trees & Honey Config</div>
      <div class="inspector-desc">Orchard harvesting and bee nectar collection</div>
      <div class="config-section">
        <div class="config-row">
          <span>Collect honey from Beehive Tree:</span>
          <input type="checkbox" checked>
        </div>
        <div class="config-row">
          <span>Request help on 3rd harvest (!):</span>
          <input type="checkbox" checked>
        </div>
      </div>
    `,
    fishing: `
      <div class="inspector-title">Fishing Lake Config</div>
      <div class="inspector-desc">Area 4 navigation and duck/lobster equipment</div>
      <div class="config-section">
        <div class="config-row">
          <span>Collect and reset lobster traps:</span>
          <input type="checkbox" checked>
        </div>
        <div class="config-row">
          <span>Produce red lures automatically:</span>
          <input type="checkbox" checked>
        </div>
      </div>
    `,
    expansion: `
      <div class="inspector-title">Farm Expansion Automation</div>
      <div class="inspector-desc">Automated plot unlocking when materials are met</div>
      <div class="config-section">
        <div class="config-row">
          <span>Auto-unlock Barn capacity when ready:</span>
          <input type="checkbox" checked>
        </div>
        <div class="config-row">
          <span>Auto-unlock Silo capacity when ready:</span>
          <input type="checkbox" checked>
        </div>
        <div class="config-row">
          <span>Auto-expand Land plots:</span>
          <input type="checkbox" checked>
        </div>
      </div>
    `
  };

  inspector.innerHTML = configs[moduleName] || '<div>Select a module</div>';
}

// ==========================================================================
// TERMINAL LOG DOCK
// ==========================================================================
function initTerminalDock() {
  const clearBtn = document.getElementById('clearLogsBtn');
  const copyBtn = document.getElementById('copyLogsBtn');
  const terminalBody = document.getElementById('terminalBody');

  clearBtn.onclick = () => {
    terminalBody.innerHTML = '<div class="log-entry info">[LOGS CLEARED]</div>';
  };

  copyBtn.onclick = () => {
    const text = Array.from(terminalBody.children).map(c => c.textContent).join('\n');
    navigator.clipboard.writeText(text).then(() => {
      log('📋 Copied all logs to clipboard.', 'info');
    });
  };
}

function log(message, type = 'info') {
  const terminalBody = document.getElementById('terminalBody');
  if (!terminalBody) return;
  const entry = document.createElement('div');
  entry.className = `log-entry ${type}`;
  const now = new Date().toTimeString().split(' ')[0];
  entry.textContent = `[${now}] ${message}`;
  terminalBody.appendChild(entry);

  if (document.getElementById('chkAutoScroll').checked) {
    terminalBody.scrollTop = terminalBody.scrollHeight;
  }
}
