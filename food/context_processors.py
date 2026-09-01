from food.models import Cart, Notification

def cart_count(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        count = cart.total_items if cart else 0
    else:
        count = 0
    return {'cart_count': count}

def notifications(request):
    return {'user_notifications': Notification.objects.filter(is_active=True)}
