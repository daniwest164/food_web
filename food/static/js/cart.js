/* =============================================
   CHOPORA - CART JAVASCRIPT (Choply-style)
   Django renders the cart HTML. This file adds
   interactive +/–/delete via fetch() and updates
   quantities, prices, and summary in-place.
   ============================================= */

var appliedPromo = null; // {code: 'CHOPORA10', rate: 0.1} when active

document.addEventListener('DOMContentLoaded', function () {
  // Event delegation for all cart operations
  var container = document.getElementById('cart-items-container');
  if (container) {
    container.addEventListener('click', function (e) {
      var btn = e.target.closest('[data-action]');
      if (!btn) return;
      e.preventDefault();
      var id = btn.dataset.id;
      var action = btn.dataset.action;
      if (action === 'increase')       updateQuantity(id,  1, btn);
      else if (action === 'decrease')  updateQuantity(id, -1, btn);
      else if (action === 'delete')    confirmDelete(id, btn);
    });
  }

  // Delete modal confirm button
  var delConfirmBtn = document.getElementById('delete-confirm-btn');
  if (delConfirmBtn) delConfirmBtn.addEventListener('click', executeDelete);

  // Clear cart modal confirm button
  var clearConfirmBtn = document.getElementById('clear-cart-confirm-btn');
  if (clearConfirmBtn) clearConfirmBtn.addEventListener('click', executeClearCart);

  // Promo code
  var promoBtn = document.getElementById('apply-promo');
  if (promoBtn) promoBtn.addEventListener('click', applyPromo);

  // Payment method selector — Jumia-style single selection (Card / Cash)
  window.selectedPaymentMethod = 'card';
  var paymentLabels = document.querySelectorAll('.payment-method');
  paymentLabels.forEach(function(label){
    label.addEventListener('click', function(){
      paymentLabels.forEach(function(l){ l.classList.remove('selected'); var chk=l.querySelector('.bi-check-circle-fill'); if(chk) chk.style.display='none'; });
      label.classList.add('selected');
      var chkIcon = label.querySelector('.bi-check-circle-fill');
      if(chkIcon) chkIcon.style.display='';
      var radio = label.querySelector('input[type="radio"]');
      if(radio){ radio.checked = true; window.selectedPaymentMethod = radio.value; }
    });
  });
  // initialise check icon visibility
  paymentLabels.forEach(function(l){
    var radio=l.querySelector('input[type="radio"]');
    var chk=l.querySelector('.bi-check-circle-fill');
    if(chk) chk.style.display = (radio && radio.checked) ? '' : 'none';
  });

  // Checkout
  var checkoutBtn = document.getElementById('checkout-btn');
  if (checkoutBtn) checkoutBtn.addEventListener('click', handleCheckout);
});

// ========================  HELPERS  ========================

function getCSRFToken() {
  var el = document.querySelector('[name=csrfmiddlewaretoken]');
  return el ? el.value : '';
}

function fmtNum(n) {
  return Number(n).toLocaleString('en-US', {
    minimumFractionDigits: 0, maximumFractionDigits: 0,
  });
}

function updateCartBadge(count) {
  document.querySelectorAll('.cart-count').forEach(function (el) {
    el.textContent = count;
    el.style.display = count > 0 ? 'flex' : 'none';
  });
  localStorage.setItem('choporta_cart_count', count);
}

function setText(id, val) {
  var el = document.getElementById(id);
  if (el) el.textContent = val;
}

// ========================  TOAST  ========================

function showToast(message, type) {
  var container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.style.cssText = 'position:fixed;bottom:20px;right:20px;z-index:10000;display:flex;flex-direction:column;gap:8px;';
    document.body.appendChild(container);
  }

  var toast = document.createElement('div');
  var bgColor = type === 'success' ? 'var(--success)' : type === 'danger' ? 'var(--danger)' : 'var(--info)';
  toast.style.cssText = 'padding:12px 20px;border-radius:10px;color:#fff;font-size:14px;font-weight:600;box-shadow:0 4px 16px rgba(0,0,0,0.3);animation:slideInRight 0.3s ease;min-width:200px;text-align:center;background:' + bgColor + ';';
  toast.textContent = message;
  container.appendChild(toast);

  setTimeout(function () {
    toast.style.opacity = '0';
    toast.style.transition = 'opacity 0.3s ease';
    setTimeout(function () { toast.remove(); }, 300);
  }, 3000);
}

