/* ============================================================
   PRIME DISH — Real-time notifications (polling, privacy-safe)
   - Polls /api/notifications/feed/ every 15s (role-aware on server).
   - Admins get: admin-private + public broadcasts (never customer privates).
   - Customers get: public broadcasts + ONLY their own private rows.
   - Toasts only genuinely NEW rows (tracked via latest_id).
   - Mark-read calls POST /mark_notification_read/ (per-user receipts
     for customers, global is_read only for admins — enforced server-side).
   Hooks (add to any bell/dropdown):
     [data-notif-badge]        -> unread count bubble (hidden when 0)
     [data-notif-list]         -> container to re-render rows into
     [data-notif-feed]         -> wrapper with data-latest-id="123"
     .mark-all-read            -> mark-all button
   ============================================================ */
(function () {
  const FEED_URL = '/api/notifications/feed/';
  const MARK_URL = '/mark_notification_read/';
  const POLL_MS = 15000;

  function getCookie(name) {
    const m = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return m ? m.pop() : '';
  }
  const csrftoken = getCookie('csrftoken');

  function toast(title, body, link) {
    // Reuse main.js showToast if present, else minimal fallback.
    if (window.showToast) {
      window.showToast(title + (body ? ' — ' + body.slice(0, 80) : ''), 'success', 'bi-bell-fill');
      return;
    }
    let c = document.querySelector('.toast-container');
    if (!c) { c = document.createElement('div'); c.className = 'toast-container'; document.body.appendChild(c); }
    const t = document.createElement('div');
    t.className = 'toast success';
    t.innerHTML = '<i class="bi bi-bell-fill"></i><span class="toast-msg"></span>';
    t.querySelector('.toast-msg').textContent = title;
    if (link) { t.style.cursor = 'pointer'; t.addEventListener('click', () => { window.location.href = link; }); }
    c.appendChild(t);
    setTimeout(() => { t.style.opacity = '0'; setTimeout(() => t.remove(), 300); }, 4500);
  }

  function iconFor(n) {
    const t = (n.title || '') + ' ' + (n.body || '');
    if (/order|deliver|track/i.test(t)) return { cls: 'order', icon: 'bi-bag-check-fill' };
    if (/payment|paid|paystack/i.test(t)) return { cls: 'payment', icon: 'bi-credit-card-2-front-fill' };
    if (/menu|rating|food|dish/i.test(t)) return { cls: 'food', icon: 'bi-egg-fried' };
    if (/user|account|regist|ban|block/i.test(t)) return { cls: 'user', icon: 'bi-person-fill' };
    return { cls: 'system', icon: 'fa-solid fa-bell' };
  }

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    }[c]));
  }

  function renderList(container, items) {
    if (!container) return;
    if (!items.length) {
      container.innerHTML = '<div class="notif-empty"><i class="bi bi-bell-slash"></i>You\'re all caught up.<br>No new notifications yet.</div>';
      return;
    }
    container.innerHTML = items.slice(0, 20).map((n) => {
      const ic = iconFor(n);
      const href = n.link_url ? esc(n.link_url) : (/(order|deliver)/i.test(n.title || '') ? '/orders' : '#');
      const unread = n.is_read ? '' : ' unread';
      const dot = n.is_read ? '' : '<span class="notif-dot"></span>';
      // Admin-private rows carry a lock so staff can tell at a glance.
      const lock = n.visibility === 'admin' ? ' <i class="bi bi-lock-fill" title="Admin only — customers can\'t see this" style="font-size:10px;opacity:.6"></i>' : '';
      return (
        '<a href="' + href + '" data-notif-id="' + n.id + '" class="notif-item' + unread + '">' +
          '<span class="notif-ico ' + ic.cls + '"><i class="bi ' + ic.icon + '"></i></span>' +
          '<span class="notif-body"><div class="notif-title">' + esc(n.title) + lock + '</div>' +
          '<div class="notif-text">' + esc(n.body) + '</div>' +
          '<div class="notif-time">' + esc(n.ago || '') + '</div></span>' + dot +
        '</a>'
      );
    }).join('');
    // single-click marks that row read (server enforces visibility)
    container.querySelectorAll('[data-notif-id]').forEach((a) => {
      a.addEventListener('click', () => {
        const id = a.getAttribute('data-notif-id');
        markOne(id);
        a.classList.remove('unread');
        const d = a.querySelector('.notif-dot');
        if (d) d.remove();
      }, { once: true });
    });
  }

  function updateBadges(count) {
    document.querySelectorAll('[data-notif-badge]').forEach((b) => {
      if (!count || count <= 0) { b.style.display = 'none'; b.textContent = ''; }
      else { b.style.display = ''; b.textContent = count > 99 ? '99+' : String(count); }
    });
    document.querySelectorAll('[data-notif-count]').forEach((c) => {
      c.textContent = String(count || 0);
    });
  }

  async function markOne(id) {
    try {
      await fetch(MARK_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'X-CSRFToken': csrftoken },
        body: 'id=' + encodeURIComponent(id),
      });
    } catch (e) { /* offline — ignore */ }
    poll(false);
  }

  async function markAll() {
    try {
      await fetch(MARK_URL, { method: 'POST', headers: { 'X-CSRFToken': csrftoken } });
    } catch (e) { /* ignore */ }
    document.querySelectorAll('[data-notif-list] .notif-item.unread').forEach((el) => {
      el.classList.remove('unread');
      const d = el.querySelector('.notif-dot');
      if (d) d.remove();
    });
    updateBadges(0);
  }

  let latestId = 0;
  let firstRun = true;
  try {
    const feed = document.querySelector('[data-notif-feed]');
    if (feed && feed.getAttribute('data-latest-id')) latestId = parseInt(feed.getAttribute('data-latest-id'), 10) || 0;
  } catch (e) {}

  async function poll(withToast = true) {
    // No bell on page (e.g. login) — skip.
    if (!document.querySelector('[data-notif-list]') && !document.querySelector('[data-notif-badge]')) return;
    let url = FEED_URL;
    if (latestId) url += '?since_id=' + latestId;
    let data;
    try {
      const res = await fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } });
      if (!res.ok) return;
      data = await res.json();
    } catch (e) { return; }

    updateBadges(data.unread_count);
    document.querySelectorAll('[data-notif-list]').forEach((c) => renderList(c, data.notifications || []));

    // Toast only rows that arrived AFTER page load (never replay history).
    if (withToast && !firstRun && data.new && data.new.length) {
      // Oldest first so toasts read in order.
      data.new.slice().reverse().forEach((n) => toast(n.title, n.body, n.link_url));
    }
    if (data.latest_id) latestId = data.latest_id;
    firstRun = false;
  }

  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.mark-all-read').forEach((b) => {
      b.addEventListener('click', (e) => { e.preventDefault(); e.stopPropagation(); markAll(); });
    });
    // Initial paint uses server HTML; first poll only sets latestId quietly.
    poll(false);
    setInterval(() => poll(true), POLL_MS);
    document.addEventListener('visibilitychange', () => { if (!document.hidden) poll(true); });
  });
})();
