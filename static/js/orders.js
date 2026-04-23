/* ============================================================
   ROOF TILE ORDERING SYSTEM — Orders Page Utilities
   ============================================================ */


/* ══════════════════════════════════════════════════════════
   ORDER SUMMARY BUILDER
   Builds a human readable summary string from an order object
══════════════════════════════════════════════════════════ */

/**
 * Build a plain text summary of an order for display
 * @param {object} order
 * @returns {string}
 */
function buildOrderSummary(order) {
    if (!order || !order.items) return 'No items';
    return order.items.map(item => {
        const name = item.inventory_item?.name || 'Unknown Item';
        const qty  = item.quantity_ordered;
        const unit = item.inventory_item?.unit || 'unit';
        return `${qty} ${unit}(s) of ${name}`;
    }).join(', ');
}


/* ══════════════════════════════════════════════════════════
   ORDER PROFIT MARGIN
   Calculate profit margin percentage for one order
══════════════════════════════════════════════════════════ */

/**
 * Calculate profit margin percentage
 * @param {number} profit
 * @param {number} total
 * @returns {string} e.g. "34.2%"
 */
function orderMargin(profit, total) {
    if (!total || total <= 0) return '—';
    return ((profit / total) * 100).toFixed(1) + '%';
}


/* ══════════════════════════════════════════════════════════
   ORDER AGE
   How long ago was an order placed
══════════════════════════════════════════════════════════ */

/**
 * Return a human readable age string for an order
 * @param {string} dateStr
 * @returns {string} e.g. "3 minutes ago"
 */
function orderAge(dateStr) {
    if (!dateStr) return '—';
    const diff = Math.floor((Date.now() - new Date(dateStr)) / 1000);
    if (diff < 60)   return `${diff}s ago`;
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return `${Math.floor(diff / 86400)}d ago`;
}


/* ══════════════════════════════════════════════════════════
   ORDER VALUE TIER
   Classify orders by value for visual priority
══════════════════════════════════════════════════════════ */

/**
 * Return a color based on order total value
 * @param {number} total
 * @returns {string} CSS color variable
 */
function orderValueColor(total) {
    if (total >= 5000)  return 'var(--amber-bright)';
    if (total >= 1000)  return 'var(--amber)';
    if (total >= 500)   return 'var(--steel-bright)';
    return 'var(--steel)';
}

/**
 * Return a tier label for an order total
 * @param {number} total
 * @returns {string}
 */
function orderValueTier(total) {
    if (total >= 5000) return 'HIGH VALUE';
    if (total >= 1000) return 'STANDARD';
    return 'SMALL';
}


/* ══════════════════════════════════════════════════════════
   BULK FULFILL PROGRESS
   Track progress during bulk order fulfillment
══════════════════════════════════════════════════════════ */

class BulkFulfillTracker {
    constructor(total) {
        this.total     = total;
        this.completed = 0;
        this.failed    = 0;
    }

    tick(success = true) {
        this.completed++;
        if (!success) this.failed++;
    }

    get percent() {
        return Math.round((this.completed / this.total) * 100);
    }

    get summary() {
        const ok   = this.completed - this.failed;
        return `${ok} fulfilled, ${this.failed} failed of ${this.total}`;
    }

    get isDone() {
        return this.completed >= this.total;
    }
}


/* ══════════════════════════════════════════════════════════
   ORDER FILTER STATE
   Persist filter/sort state across renders
══════════════════════════════════════════════════════════ */

const OrderFilters = (() => {
    let state = {
        status:   'all',
        sort:     'newest',
        page:     0,
        pageSize: 20
    };

    return {
        get status()   { return state.status; },
        get sort()     { return state.sort; },
        get page()     { return state.page; },
        get pageSize() { return state.pageSize; },

        setStatus(s)  { state.status = s; state.page = 0; },
        setSort(s)    { state.sort   = s; state.page = 0; },
        nextPage()    { state.page++; },
        prevPage()    { state.page = Math.max(0, state.page - 1); },
        resetPage()   { state.page = 0; },

        paginate(arr) {
            const start = state.page * state.pageSize;
            return arr.slice(start, start + state.pageSize);
        },

        pageInfo(total) {
            const start = state.page * state.pageSize;
            const end   = Math.min(start + state.pageSize, total);
            return { start, end, total,
                     hasPrev: state.page > 0,
                     hasNext: end < total };
        }
    };
})();


/* ══════════════════════════════════════════════════════════
   SORT ORDERS
   Reusable sort function for order arrays
══════════════════════════════════════════════════════════ */

/**
 * Sort an array of orders by a given strategy
 * @param {array}  orders
 * @param {string} strategy newest|oldest|highest|lowest
 * @returns {array}
 */
function sortOrders(orders, strategy = 'newest') {
    const sorted = [...orders];
    switch (strategy) {
        case 'newest':
            return sorted.sort((a, b) =>
                new Date(b.created_at) - new Date(a.created_at));
        case 'oldest':
            return sorted.sort((a, b) =>
                new Date(a.created_at) - new Date(b.created_at));
        case 'highest':
            return sorted.sort((a, b) => b.total_amount - a.total_amount);
        case 'lowest':
            return sorted.sort((a, b) => a.total_amount - b.total_amount);
        default:
            return sorted;
    }
}


/* ══════════════════════════════════════════════════════════
   INIT LOG
══════════════════════════════════════════════════════════ */
console.log('%c [Orders Module Loaded] ',
    'background:#1A2332;color:#F59E0B;font-size:10px;');