// ========================  QUANTITY (increase / decrease)  ========================

function updateQuantity(itemId, delta, btn) {
  var row = btn.closest('.item-row');
  if (!row) return;
  var qtyEl = row.querySelector('.qty-num');
  var currentQty = qtyEl ? parseInt(qtyEl.textContent) : 1;
  var newQty = currentQty + delta;

  // Going to 0 → show delete modal
  if (newQty <= 0) {
    confirmDelete(itemId, btn);
    return;
  }

  btn.disabled = true;

  fetch('/update_cart/' + itemId, {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCSRFToken(),
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: 'quantity=' + newQty
  })
  .then(function (r) { return r.json(); })
  .then(function (data) {
    if (data.status === 'success') {
      syncCartUI(data);
    }
  })
  .catch(function () {
    showToast('Error updating quantity', 'danger');
  })
  .then(function () {
    btn.disabled = false;
  });
}

// ========================  DELETE (with Bootstrap modal)  ========================

function confirmDelete(itemId, btn) {
  var row = btn.closest('.item-row');
  var nameEl = row ? row.querySelector('.checkout-item-name') : null;
  var name = nameEl ? nameEl.textContent : 'this item';

  document.getElementById('delete-message').textContent =
    'Are you sure you want to remove "' + name + '" from your cart?';

  var confirmBtn = document.getElementById('delete-confirm-btn');
  if (confirmBtn) confirmBtn.dataset.id = itemId;

  var modalEl = document.getElementById('deleteCartModal');
  if (modalEl) {
    var modal = new bootstrap.Modal(modalEl);
    modal.show();
  }
}

function executeDelete() {
  var confirmBtn = document.getElementById('delete-confirm-btn');
  var itemId = confirmBtn ? confirmBtn.dataset.id : null;
  if (!itemId) return;

  var modalEl = document.getElementById('deleteCartModal');
  var modal = bootstrap.Modal.getInstance(modalEl);
  if (modal) modal.hide();

  var row = document.querySelector('.item-row[data-id="' + itemId + '"]');

  fetch('/remove_from_cart/' + itemId, {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCSRFToken(),
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: 'item_id=' + itemId
  })
  .then(function (r) { return r.json(); })
  .then(function (data) {
    if (data.status === 'success') {
      if (data.items && data.items.length > 0) {
        if (row) row.remove();
        syncCartUI(data);
        showToast('Item removed', 'success');
      } else {
        window.location.reload();
      }
    }
  })
  .catch(function () {
    showToast('Error removing item', 'danger');
  });
}

// ========================  CLEAR FULL CART  ========================

function executeClearCart() {
  var modalEl = document.getElementById('clearCartModal');
  var modal = bootstrap.Modal.getInstance(modalEl);
  if (modal) modal.hide();

  var btn = document.getElementById('clear-cart-btn');
  if (btn) { btn.disabled = true; btn.innerHTML = '<i class="bi bi-hourglass-split"></i> Clearing...'; }

  fetch('/clear-cart/', {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCSRFToken(),
      'Content-Type': 'application/x-www-form-urlencoded',
    }
  })
  .then(function (r) { return r.json(); })
  .then(function (data) {
    if (data.status === 'success') {
      window.location.reload();
    } else {
      showToast('Error clearing cart', 'danger');
      if (btn) { btn.disabled = false; btn.innerHTML = '<i class="bi bi-trash me-1"></i> Clear Cart'; }
    }
  })
  .catch(function () {
    showToast('Error clearing cart', 'danger');
    if (btn) { btn.disabled = false; btn.innerHTML = '<i class="bi bi-trash me-1"></i> Clear Cart'; }
  });
}

// ========================  SYNC UI  ========================

function syncCartUI(data) {
  data.items.forEach(function (item) {
    var row = document.querySelector('.item-row[data-id="' + item.id + '"]');
    if (!row) return;

    var qtyEl = row.querySelector('.qty-num');
    if (qtyEl) qtyEl.textContent = item.quantity;

    var priceEl = row.querySelector('.checkout-item-price.fw-bold');
    if (priceEl) priceEl.textContent = '₦' + fmtNum(item.total_price);

    var decBtn = row.querySelector('[data-action="decrease"]');
    if (decBtn) {
      decBtn.disabled = (item.quantity <= 1);
    }
  });

  updateSummary(data);
  updateCartBadge(data.cart_count);
}

