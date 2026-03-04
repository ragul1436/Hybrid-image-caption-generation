// ─── Hybrid Image Caption Generator ── app.js ───
// Shared utilities used across all Jinja2 templates

const API_BASE = '';  // same origin

// ─── Auth helpers ───────────────────────────────

function getToken() {
    return localStorage.getItem('token');
}

function setToken(token) {
    localStorage.setItem('token', token);
}

function clearToken() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
}

function getUser() {
    try {
        return JSON.parse(localStorage.getItem('user'));
    } catch {
        return null;
    }
}

function setUser(user) {
    localStorage.setItem('user', JSON.stringify(user));
}

/**
 * Redirect to /login if no token found.
 * Call at the top of every protected page's DOMContentLoaded.
 */
function requireAuth() {
    if (!getToken()) {
        window.location.href = '/login';
    }
}

/**
 * Redirect away from auth pages if already logged in.
 */
function redirectIfLoggedIn(target = '/dashboard') {
    if (getToken()) {
        window.location.href = target;
    }
}

// ─── API fetch wrapper ──────────────────────────

/**
 * Wrapper around fetch() that auto-attaches the Bearer token.
 * Returns the raw Response object (caller should check .ok, .json(), etc.)
 *
 * @param {string} url - API path, e.g. '/api/v1/images/'
 * @param {RequestInit} options - fetch options (method, body, headers …)
 * @returns {Promise<Response>}
 */
async function apiFetch(url, options = {}) {
    const token = getToken();
    const headers = options.headers ? { ...options.headers } : {};

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    // Default Content-Type to JSON unless body is FormData
    if (options.body && !(options.body instanceof FormData) && !headers['Content-Type']) {
        headers['Content-Type'] = 'application/json';
    }

    const res = await fetch(`${API_BASE}${url}`, {
        ...options,
        headers,
    });

    // Auto-logout on 401
    if (res.status === 401) {
        clearToken();
        window.location.href = '/login';
        throw new Error('Unauthorized');
    }

    return res;
}

// ─── Toast notifications ────────────────────────

/**
 * Show a toast notification.
 *
 * @param {string} message
 * @param {'success'|'error'|'info'} type
 * @param {number} duration - ms before auto-dismiss (default 3000)
 */
function showToast(message, type = 'info', duration = 3000) {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const colorMap = {
        success: 'bg-green-600',
        error: 'bg-red-600',
        info: 'bg-indigo-600',
    };

    const iconMap = {
        success: `<svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"/></svg>`,
        error: `<svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z"/></svg>`,
        info: `<svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m11.25 11.25.041-.02a.75.75 0 0 1 1.063.852l-.708 2.836a.75.75 0 0 0 1.063.853l.041-.021M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9-3.75h.008v.008H12V8.25Z"/></svg>`,
    };

    const toast = document.createElement('div');
    toast.className = `${colorMap[type] || colorMap.info} text-white px-4 py-3 rounded-lg shadow-lg flex items-center gap-3 toast-enter max-w-sm`;
    toast.innerHTML = `
        ${iconMap[type] || iconMap.info}
        <span class="text-sm font-medium flex-1">${message}</span>
        <button onclick="dismissToast(this.parentElement)" class="text-white/70 hover:text-white">
            <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12"/></svg>
        </button>
    `;

    container.appendChild(toast);

    if (duration > 0) {
        setTimeout(() => dismissToast(toast), duration);
    }
}

function dismissToast(el) {
    if (!el || !el.parentElement) return;
    el.classList.remove('toast-enter');
    el.classList.add('toast-exit');
    el.addEventListener('animationend', () => el.remove());
}

// ─── UI Toggles ─────────────────────────────────

function toggleUserMenu() {
    const menu = document.getElementById('user-menu');
    if (menu) {
        menu.classList.toggle('hidden');
    }
}

function toggleMobileMenu() {
    const menu = document.getElementById('mobile-menu');
    if (menu) {
        menu.classList.toggle('hidden');
    }
}

// Close user menu when clicking outside
document.addEventListener('click', (e) => {
    const menu = document.getElementById('user-menu');
    const btn = document.getElementById('user-menu-btn');
    if (menu && btn && !btn.contains(e.target) && !menu.contains(e.target)) {
        menu.classList.add('hidden');
    }
});

// ─── Logout ─────────────────────────────────────

function handleLogout() {
    clearToken();
    showToast('Logged out successfully', 'success');
    setTimeout(() => {
        window.location.href = '/login';
    }, 300);
}

// ─── Utility helpers ────────────────────────────

/**
 * Format a date string for display.
 */
function formatDate(dateStr) {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
}

/**
 * Format file size in human-readable form.
 */
function formatFileSize(bytes) {
    if (!bytes) return '0 B';
    const units = ['B', 'KB', 'MB', 'GB'];
    let i = 0;
    let size = bytes;
    while (size >= 1024 && i < units.length - 1) {
        size /= 1024;
        i++;
    }
    return `${size.toFixed(1)} ${units[i]}`;
}

/**
 * Debounce a function call.
 */
function debounce(fn, delay = 300) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => fn(...args), delay);
    };
}

/**
 * Truncate text to a max length.
 */
function truncate(str, max = 100) {
    if (!str) return '';
    return str.length > max ? str.slice(0, max) + '…' : str;
}

// ─── Navbar active link highlighting ────────────

document.addEventListener('DOMContentLoaded', () => {
    const path = window.location.pathname;
    document.querySelectorAll('nav a[href]').forEach(link => {
        const href = link.getAttribute('href');
        if (href === path || (href !== '/' && path.startsWith(href))) {
            link.classList.add('text-white', 'bg-slate-700');
            link.classList.remove('text-slate-300');
        }
    });

    // Set username in navbar
    const user = getUser();
    const userNameEl = document.getElementById('user-name');
    if (user && userNameEl) {
        userNameEl.textContent = user.name || user.email || 'User';
    }
});
