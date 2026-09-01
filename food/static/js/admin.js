/* =============================================
   CHOPORA - ADMIN JAVASCRIPT
============================================= */

document.addEventListener('DOMContentLoaded', function () {

  // ---- Bar Chart ----
  const barChart = document.getElementById('bar-chart');
  if (barChart) {
    const data = [
      { label: 'Jan', val: 60 }, { label: 'Feb', val: 75 },
      { label: 'Mar', val: 55 }, { label: 'Apr', val: 85 },
      { label: 'May', val: 70 }, { label: 'Jun', val: 95 },
    ];
    const maxVal = Math.max(...data.map(d => d.val));
    barChart.innerHTML = data.map(d => `
      <div class="bar-group">
        <div class="bar" style="height:${(d.val / maxVal) * 160}px" title="${d.val}%"></div>
        <span class="bar-label">${d.label}</span>
      </div>`).join('');
  }

  // ---- Donut Chart (SVG) ----
  const donutWrap = document.getElementById('donut-chart-wrap');
  if (donutWrap) {
    const segments = [
      { label: 'Rice Dishes', val: 38, color: '#FF6600' },
      { label: 'Grills & BBQ', val: 25, color: '#FF8533' },
      { label: 'Fast Food', val: 20, color: '#FFB380' },
      { label: 'Swallow', val: 17, color: '#2a2a2a' },
    ];
    const r = 60, cx = 80, cy = 80;
    const circumference = 2 * Math.PI * r;
    let offset = 0;
    let paths = '';
    segments.forEach(seg => {
      const dash = (seg.val / 100) * circumference;
      paths += `<circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="${seg.color}" stroke-width="18"
        stroke-dasharray="${dash} ${circumference - dash}" stroke-dashoffset="${-offset}" />`;
      offset += dash;
    });
    donutWrap.querySelector('.donut-svg').innerHTML = `
      <svg class="donut-svg" viewBox="0 0 160 160" width="160" height="160" style="transform:rotate(-90deg)">
        ${paths}
      </svg>`;
    donutWrap.querySelector('.donut-legend').innerHTML = segments.map(s => `
      <div class="legend-item">
        <span class="legend-dot" style="background:${s.color}"></span>
        <span class="legend-label">${s.label}</span>
        <span class="legend-val">${s.val}%</span>
      </div>`).join('');
  }

  // ---- Toggle switches ----
  document.querySelectorAll('.toggle').forEach(toggle => {
    toggle.addEventListener('click', () => {
      toggle.classList.toggle('on');
    });
  });

  // ---- Admin Search ----
  const adminSearch = document.querySelector('.topbar-search input');
  if (adminSearch) {
    adminSearch.addEventListener('input', function () {
      const query = this.value.toLowerCase();
      document.querySelectorAll('.data-table tbody tr').forEach(row => {
        row.style.display = row.textContent.toLowerCase().includes(query) ? '' : 'none';
      });
    });
  }

  // ---- Order Status Update ----
  document.querySelectorAll('.status-select').forEach(sel => {
    sel.addEventListener('change', function () {
      const val = this.value;
      const badge = this.closest('tr')?.querySelector('.badge');
      if (badge) {
        badge.className = 'badge';
        if (val === 'delivered') badge.classList.add('badge-success');
        else if (val === 'pending') badge.classList.add('badge-warning');
        else if (val === 'cancelled') badge.classList.add('badge-danger');
        else badge.classList.add('badge-info');
        badge.textContent = val.charAt(0).toUpperCase() + val.slice(1);
      }
      if (window.showToast) showToast('Order status updated', 'success', 'bi-check-circle-fill');
    });
  });

  // ---- Delete row buttons ----
  document.querySelectorAll('.delete-row-btn').forEach(btn => {
    btn.addEventListener('click', function () {
      if (confirm('Are you sure you want to delete this item?')) {
        this.closest('tr')?.remove();
        if (window.showToast) showToast('Deleted successfully', 'danger', 'bi-trash3-fill');
      }
    });
  });

  // ---- Menu management image click ----
  document.querySelectorAll('.menu-mgmt-img').forEach(img => {
    img.style.cursor = 'pointer';
  });

  // ---- Add menu item form ----
  const addMenuForm = document.getElementById('add-menu-form');
  if (addMenuForm) {
    addMenuForm.addEventListener('submit', e => {
      e.preventDefault();
      if (window.showToast) showToast('Menu item added successfully!', 'success', 'bi-plus-circle-fill');
      var m = bootstrap.Modal.getInstance(document.getElementById('add-item-modal'));
      if (m) m.hide();
      addMenuForm.reset();
    });
  }

  // ---- Settings form ----
  const settingsForm = document.querySelector('.settings-form');
  if (settingsForm) {
    settingsForm.addEventListener('submit', e => {
      e.preventDefault();
      if (window.showToast) showToast('Settings saved!', 'success', 'bi-gear-fill');
    });
  }

  // ---- Live clock ----
  const clockEl = document.getElementById('admin-clock');
  if (clockEl) {
    const updateClock = () => {
      const now = new Date();
      clockEl.textContent = now.toLocaleTimeString('en-NG', { hour: '2-digit', minute: '2-digit' });
    };
    updateClock();
    setInterval(updateClock, 1000);
  }

  // ---- Sidebar active state ----
  const currentPage = location.pathname.split('/').pop();
  document.querySelectorAll('.admin-sidebar a').forEach(link => {
    if (link.getAttribute('href') === currentPage) {
      link.classList.add('active');
    }
  });

  // ---- Notification bell ----
  const bellBtn = document.querySelector('.topbar-icon-btn.bell');
  if (bellBtn) {
    bellBtn.addEventListener('click', () => {
      if (window.showToast) showToast('3 new orders received!', 'success', 'bi-bell-fill');
    });
  }

  // ---- Export button ----
  const exportBtn = document.getElementById('export-btn');
  if (exportBtn) {
    exportBtn.addEventListener('click', () => {
      if (window.showToast) showToast('Exporting data...', 'success', 'bi-download');
    });
  }

  // ---- Animated counters for stats ----
  document.querySelectorAll('.stat-num[data-target]').forEach(el => {
    const target = parseInt(el.dataset.target);
    const prefix = el.dataset.prefix || '';
    const suffix = el.dataset.suffix || '';
    let current = 0;
    const step = target / 50;
    const timer = setInterval(() => {
      current = Math.min(current + step, target);
      el.textContent = prefix + Math.floor(current).toLocaleString() + suffix;
      if (current >= target) clearInterval(timer);
    }, 30);
  });

  // ---- Mobile sidebar toggle ----
  const mobileToggle = document.getElementById('mobile-sidebar-toggle');
  const adminSidebar = document.querySelector('.admin-sidebar');
  if (mobileToggle && adminSidebar) {
    mobileToggle.addEventListener('click', () => {
      adminSidebar.classList.toggle('mobile-open');
    });
  }
});