function updateSummary(data) {
  var promoDiscount = 0;
  if (appliedPromo) {
    promoDiscount = data.subtotal * appliedPromo.rate;
  }
  var finalTotal = data.subtotal + data.delivery - promoDiscount;

  setText('summary-subtotal', '₦' + fmtNum(data.subtotal));
  setText('summary-delivery', data.delivery > 0 ? '₦' + fmtNum(data.delivery) : 'Free');
  setText('summary-discount', '-₦' + fmtNum(data.discount));
  setText('summary-total',   '₦' + fmtNum(finalTotal));
  setText('btn-total-label', '₦' + fmtNum(finalTotal));

  var promoLine = document.getElementById('promo-line');
  if (promoLine) {
    if (appliedPromo) {
      promoLine.style.display = 'flex';
      setText('promo-code-display', appliedPromo.code);
      setText('promo-amount', '-₦' + fmtNum(promoDiscount));
    } else {
      promoLine.style.display = 'none';
    }
  }
}

// ========================  PROMO CODE  ========================

function applyPromo() {
  var input = document.getElementById('promo-input');
  var feedback = document.getElementById('promo-feedback');
  if (!input) return;
  var code = input.value.trim().toUpperCase();

  if (code === 'CHOPORA10') {
    appliedPromo = { code: code, rate: 0.1 };
    input.value = '';
    if (feedback) {
      feedback.textContent = 'Promo code applied – 10% off!';
      feedback.style.display = 'block';
      feedback.style.color = 'var(--success)';
      feedback.className = 'promo-feedback success';
    }
    showToast('Promo code applied – 10% off!', 'success');
    fetchCartAndSync();
  } else if (code) {
    if (feedback) {
      feedback.textContent = 'Invalid promo code';
      feedback.style.display = 'block';
      feedback.style.color = 'var(--danger)';
      feedback.className = 'promo-feedback error';
    }
    showToast('Invalid promo code', 'danger');
  }
}

function fetchCartAndSync() {
  fetch('/cart-data/', {
    headers: { 'X-Requested-With': 'XMLHttpRequest' }
  })
  .then(function (r) { return r.json(); })
  .then(function (data) {
    if (data.status === 'success') updateSummary(data);
  });
}

// ========================  SUCCESS OVERLAY  ========================

function showSuccessOverlay(orderId) {
  // Jumia-style: clear cart badge + localStorage immediately so cart icon shows 0 everywhere
  updateCartBadge(0);
  localStorage.removeItem('choporta_cart_count');

  var overlay = document.getElementById('checkout-success-overlay');
  if (!overlay) {
    window.location.href = '/orders';
    return;
  }

  var orderIdEl = document.getElementById('success-order-id');
  if (orderIdEl) orderIdEl.textContent = orderId || 'PD-0000';

  overlay.classList.add('show');
  spawnConfetti(overlay);

  // Auto-redirect to orders page where the new order is visible
  setTimeout(function () {
    window.location.href = '/orders';
  }, 4000);
}

function spawnConfetti(container) {
  var colors = ['#FF6600', '#22c55e', '#3b82f6', '#eab308', '#ef4444', '#a855f7'];
  for (var i = 0; i < 30; i++) {
    var particle = document.createElement('div');
    particle.className = 'confetti-particle';
    particle.style.left = Math.random() * 100 + '%';
    particle.style.background = colors[Math.floor(Math.random() * colors.length)];
    particle.style.animationDelay = Math.random() * 2 + 's';
    particle.style.animationDuration = (2 + Math.random() * 2) + 's';
    particle.style.width = (4 + Math.random() * 8) + 'px';
    particle.style.height = particle.style.width;
    container.appendChild(particle);
  }
  // Clean up confetti after animation
  setTimeout(function () {
    container.querySelectorAll('.confetti-particle').forEach(function(p) { p.remove(); });
  }, 5000);
}

// ========================  CHECKOUT  ========================

