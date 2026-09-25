/* =============================================
   PRIME DISH - USER PAGES JAVASCRIPT
============================================= */

document.addEventListener('DOMContentLoaded', function () {

  // ---- Password toggle ----
  document.querySelectorAll('.password-toggle').forEach(btn => {
    btn.addEventListener('click', function () {
      const input = this.previousElementSibling;
      if (!input) return;
      if (input.type === 'password') {
        input.type = 'text';
        this.querySelector('i').className = 'bi bi-eye-slash';
      } else {
        input.type = 'password';
        this.querySelector('i').className = 'bi bi-eye';
      }
    });
  });

  // ---- Profile form ----
  // const profileForm = document.getElementById('profile-form');
  // if (profileForm) {
  //   profileForm.addEventListener('submit', function (e) {
  //     e.preventDefault();
  //     const btn = this.querySelector('button[type="submit"]');
  //     btn.innerHTML = '<span class="spinner"></span> Saving...';
  //     btn.disabled = true;
  //     setTimeout(() => {
  //       btn.innerHTML = '<i class="bi bi-check-lg"></i> Saved!';
  //       btn.disabled = false;
  //       showToast('Profile updated successfully!', 'success', 'bi-person-check-fill');
  //       setTimeout(() => { btn.innerHTML = '<i class="bi bi-floppy"></i> Save Changes'; }, 2000);
  //     }, 1200);
  //   });
  // }

  // ---- Order tracking steps ----
  const trackSteps = document.querySelectorAll('.track-step');
  if (trackSteps.length) {
    let current = 2; // demo: step 2 is active (0-indexed)
    trackSteps.forEach((step, i) => {
      if (i < current) step.classList.add('done');
      else if (i === current) step.classList.add('active');
    });
    document.querySelectorAll('.order-track-line').forEach((line, i) => {
      if (i < current) line.classList.add('done');
    });
  }

  // ---- ETa countdown ----
  const etaEl = document.getElementById('eta-countdown');
  if (etaEl) {
    let minutes = 18, seconds = 30;
    const timer = setInterval(() => {
      if (seconds === 0) {
        if (minutes === 0) { clearInterval(timer); etaEl.textContent = 'Arrived!'; return; }
        minutes--;
        seconds = 59;
      } else seconds--;
      etaEl.textContent = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    }, 1000);
  }

  // ---- Reorder button ----
  document.querySelectorAll('.reorder-btn').forEach(btn => {
    btn.addEventListener('click', function () {
      this.innerHTML = '<span class="spinner"></span>';
      setTimeout(() => {
        this.innerHTML = '<i class="bi bi-check-lg"></i> Added!';
        showToast('Items added to cart!', 'success', 'bi-bag-check-fill');
        setTimeout(() => { this.innerHTML = '<i class="bi bi-arrow-repeat"></i> Reorder'; }, 2000);
      }, 1000);
    });
  });



  // ---- Tab switching ----
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', function () {
      const group = this.dataset.group;
      const target = this.dataset.tab;
      document.querySelectorAll(`[data-group="${group}"].tab-btn`).forEach(b => b.classList.remove('active'));
      document.querySelectorAll(`[data-group="${group}"].tab-panel`).forEach(p => p.classList.add('hidden'));
      this.classList.add('active');
      document.querySelector(`[data-group="${group}"][data-panel="${target}"]`)?.classList.remove('hidden');
    });
  });

  // ---- Notification dropdown: mark all as read ----
  const markAllRead = document.querySelector('.mark-all-read');
  if (markAllRead) {
    markAllRead.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      const dropdown = this.closest('.notif-dropdown');
      const list = dropdown ? dropdown.querySelector('.notif-list') : null;
      const bellBadge = document.querySelector('.bell-badge, .topbar-icon-btn.bell .unread-dot-badge');
      const notifCount = document.querySelector('.notif-count');
      if (list) {
        list.querySelectorAll('.notif-item.unread').forEach(item => item.classList.remove('unread'));
        list.querySelectorAll('.notif-item .notif-dot, .notif-item .unread-dot').forEach(dot => dot.remove());
      }
      if (bellBadge) bellBadge.remove();
      if (notifCount) notifCount.remove();
    });
  }

  // ---- Notification item click: mark as read ----
  document.querySelectorAll('.notif-item.unread').forEach(item => {
    item.addEventListener('click', function (e) {
      this.classList.remove('unread');
      const dot = this.querySelector('.notif-dot, .unread-dot');
      if (dot) dot.remove();
    });
  });
});
