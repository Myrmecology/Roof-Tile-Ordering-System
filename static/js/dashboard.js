/* ============================================================
   ROOF TILE ORDERING SYSTEM — Global Dashboard Utilities
   Shared helpers, formatters and UI utilities
   Available on every page via base.html
   ============================================================ */


/* ══════════════════════════════════════════════════════════
   FORMAT HELPERS
══════════════════════════════════════════════════════════ */

/**
 * Format a number as USD currency
 * @param {number} value
 * @returns {string} e.g. "$1,234.56"
 */
function formatCurrency(value) {
    return '$' + parseFloat(value || 0).toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

/**
 * Format a number with thousands separator
 * @param {number} value
 * @returns {string} e.g. "1,234"
 */
function formatNumber(value) {
    return parseInt(value || 0).toLocaleString('en-US');
}

/**
 * Format a datetime string to short readable format
 * @param {string} dateStr
 * @returns {string} e.g. "Apr 22, 14:35"
 */
function formatDateTime(dateStr) {
    if (!dateStr) return '—';
    return new Date(dateStr).toLocaleString('en-US', {
        month:  'short',
        day:    'numeric',
        hour:   '2-digit',
        minute: '2-digit'
    });
}

/**
 * Format a datetime string to date only
 * @param {string} dateStr
 * @returns {string} e.g. "Apr 22, 2026"
 */
function formatDate(dateStr) {
    if (!dateStr) return '—';
    return new Date(dateStr).toLocaleDateString('en-US', {
        month: 'short',
        day:   'numeric',
        year:  'numeric'
    });
}

/**
 * Format seconds into mm:ss countdown
 * @param {number} seconds
 * @returns {string} e.g. "1:30"
 */
function formatCountdown(seconds) {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${String(s).padStart(2, '0')}`;
}

/**
 * Truncate a string to a max length
 * @param {string} str
 * @param {number} max
 * @returns {string}
 */
function truncate(str, max = 30) {
    if (!str) return '—';
    return str.length > max ? str.substring(0, max - 1) + '…' : str;
}

/**
 * Zero-pad a number to a given width
 * @param {number} n
 * @param {number} width
 * @returns {string} e.g. "007"
 */
function zeroPad(n, width = 3) {
    return String(n).padStart(width, '0');
}


/* ══════════════════════════════════════════════════════════
   STATUS BADGE GENERATORS
══════════════════════════════════════════════════════════ */

/**
 * Generate an order status badge HTML string
 * @param {string} status
 * @returns {string} HTML
 */
function orderStatusBadge(status) {
    const map = {
        pending:     '<span class="badge badge-pending">Pending</span>',
        fulfilled:   '<span class="badge badge-fulfilled">Fulfilled</span>',
        cancelled:   '<span class="badge badge-cancelled">Cancelled</span>',
        backordered: '<span class="badge badge-backordered">Backorder</span>'
    };
    return map[status] || `<span class="badge">${status}</span>`;
}

/**
 * Generate a customer type badge HTML string
 * @param {string} type
 * @returns {string} HTML
 */
function customerTypeBadge(type) {
    const map = {
        company:    '<span class="badge badge-company">Company</span>',
        individual: '<span class="badge badge-individual">Individual</span>'
    };
    return map[type] || `<span class="badge">${type}</span>`;
}

/**
 * Generate a stock status badge HTML string
 * @param {number} quantity
 * @param {number} reorderPoint
 * @returns {string} HTML
 */
function stockStatusBadge(quantity, reorderPoint) {
    if (quantity <= 5) {
        return '<span class="badge badge-low-stock low-stock-pulse">Critical</span>';
    } else if (quantity <= reorderPoint) {
        return '<span class="badge badge-low-stock">Low Stock</span>';
    }
    return '<span class="badge badge-ok">In Stock</span>';
}

/**
 * Generate a category pill HTML string
 * @param {string} category
 * @returns {string} HTML
 */
function categoryPill(category) {
    return `<span class="cat-pill ${category}">${category}</span>`;
}


/* ══════════════════════════════════════════════════════════
   DOM HELPERS
══════════════════════════════════════════════════════════ */

/**
 * Safely set the text content of an element by ID
 * @param {string} id
 * @param {string} value
 */
function setText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
}

/**
 * Safely set the inner HTML of an element by ID
 * @param {string} id
 * @param {string} html
 */
function setHTML(id, html) {
    const el = document.getElementById(id);
    if (el) el.innerHTML = html;
}

/**
 * Show an element by ID (sets display to block)
 * @param {string} id
 * @param {string} display
 */
function showEl(id, display = 'block') {
    const el = document.getElementById(id);
    if (el) el.style.display = display;
}

/**
 * Hide an element by ID
 * @param {string} id
 */
function hideEl(id) {
    const el = document.getElementById(id);
    if (el) el.style.display = 'none';
}

/**
 * Toggle a CSS class on an element
 * @param {string} id
 * @param {string} cls
 * @param {boolean} force
 */
function toggleClass(id, cls, force) {
    const el = document.getElementById(id);
    if (el) el.classList.toggle(cls, force);
}

/**
 * Render a skeleton loading row for a table
 * @param {number} cols
 * @param {number} rows
 * @returns {string} HTML
 */
function skeletonRows(cols = 5, rows = 4) {
    const cell = `
        <td style="padding:0.7rem 0.9rem;">
            <div class="skeleton skeleton-text"
                 style="width:${60 + Math.random() * 30}%;"></div>
        </td>`;
    const row  = `<tr>${cell.repeat(cols)}</tr>`;
    return row.repeat(rows);
}

/**
 * Render a centered empty state for a table
 * @param {number} cols
 * @param {string} message
 * @param {string} icon
 * @returns {string} HTML
 */
function emptyRow(cols = 5, message = 'No data found', icon = 'fa-box-open') {
    return `
        <tr>
            <td colspan="${cols}">
                <div class="empty-state">
                    <div class="empty-state-icon">
                        <i class="fas ${icon}"></i>
                    </div>
                    <div class="empty-state-text">${message}</div>
                </div>
            </td>
        </tr>`;
}

/**
 * Render a centered spinner for a table
 * @param {number} cols
 * @returns {string} HTML
 */
function loadingRow(cols = 5) {
    return `
        <tr>
            <td colspan="${cols}">
                <div class="empty-state" style="padding:2rem;">
                    <div class="spinner"></div>
                </div>
            </td>
        </tr>`;
}


/* ══════════════════════════════════════════════════════════
   API HELPERS
══════════════════════════════════════════════════════════ */

/**
 * Perform a GET request and return parsed JSON
 * Returns null on error
 * @param {string} url
 * @returns {Promise<any|null>}
 */
async function apiGet(url) {
    try {
        const res = await fetch(url);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return await res.json();
    } catch (e) {
        console.error(`GET ${url} failed:`, e);
        return null;
    }
}

/**
 * Perform a POST request and return parsed JSON
 * Returns null on error
 * @param {string} url
 * @param {object|null} body
 * @returns {Promise<any|null>}
 */
async function apiPost(url, body = null) {
    try {
        const opts = {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' }
        };
        if (body) opts.body = JSON.stringify(body);
        const res = await fetch(url, opts);
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || `HTTP ${res.status}`);
        }
        return await res.json();
    } catch (e) {
        console.error(`POST ${url} failed:`, e);
        showToast('order_cancelled', 'Request Failed', e.message);
        return null;
    }
}


/* ══════════════════════════════════════════════════════════
   CHART HELPERS
══════════════════════════════════════════════════════════ */

/**
 * Standard Chart.js dark theme options
 * Merge with your specific chart options
 */
const CHART_THEME = {
    responsive:          true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            display:  true,
            position: 'top',
            labels: {
                color:     '#94A3B8',
                boxWidth:  10,
                boxHeight: 10,
                padding:   14,
                font: { family: "'Share Tech Mono', monospace", size: 10 }
            }
        },
        tooltip: {
            backgroundColor: '#1A2332',
            borderColor:     'rgba(245,158,11,0.3)',
            borderWidth:     1,
            titleColor:      '#F59E0B',
            bodyColor:       '#94A3B8',
            padding:         10,
            titleFont: { family: "'Barlow Condensed', sans-serif", size: 13, weight: '700' },
            bodyFont:  { family: "'Share Tech Mono', monospace", size: 11 }
        }
    },
    scales: {
        x: {
            grid:  { color: 'rgba(148,163,184,0.06)' },
            ticks: { color: '#475569', font: { size: 10 } }
        },
        y: {
            grid:  { color: 'rgba(148,163,184,0.06)' },
            ticks: { color: '#475569', font: { size: 10 } }
        }
    }
};

/**
 * Destroy a Chart.js instance safely
 * @param {Chart|null} chartInstance
 */
function destroyChart(chartInstance) {
    if (chartInstance && typeof chartInstance.destroy === 'function') {
        chartInstance.destroy();
    }
}

/**
 * Category color map for charts
 */
const CATEGORY_COLORS = {
    shingles:     '#F59E0B',
    tar:          '#A78BFA',
    gloves:       '#34D399',
    underlayment: '#F472B6',
    nails:        '#FBBF24',
    tools:        '#60A5FA'
};


/* ══════════════════════════════════════════════════════════
   CONFIRM DIALOG
══════════════════════════════════════════════════════════ */

/**
 * Show a styled confirmation dialog
 * Returns a Promise that resolves to true/false
 * @param {string} title
 * @param {string} message
 * @param {string} confirmLabel
 * @returns {Promise<boolean>}
 */
function confirmDialog(title, message, confirmLabel = 'Confirm') {
    return new Promise(resolve => {
        const existing = document.getElementById('confirm-dialog');
        if (existing) existing.remove();

        const dialog = document.createElement('div');
        dialog.id    = 'confirm-dialog';
        dialog.style.cssText = `
            position:fixed;inset:0;z-index:600;
            background:rgba(0,0,0,0.8);backdrop-filter:blur(4px);
            display:flex;align-items:center;justify-content:center;`;

        dialog.innerHTML = `
            <div style="background:var(--bg-panel);
                        border:1px solid var(--amber-border);
                        border-radius:4px;width:380px;
                        max-width:90vw;overflow:hidden;">
                <div style="height:2px;background:linear-gradient(90deg,
                     var(--amber-dim),var(--amber),transparent);"></div>
                <div style="padding:1.25rem;">
                    <div style="font-family:var(--font-display);
                                font-size:1.1rem;font-weight:800;
                                letter-spacing:0.06em;text-transform:uppercase;
                                color:var(--amber);margin-bottom:0.5rem;">
                        ${title}
                    </div>
                    <div style="font-size:0.82rem;color:var(--steel);
                                line-height:1.6;margin-bottom:1.25rem;">
                        ${message}
                    </div>
                    <div style="display:flex;gap:0.5rem;justify-content:flex-end;">
                        <button id="confirm-cancel"
                                class="btn btn-ghost btn-sm">Cancel</button>
                        <button id="confirm-ok"
                                class="btn btn-primary btn-sm">
                            ${confirmLabel}
                        </button>
                    </div>
                </div>
            </div>`;

        document.body.appendChild(dialog);

        document.getElementById('confirm-ok').onclick = () => {
            dialog.remove();
            resolve(true);
        };
        document.getElementById('confirm-cancel').onclick = () => {
            dialog.remove();
            resolve(false);
        };
        dialog.onclick = e => {
            if (e.target === dialog) { dialog.remove(); resolve(false); }
        };
    });
}


/* ══════════════════════════════════════════════════════════
   COPY TO CLIPBOARD
══════════════════════════════════════════════════════════ */

/**
 * Copy a string to the clipboard and show a toast
 * @param {string} text
 * @param {string} label
 */
async function copyToClipboard(text, label = 'Value') {
    try {
        await navigator.clipboard.writeText(text);
        showToast('order_fulfilled', 'Copied', `${label} copied to clipboard.`);
    } catch (e) {
        showToast('order_cancelled', 'Copy Failed', 'Could not access clipboard.');
    }
}


/* ══════════════════════════════════════════════════════════
   DEBOUNCE
══════════════════════════════════════════════════════════ */

/**
 * Debounce a function call
 * @param {Function} fn
 * @param {number} delay
 * @returns {Function}
 */
function debounce(fn, delay = 300) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => fn(...args), delay);
    };
}


/* ══════════════════════════════════════════════════════════
   LOCAL STATE — Lightweight page state manager
══════════════════════════════════════════════════════════ */

const AppState = (() => {
    const state = {};
    return {
        set(key, value)  { state[key] = value; },
        get(key, def)    { return key in state ? state[key] : def; },
        toggle(key)      { state[key] = !state[key]; return state[key]; },
        increment(key)   { state[key] = (state[key] || 0) + 1; return state[key]; },
        decrement(key)   { state[key] = Math.max(0, (state[key] || 0) - 1); return state[key]; },
        reset(key)       { delete state[key]; },
        dump()           { return { ...state }; }
    };
})();


/* ══════════════════════════════════════════════════════════
   KEYBOARD SHORTCUTS
══════════════════════════════════════════════════════════ */

document.addEventListener('keydown', e => {
    // ESC — close any open modal
    if (e.key === 'Escape') {
        document.querySelectorAll('[id$="-modal"]').forEach(el => {
            if (el.style.display === 'flex') el.style.display = 'none';
        });
        const confirmDlg = document.getElementById('confirm-dialog');
        if (confirmDlg) confirmDlg.remove();
    }

    // Ctrl/Cmd + R — prevent default browser refresh on dashboard
    // (we handle our own refresh)
    if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
        if (typeof loadAll === 'function') {
            e.preventDefault();
            loadAll();
            showToast('order_fulfilled', 'Refreshed', 'Dashboard data reloaded.');
        }
    }
});


/* ══════════════════════════════════════════════════════════
   PAGE VISIBILITY — Pause/resume on tab switch
══════════════════════════════════════════════════════════ */

document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') {
        // Refresh data when user returns to the tab
        if (typeof loadAll === 'function') {
            loadAll();
        } else if (typeof loadDashboard === 'function') {
            loadDashboard();
        }
    }
});


/* ══════════════════════════════════════════════════════════
   PROFIT COLOR HELPER
══════════════════════════════════════════════════════════ */

/**
 * Return a CSS color variable string based on profit value
 * @param {number} profit
 * @returns {string}
 */
function profitColor(profit) {
    if (profit > 0)  return 'var(--success)';
    if (profit < 0)  return 'var(--hazard)';
    return 'var(--steel-dim)';
}


/* ══════════════════════════════════════════════════════════
   STOCK LEVEL HELPERS
══════════════════════════════════════════════════════════ */

/**
 * Return a CSS color string based on stock vs reorder point
 * @param {number} quantity
 * @param {number} reorderPoint
 * @returns {string}
 */
function stockColor(quantity, reorderPoint) {
    if (quantity <= 5)            return 'var(--hazard)';
    if (quantity <= reorderPoint) return 'var(--amber)';
    return 'var(--success)';
}

/**
 * Calculate stock percentage of a safe max
 * @param {number} quantity
 * @param {number} maxQuantity
 * @returns {number} 0–100
 */
function stockPercent(quantity, maxQuantity = 300) {
    return Math.min(100, Math.max(0, (quantity / maxQuantity) * 100));
}


/* ══════════════════════════════════════════════════════════
   SCROLL TO TOP
══════════════════════════════════════════════════════════ */

/**
 * Smooth scroll the main content area to the top
 */
function scrollToTop() {
    const main = document.querySelector('.main-content');
    if (main) main.scrollTo({ top: 0, behavior: 'smooth' });
    window.scrollTo({ top: 0, behavior: 'smooth' });
}


/* ══════════════════════════════════════════════════════════
   INIT LOG
══════════════════════════════════════════════════════════ */
console.log(
    '%c ROOF TILE ORDERING SYSTEM ',
    'background:#F59E0B;color:#080B0F;font-weight:900;' +
    'font-size:13px;padding:4px 8px;border-radius:2px;',
    '\nJustin Computer Science — 2026'
);