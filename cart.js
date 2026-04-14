/* ============================================================
   Cart — carrito cliente con localStorage
   Lee strings y moneda desde window.APP (definido en base.html)
   ============================================================ */

const Cart = (function () {
  const KEY = 'mvideo_cart_py';
  let items = JSON.parse(localStorage.getItem(KEY) || '[]');
  const S = (window.APP && window.APP.strings) || {};
  const CURRENCY = (window.APP && window.APP.currency) || 'PYG';
  const USD_RATE = (window.APP && window.APP.usdRate) || 7300;

  function save() {
    localStorage.setItem(KEY, JSON.stringify(items));
    updateBadge();
    renderDrawer();
  }

  function add(id, name, price, image) {
    const existing = items.find(i => i.id === id);
    if (existing) existing.qty += 1;
    else items.push({ id, name, price, image, qty: 1 });
    save();
    toast(S.added || 'Added');
  }

  function remove(id) {
    items = items.filter(i => i.id !== id);
    save();
  }

  function setQty(id, qty) {
    const item = items.find(i => i.id === id);
    if (!item) return;
    item.qty = Math.max(1, qty);
    save();
  }

  function clear() {
    items = [];
    save();
  }

  function total() {
    return items.reduce((s, i) => s + i.price * i.qty, 0);
  }

  function count() {
    return items.reduce((s, i) => s + i.qty, 0);
  }

  // Format price in PYG or USD depending on active currency
  function fmt(pyg) {
    if (CURRENCY === 'USD') {
      return 'US$ ' + (pyg / USD_RATE).toFixed(2);
    }
    return '₲ ' + Math.round(pyg).toLocaleString('es-PY').replace(/,/g, '.');
  }

  function updateBadge() {
    const badge = document.getElementById('cart-badge');
    const c = count();
    if (badge) {
      badge.textContent = c;
      badge.classList.toggle('hidden', c === 0);
    }
  }

  function renderDrawer() {
    const wrap = document.getElementById('cart-items');
    const totalEl = document.getElementById('cart-total');
    if (!wrap) return;

    if (items.length === 0) {
      wrap.innerHTML = `
        <div class="text-center text-gray-400 py-10">
          <div class="text-5xl mb-3">🛒</div>
          <p>${S.empty || 'Empty'}</p>
        </div>`;
      if (totalEl) totalEl.textContent = fmt(0);
      return;
    }

    wrap.innerHTML = items.map(i => `
      <div class="flex gap-3 items-center border-b border-gray-100 pb-3">
        <img src="${i.image || ''}" class="w-16 h-16 object-cover rounded bg-gray-100">
        <div class="flex-1 min-w-0">
          <div class="font-semibold text-sm truncate">${escapeHtml(i.name)}</div>
          <div class="text-sm text-brand font-bold">${fmt(i.price)}</div>
          <div class="flex items-center gap-2 mt-1">
            <button onclick="Cart.setQty(${i.id}, ${i.qty - 1})" class="w-6 h-6 rounded bg-gray-200 hover:bg-brand hover:text-white font-bold">−</button>
            <span class="text-sm font-semibold min-w-[20px] text-center">${i.qty}</span>
            <button onclick="Cart.setQty(${i.id}, ${i.qty + 1})" class="w-6 h-6 rounded bg-gray-200 hover:bg-brand hover:text-white font-bold">+</button>
          </div>
        </div>
        <button onclick="Cart.remove(${i.id})" class="text-gray-400 hover:text-brand text-xs">${S.remove || 'Remove'}</button>
      </div>
    `).join('');
    if (totalEl) totalEl.textContent = fmt(total());
  }

  function open() {
    renderDrawer();
    document.getElementById('cart-drawer').classList.remove('translate-x-full');
    document.getElementById('cart-overlay').classList.remove('hidden');
  }

  function close() {
    document.getElementById('cart-drawer').classList.add('translate-x-full');
    document.getElementById('cart-overlay').classList.add('hidden');
  }

  async function checkout() {
    if (items.length === 0) { toast(S.empty || 'Empty'); return; }
    try {
      const res = await fetch('/checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ items: items.map(i => ({ id: i.id, qty: i.qty })) }),
      });
      if (res.status === 401) {
        toast(S.loginFirst || 'Login first');
        setTimeout(() => window.location.href = '/login', 1000);
        return;
      }
      const data = await res.json();
      if (data.ok) {
        toast((S.orderPlaced || 'Ordered') + ' #' + data.order_id);
        clear();
        close();
        setTimeout(() => window.location.href = '/profile', 1500);
      } else {
        toast(data.error || (S.error || 'Error'));
      }
    } catch (e) {
      toast(S.error || 'Error');
    }
  }

  function toast(msg) {
    const el = document.getElementById('toast');
    if (!el) return;
    el.textContent = msg;
    el.classList.remove('opacity-0', 'translate-y-4');
    clearTimeout(el._t);
    el._t = setTimeout(() => el.classList.add('opacity-0', 'translate-y-4'), 2000);
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, c => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    }[c]));
  }

  document.addEventListener('DOMContentLoaded', () => {
    updateBadge();
    renderDrawer();
    const openBtn = document.getElementById('open-cart');
    const closeBtn = document.getElementById('close-cart');
    const overlay = document.getElementById('cart-overlay');
    const clearBtn = document.getElementById('clear-cart-btn');
    const checkoutBtn = document.getElementById('checkout-btn');
    if (openBtn) openBtn.addEventListener('click', open);
    if (closeBtn) closeBtn.addEventListener('click', close);
    if (overlay) overlay.addEventListener('click', close);
    if (clearBtn) clearBtn.addEventListener('click', () => {
      if (confirm(S.confirmClear || 'Clear?')) clear();
    });
    if (checkoutBtn) checkoutBtn.addEventListener('click', checkout);
  });

  return { add, remove, setQty, clear, total, count, open, close, checkout };
})();
