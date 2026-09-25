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
    return {'user_notifications': Notification.objects.filter(is_active=True)}
