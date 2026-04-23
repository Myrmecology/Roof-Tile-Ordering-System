/* ============================================================
   ROOF TILE ORDERING SYSTEM — Inventory Page Utilities
   ============================================================ */


/* ══════════════════════════════════════════════════════════
   STOCK LEVEL BAR
   Render an inline SVG-style stock bar
══════════════════════════════════════════════════════════ */

/**
 * Generate a stock level progress bar HTML string
 * @param {number} quantity
 * @param {number} reorderPoint
 * @param {number} maxQty
 * @returns {string} HTML
 */
function stockBar(quantity, reorderPoint, maxQty = 300) {
    const pct      = Math.min(100, Math.max(0, (quantity / maxQty) * 100));
    const isCrit   = quantity <= 5;
    const isLow    = quantity <= reorderPoint;
    const cls      = isCrit ? 'critical' : isLow ? 'low' : 'ok';

    return `
        <div class="stock-bar-track">
            <div class="stock-bar-fill ${cls}"
                 style="width:${pct.toFixed(1)}%">
            </div>
        </div>`;
}


/* ══════════════════════════════════════════════════════════
   MARGIN CALCULATOR
   Compute sell margin from cost and sell price
══════════════════════════════════════════════════════════ */

/**
 * Calculate margin percentage from cost and sell price
 * @param {number} costPrice
 * @param {number} sellPrice
 * @returns {number} margin percentage
 */
function calcMargin(costPrice, sellPrice) {
    if (!sellPrice || sellPrice <= 0) return 0;
    return ((sellPrice - costPrice) / sellPrice) * 100;
}

/**
 * Format margin as a color-coded HTML string
 * @param {number} costPrice
 * @param {number} sellPrice
 * @returns {string} HTML
 */
function marginDisplay(costPrice, sellPrice) {
    const pct   = calcMargin(costPrice, sellPrice);
    const color = pct >= 40
        ? 'var(--success)'
        : pct >= 25
            ? 'var(--amber)'
            : 'var(--hazard)';
    return `<span style="font-family:var(--font-mono);
                         font-size:0.78rem;color:${color};">
                ${pct.toFixed(1)}%
            </span>`;
}


/* ══════════════════════════════════════════════════════════
   INVENTORY VALUE CALCULATOR
   Total value of inventory at cost or sell price
══════════════════════════════════════════════════════════ */

/**
 * Calculate total inventory value
 * @param {array}  items
 * @param {string} priceKey 'cost_price' | 'sell_price'
 * @returns {number}
 */
function totalInventoryValue(items, priceKey = 'sell_price') {
    return items.reduce((sum, item) =>
        sum + (item.quantity * (item[priceKey] || 0)), 0
    );
}

/**
 * Count items by category
 * @param {array} items
 * @returns {object} { category: count }
 */
function countByCategory(items) {
    return items.reduce((acc, item) => {
        acc[item.category] = (acc[item.category] || 0) + 1;
        return acc;
    }, {});
}

/**
 * Get all items below reorder point
 * @param {array} items
 * @returns {array}
 */
function getLowStockItems(items) {
    return items.filter(i => i.quantity <= i.reorder_point);
}

/**
 * Get all critical stock items (qty <= 5)
 * @param {array} items
 * @returns {array}
 */
function getCriticalItems(items) {
    return items.filter(i => i.quantity <= 5);
}


/* ══════════════════════════════════════════════════════════
   RESTOCK COST ESTIMATOR
   Estimate cost to bring all low stock to reorder_quantity
══════════════════════════════════════════════════════════ */

/**
 * Estimate total cost to restock all low stock items
 * @param {array} items  All inventory items
 * @returns {number}     Estimated restock cost
 */
function estimateRestockCost(items) {
    return getLowStockItems(items).reduce((sum, item) => {
        const needed = item.reorder_quantity - item.quantity;
        if (needed > 0) {
            sum += needed * item.cost_price;
        }
        return sum;
    }, 0);
}


/* ══════════════════════════════════════════════════════════
   CATEGORY SORTER
   Sort inventory by category then name
══════════════════════════════════════════════════════════ */

const CATEGORY_ORDER = [
    'shingles', 'tar', 'gloves',
    'underlayment', 'nails', 'tools'
];

/**
 * Sort inventory items by category order then alphabetically
 * @param {array} items
 * @returns {array}
 */
function sortInventory(items) {
    return [...items].sort((a, b) => {
        const catA = CATEGORY_ORDER.indexOf(a.category);
        const catB = CATEGORY_ORDER.indexOf(b.category);
        if (catA !== catB) return catA - catB;
        return a.name.localeCompare(b.name);
    });
}


/* ══════════════════════════════════════════════════════════
   RESTOCK ITEM BUILDER
   Build a restock order payload for the API
══════════════════════════════════════════════════════════ */

/**
 * Build a restock order payload from a list of items
 * @param {array}  items   Array of { inventory_item_id, quantity_ordered, unit_cost }
 * @param {string} notes   Optional notes
 * @returns {object}       API-ready payload
 */
function buildRestockPayload(items, notes = null) {
    return {
        notes,
        items: items.map(i => ({
            inventory_item_id: i.inventory_item_id,
            quantity_ordered:  parseInt(i.quantity_ordered),
            unit_cost:         parseFloat(i.unit_cost)
        }))
    };
}

/**
 * Calculate total cost of a restock item list
 * @param {array} items
 * @returns {number}
 */
function restockTotal(items) {
    return items.reduce(
        (sum, i) => sum + (i.quantity_ordered * i.unit_cost), 0
    );
}


/* ══════════════════════════════════════════════════════════
   SKU FORMATTER
   Format SKU strings for display
══════════════════════════════════════════════════════════ */

/**
 * Wrap a SKU in styled mono HTML
 * @param {string} sku
 * @returns {string} HTML
 */
function skuTag(sku) {
    return `<span style="font-family:var(--font-mono);
                         font-size:0.65rem;
                         color:var(--steel-dim);
                         letter-spacing:0.06em;">${sku}</span>`;
}


/* ══════════════════════════════════════════════════════════
   INIT LOG
══════════════════════════════════════════════════════════ */
console.log('%c [Inventory Module Loaded] ',
    'background:#1A2332;color:#F59E0B;font-size:10px;');