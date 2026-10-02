from food.models import Cart, Notification

def cart_count(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        count = cart.total_items if cart else 0
    else:
        data = request.session.get('cart')
        count = 0
        if isinstance(data, dict):
            for v in data.values():
                try:
                    qty = int(v)
                    if qty > 0:
                        count += qty
                except (ValueError, TypeError):
                    continue
    return {'cart_count': count}

def notifications(request):
    """
    Role-aware notification context (privacy-safe).

    - Anonymous: no notifications.
    - Admin/staff: admin inbox (admin-private + public broadcasts).
      Exposes `admin_notifications` + `admin_unread_count`.
      `user_notifications` is aliased to the same list so existing admin
      templates keep working, but it NEVER contains customer-private rows.
    - Customer: ONLY public broadcasts (all/customers) + their own private
      rows. Admin-private rows are never leaked. Per-user read state is
      computed via NotificationRead (global is_read is ignored for customers).
      Exposes `user_notifications` + `user_unread_count`.
    """
    from food.models import NotificationRead
    user = getattr(request, 'user', None)
    if user is None or not getattr(user, 'is_authenticated', False):
        return {
            'user_notifications': [],
            'user_unread_count': 0,
            'admin_notifications': [],
            'admin_unread_count': 0,
        }

    is_admin = getattr(user, 'is_superuser', False) or getattr(user, 'is_staff', False)
    if is_admin:
        qs = Notification.for_admin().order_by('-created_at')[:20]
        items = list(qs)
        for n in items:
            # unify template flag: admin inbox uses global is_read
            n.is_read_for_user = bool(n.is_read)
        unread = Notification.objects.filter(
            is_active=True, is_read=False,
        ).filter(
            visibility__in=['admin', 'public']
        ).count()
        return {
            'admin_notifications': items,
            'admin_unread_count': unread,
            # alias for existing admin templates that use user_notifications
            'user_notifications': items,
            'user_unread_count': unread,
        }

    qs = Notification.for_user(user).order_by('-created_at')[:20]
    items = list(qs)
    if items:
        read_ids = set(
            NotificationRead.objects.filter(
                user=user, notification_id__in=[n.id for n in items]
            ).values_list('notification_id', flat=True)
        )
    else:
        read_ids = set()
    for n in items:
        # template-friendly per-user flag (does not mutate DB)
        n.is_read_for_user = n.id in read_ids
    unread = len([n for n in items if n.id not in read_ids])
    # Fallback: if inbox > 20, count remaining unread too (cheap extra query)
    if len(items) == 20:
        all_ids = Notification.for_user(user).values_list('id', flat=True)
        read_all = set(
            NotificationRead.objects.filter(user=user).values_list('notification_id', flat=True)
        )
        unread = len([i for i in all_ids if i not in read_all])
    return {
        'user_notifications': items,
        'user_unread_count': unread,
        'admin_notifications': [],
        'admin_unread_count': 0,
    }
