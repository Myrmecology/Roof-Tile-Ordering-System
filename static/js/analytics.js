/* ============================================================
   ROOF TILE ORDERING SYSTEM — Analytics Page Utilities
   ============================================================ */


/* ══════════════════════════════════════════════════════════
   METRIC FORMATTERS
══════════════════════════════════════════════════════════ */

/**
 * Format a large number into a compact label
 * e.g. 1500 → "1.5k", 1200000 → "1.2M"
 * @param {number} value
 * @returns {string}
 */
function compactNumber(value) {
    if (value >= 1_000_000) return (value / 1_000_000).toFixed(1) + 'M';
    if (value >= 1_000)     return (value / 1_000).toFixed(1) + 'k';
    return String(Math.round(value));
}

/**
 * Format a number as a percentage string
 * @param {number} value   0–100
 * @param {number} digits  decimal places
 * @returns {string}
 */
function pctStr(value, digits = 1) {
    return parseFloat(value || 0).toFixed(digits) + '%';
}

/**
 * Calculate gross margin from revenue and cost
 * @param {number} revenue
 * @param {number} cost
 * @returns {number} margin percentage
 */
function grossMargin(revenue, cost) {
    if (!revenue || revenue <= 0) return 0;
    return ((revenue - cost) / revenue) * 100;
}

/**
 * Calculate average order value
 * @param {number} totalRevenue
 * @param {number} orderCount
 * @returns {number}
 */
function avgOrderValue(totalRevenue, orderCount) {
    if (!orderCount || orderCount <= 0) return 0;
    return totalRevenue / orderCount;
}


/* ══════════════════════════════════════════════════════════
   CHART COLOR PALETTE
   Extended palette for multi-series charts
══════════════════════════════════════════════════════════ */

const CHART_PALETTE = {
    amber:    { solid: '#F59E0B', faded: 'rgba(245,158,11,0.7)',  ghost: 'rgba(245,158,11,0.12)' },
    green:    { solid: '#34D399', faded: 'rgba(52,211,153,0.7)',  ghost: 'rgba(52,211,153,0.12)' },
    blue:     { solid: '#60A5FA', faded: 'rgba(96,165,250,0.7)',  ghost: 'rgba(96,165,250,0.12)' },
    purple:   { solid: '#A78BFA', faded: 'rgba(167,139,250,0.7)', ghost: 'rgba(167,139,250,0.12)' },
    pink:     { solid: '#F472B6', faded: 'rgba(244,114,182,0.7)', ghost: 'rgba(244,114,182,0.12)' },
    yellow:   { solid: '#FBBF24', faded: 'rgba(251,191,36,0.7)',  ghost: 'rgba(251,191,36,0.12)' },
    steel:    { solid: '#94A3B8', faded: 'rgba(148,163,184,0.5)', ghost: 'rgba(148,163,184,0.08)' },
    hazard:   { solid: '#EF4444', faded: 'rgba(239,68,68,0.7)',   ghost: 'rgba(239,68,68,0.12)' }
};

/**
 * Get an array of solid chart colors in order
 * @param {number} count
 * @returns {string[]}
 */
function getPaletteColors(count) {
    const keys   = Object.keys(CHART_PALETTE);
    const colors = [];
    for (let i = 0; i < count; i++) {
        colors.push(CHART_PALETTE[keys[i % keys.length]].solid);
    }
    return colors;
}

/**
 * Get faded versions of palette colors
 * @param {number} count
 * @returns {string[]}
 */
function getPaletteFaded(count) {
    const keys   = Object.keys(CHART_PALETTE);
    const colors = [];
    for (let i = 0; i < count; i++) {
        colors.push(CHART_PALETTE[keys[i % keys.length]].faded);
    }
    return colors;
}


/* ══════════════════════════════════════════════════════════
   TRANSACTION CLASSIFIER
══════════════════════════════════════════════════════════ */

/**
 * Return display properties for a transaction type
 * @param {string} type
 * @returns {object} { label, color, prefix, badgeHtml }
 */
function transactionDisplay(type) {
    const map = {
        sale: {
            label:     'Sale',
            color:     'var(--success)',
            prefix:    '+',
            badgeHtml: '<span class="badge badge-fulfilled">Sale</span>'
        },
        restock: {
            label:     'Restock',
            color:     'var(--hazard)',
            prefix:    '−',
            badgeHtml: '<span class="badge" style="color:#60A5FA;background:rgba(96,165,250,0.1);border-color:#60A5FA;">Restock</span>'
        },
        profit: {
            label:     'Profit',
            color:     'var(--amber)',
            prefix:    '+',
            badgeHtml: '<span class="badge badge-pending">Profit</span>'
        }
    };
    return map[type] || {
        label:     type,
        color:     'var(--steel)',
        prefix:    '',
        badgeHtml: `<span class="badge">${type}</span>`
    };
}


/* ══════════════════════════════════════════════════════════
   RUNNING BALANCE CALCULATOR
   Takes a list of transactions and computes running balance
══════════════════════════════════════════════════════════ */

/**
 * Add a running balance field to a transactions array
 * Assumes transactions are oldest-first
 * @param {array}  transactions
 * @param {number} startingBalance
 * @returns {array} with runningBalance field added
 */