function handleCheckout() {
  var btn = document.getElementById('checkout-btn');
  if (!btn) return;

  var method = window.selectedPaymentMethod || 'card';

  // Cash on Delivery — Jumia-style: create order directly, no Paystack
  if (method === 'cash') {
    btn.innerHTML = '<i class="bi bi-hourglass-split"></i> Placing Order...';
    btn.disabled = true;

    fetch('/cart-data/', {
      headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(function (r) { return r.json(); })
    .then(function (data) {
      if (data.status !== 'success' || data.items.length === 0) {
        showToast('Cart is empty', 'danger');
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-bag-check-fill"></i> Place Order — <span id="btn-total-label">₦0</span>';
        return;
      }
      return fetch('/place_order/', {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCSRFToken(),
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'payment_method=cash'
      });
    })
    .then(function (r) { return r ? r.json() : null; })
    .then(function (data) {
      if (data && data.status === 'success') {
        showSuccessOverlay(data.order_id);
      } else if (data) {
        showToast(data.error || 'Error placing order', 'danger');
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-bag-check-fill"></i> Place Order — <span id="btn-total-label">₦0</span>';
      }
    })
    .catch(function () {
      showToast('Network error placing order', 'danger');
      btn.disabled = false;
      btn.innerHTML = '<i class="bi bi-bag-check-fill"></i> Place Order — <span id="btn-total-label">₦0</span>';
    });
    return;
  }

  // Pay with Card — Paystack (simple, same Jumia flow)
  btn.innerHTML = '<i class="bi bi-hourglass-split"></i> Processing...';
  btn.disabled = true;

  fetch('/cart-data/', {
    headers: { 'X-Requested-With': 'XMLHttpRequest' }
  })
  .then(function (r) { return r.json(); })
  .then(function (data) {
    if (data.status !== 'success' || data.items.length === 0) {
      showToast('Cart is empty', 'danger');
      btn.disabled = false;
      btn.innerHTML = '<i class="bi bi-bag-check-fill"></i> Place Order — <span id="btn-total-label">₦0</span>';
      return;
    }

    if (typeof PaystackPop === 'undefined') {
      showToast('Payment system failed to load. Check your connection to js.paystack.co and refresh.', 'danger');
      btn.disabled = false;
      btn.innerHTML = '<i class="bi bi-bag-check-fill"></i> Place Order — <span id="btn-total-label">₦0</span>';
      return;
    }

    var email = document.getElementById('user-email').value;
    var publicKey = document.getElementById('paystack-public-key').value;
    var amountKobo = Math.round(data.total * 100);

    var handler = PaystackPop.setup({
      key: publicKey,
      email: email,
      amount: amountKobo,
      currency: 'NGN',
      ref: 'PD-' + Math.random().toString(36).substr(2, 12).toUpperCase(),
      callback: function (response) {
        verifyPaystackPayment(response.reference, btn);
      },
      onClose: function () {
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-bag-check-fill"></i> Place Order — <span id="btn-total-label">₦0</span>';
      }
    });
    handler.openIframe();
  })
  .catch(function () {
    showToast('Error fetching cart data', 'danger');
    btn.disabled = false;
    btn.innerHTML = '<i class="bi bi-bag-check-fill"></i> Place Order — <span id="btn-total-label">₦0</span>';
  });
}

function verifyPaystackPayment(reference, btn) {
  btn.innerHTML = '<i class="bi bi-hourglass-split"></i> Verifying...';
  btn.disabled = true;

  fetch('/verify-paystack-payment/', {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCSRFToken(),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ reference: reference })
  })
  .then(function (r) {
    if (!r.ok) {
      return r.json().catch(function() { return {error: 'Payment verification failed'}; }).then(function(d) { throw new Error(d.error || 'Verification failed'); });
    }
    return r.json();
  })
  .then(function (data) {
    if (data.status === 'success') {
      showSuccessOverlay(data.order_id);
    } else {
      showToast(data.error || 'Error verifying payment', 'danger');
      btn.disabled = false;
      btn.innerHTML = '<i class="bi bi-bag-check-fill"></i> Place Order — <span id="btn-total-label">₦0</span>';
    }
  })
  .catch(function (err) {
    showToast(err.message || 'Network error verifying payment', 'danger');
    btn.disabled = false;
    btn.innerHTML = '<i class="bi bi-bag-check-fill"></i> Place Order — <span id="btn-total-label">₦0</span>';
  });
}
