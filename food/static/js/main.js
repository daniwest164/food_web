/* =============================================
   CHOPORA - MAIN JAVASCRIPT
============================================= */

document.addEventListener('DOMContentLoaded', function () {

  // ---- Navbar Scroll ----
  const navbar = document.querySelector('.navbar');
  if (navbar) {
    window.addEventListener('scroll', () => {
      navbar.classList.toggle('scrolled', window.scrollY > 50);
    });
  }

  // ---- Back to Top ----
  const btt = document.getElementById('back-to-top');
  if (btt) {
    window.addEventListener('scroll', () => {
      btt.classList.toggle('visible', window.scrollY > 400);
    });
    btt.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
  }

  // ---- Animate on Scroll ----
  const animEls = document.querySelectorAll('.animate-on-scroll');
  if (animEls.length) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry, i) => {
        if (entry.isIntersecting) {
          setTimeout(() => entry.target.classList.add('visible'), i * 80);
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1 });
    animEls.forEach(el => observer.observe(el));
  }

  // ---- Menu Filter Buttons ----
  const filterBtns = document.querySelectorAll('.filter-btn');
  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const category = btn.dataset.cat;
      filterMenuCards(category);
    });
  });

  function filterMenuCards(cat) {
    document.querySelectorAll('.menu-card').forEach(card => {
      const cardCat = card.dataset.category;
      if (cat === 'all' || cardCat === cat) {
        card.style.display = '';
        card.style.animation = 'fadeInUp 0.4s ease';
      } else {
        card.style.display = 'none';
      }
    });
  }

  // ---- Favourite Toggle ----
  document.querySelectorAll('.fav-btn').forEach(btn => {
    btn.addEventListener('click', e => {
      e.stopPropagation();
      btn.classList.toggle('active');
      const icon = btn.querySelector('i');
      if (btn.classList.contains('active')) {
        icon.className = 'bi bi-heart-fill';
        showToast('Added to favourites', 'success', 'bi-heart-fill');
      } else {
        icon.className = 'bi bi-heart';
        showToast('Removed from favourites', 'danger', 'bi-heart');
      }
    });
  });

  // ---- Add to Cart Buttons ── handled by quickView() in menu.html via backend fetch
  // ---- Cart badge ── updated server-side via context_processor + cart.js

  // ---- Toast Notifications ----
  window.showToast = function (message, type = 'success', icon = 'bi-check-circle-fill') {
    let container = document.querySelector('.toast-container');
    if (!container) {
      container = document.createElement('div');
      container.className = 'toast-container';
      document.body.appendChild(container);
    }
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<i class="bi ${icon}"></i><span class="toast-msg">${message}</span>`;
    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(30px)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 2500);
  };

  // ---- Category Card Click ----
  document.querySelectorAll('.category-card').forEach(card => {
    card.addEventListener('click', () => {
      const cat = card.dataset.cat;
      if (cat) window.location.href = `/menu?category=${cat}`;
    });
  });

  // ---- Toggle Sidebar (mobile) ----
  const adminMenuToggle = document.getElementById('admin-menu-toggle');
  if (adminMenuToggle) {
    adminMenuToggle.addEventListener('click', () => {
      document.querySelector('.admin-sidebar')?.classList.toggle('open');
    });
  }

  // ---- Newsletter Form ----
  const newsletterForm = document.querySelector('.newsletter-form');
  if (newsletterForm) {
    newsletterForm.addEventListener('submit', e => {
      e.preventDefault();
      showToast('Subscribed successfully!', 'success', 'bi-envelope-check-fill');
      newsletterForm.reset();
    });
  }

  // ---- Contact Form ----
  const contactForm = document.querySelector('.contact-form');
  if (contactForm) {
    contactForm.addEventListener('submit', e => {
      e.preventDefault();
      showToast('Message sent! We will get back to you soon.', 'success', 'bi-send-fill');
      contactForm.reset();
    });
  }

  // ---- Smooth scroll for anchor links ----
  document.querySelectorAll('a[href^="#"]').forEach(link => {
    link.addEventListener('click', e => {
      const target = document.querySelector(link.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  // ---- Counter Animation ----
  function animateCounter(el) {
    const target = parseInt(el.dataset.target || el.textContent.replace(/\D/g, ''));
    const suffix = el.dataset.suffix || '';
    const prefix = el.dataset.prefix || '';
    const duration = 1500;
    const steps = 60;
    const increment = target / steps;
    let current = 0;
    const timer = setInterval(() => {
      current += increment;
      if (current >= target) {
        current = target;
        clearInterval(timer);
      }
      el.textContent = prefix + Math.floor(current).toLocaleString() + suffix;
    }, duration / steps);
  }

  const counterEls = document.querySelectorAll('[data-counter]');
  if (counterEls.length) {
    const counterObs = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          animateCounter(entry.target);
          counterObs.unobserve(entry.target);
        }
      });
    }, { threshold: 0.5 });
    counterEls.forEach(el => counterObs.observe(el));
  }
});