function addRunningBalance(transactions, startingBalance = 50000) {
    let balance = startingBalance;
    return [...transactions].reverse().map(tx => {
        if (tx.transaction_type === 'sale') balance += tx.amount;
        else if (tx.transaction_type === 'restock') balance -= tx.amount;
        return { ...tx, runningBalance: balance };
    }).reverse();
}


/* ══════════════════════════════════════════════════════════
   DATE RANGE HELPERS
══════════════════════════════════════════════════════════ */

/**
 * Get an array of date strings for the last N days
 * @param {number} days
 * @returns {string[]} ISO date strings YYYY-MM-DD
 */
function lastNDays(days = 7) {
    const dates = [];
    for (let i = days - 1; i >= 0; i--) {
        const d = new Date();
        d.setDate(d.getDate() - i);
        dates.push(d.toISOString().split('T')[0]);
    }
    return dates;
}

/**
 * Fill gaps in daily volume data with zero entries
 * @param {array}  data   Array of { date, order_count, revenue }
 * @param {number} days
 * @returns {array}       Complete array with all days filled
 */
function fillDailyGaps(data, days = 7) {
    const byDate = {};
    data.forEach(d => { byDate[d.date] = d; });

    return lastNDays(days).map(date => byDate[date] || {
        date,
        order_count: 0,
        revenue:     0
    });
}

/**
 * Format a date string to short month-day label
 * @param {string} dateStr YYYY-MM-DD
 * @returns {string} e.g. "Apr 22"
 */
function shortDateLabel(dateStr) {
    if (!dateStr) return '—';
    return new Date(dateStr + 'T00:00:00').toLocaleDateString('en-US', {
        month: 'short',
        day:   'numeric'
    });
}


/* ══════════════════════════════════════════════════════════
   REVENUE SUMMARY BUILDER
   Build a human readable revenue summary
══════════════════════════════════════════════════════════ */

/**
 * Build a formatted revenue summary object
 * @param {object} summary  API analytics summary response
 * @param {object} budget   API budget response
 * @returns {object}
 */
function buildRevenueSummary(summary, budget) {
    const margin = summary.total_revenue > 0
        ? (summary.total_profit / summary.total_revenue) * 100
        : 0;

    const aov = summary.fulfilled_orders > 0
        ? summary.total_revenue / summary.fulfilled_orders
        : 0;

    return {
        revenue:         summary.total_revenue   || 0,
        profit:          summary.total_profit    || 0,
        margin:          margin,
        totalOrders:     summary.total_orders    || 0,
        fulfilledOrders: summary.fulfilled_orders || 0,
        pendingOrders:   summary.pending_orders  || 0,
        aov,
        balance:         budget.balance          || 0,
        totalSpent:      budget.total_spent      || 0,
        totalEarned:     budget.total_earned     || 0
    };
}


/* ══════════════════════════════════════════════════════════
   EXPORT TO CSV
   Export analytics data as a downloadable CSV
══════════════════════════════════════════════════════════ */

/**
 * Convert an array of objects to a CSV string
 * @param {array}    rows
 * @param {string[]} columns
 * @returns {string}
 */
function toCSV(rows, columns) {
    const header = columns.join(',');
    const lines  = rows.map(row =>
        columns.map(col => {
            const val = row[col] ?? '';
            const str = String(val).replace(/"/g, '""');
            return str.includes(',') ? `"${str}"` : str;
        }).join(',')
    );
    return [header, ...lines].join('\n');
}

/**
 * Trigger a CSV download in the browser
 * @param {string} csvString
 * @param {string} filename
 */
function downloadCSV(csvString, filename = 'export.csv') {
    const blob = new Blob([csvString], { type: 'text/csv;charset=utf-8;' });
    const url  = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href     = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

/**
 * Export transaction history as CSV
 * @param {array} transactions
 */
function exportTransactionsCSV(transactions) {
    const rows = transactions.map(tx => ({
        id:          tx.id,
        type:        tx.transaction_type,
        description: tx.description,
        amount:      tx.amount.toFixed(2),
        balance:     tx.balance_after.toFixed(2),
        date:        tx.created_at
    }));
    const csv = toCSV(rows, [
        'id', 'type', 'description',
        'amount', 'balance', 'date'
    ]);
    downloadCSV(csv, `transactions-${new Date().toISOString().split('T')[0]}.csv`);
    showToast('order_fulfilled', 'Export Complete',
              'Transaction history downloaded as CSV.');
}


/* ══════════════════════════════════════════════════════════
   ANALYTICS REFRESH SCHEDULER
   Smart refresh that backs off when tab is hidden
══════════════════════════════════════════════════════════ */

class AnalyticsRefresher {
    constructor(refreshFn, intervalMs = 30000) {
        this.refreshFn  = refreshFn;
        this.intervalMs = intervalMs;
        this.timer      = null;
        this.paused     = false;
    }

    start() {
        this.stop();
        this.timer = setInterval(() => {
            if (!this.paused && document.visibilityState === 'visible') {
                this.refreshFn();
            }
        }, this.intervalMs);
    }

    stop() {
        if (this.timer) {
            clearInterval(this.timer);
            this.timer = null;
        }
    }

    pause()  { this.paused = true; }
    resume() { this.paused = false; }

    forceRefresh() { this.refreshFn(); }
}


/* ══════════════════════════════════════════════════════════
   INIT LOG
══════════════════════════════════════════════════════════ */
console.log('%c [Analytics Module Loaded] ',
    'background:#1A2332;color:#F59E0B;font-size:10px;');