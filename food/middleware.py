from django.contrib.auth import logout
from django.contrib import messages

# Middleware to prevent browser caching of authenticated pages.
# When user clicks browser back/forward, the page MUST be re-fetched
# from the server so that @login_required can properly redirect if
# the session has expired or the user has logged out.
class NoCacheMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated:
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        return response


# Middleware that checks on EVERY request whether the authenticated user
# has been blocked/banned by an admin. If blocked, the user is
# immediately logged out and shown the blocked message.
class BlockedUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Lazy import to avoid circular import at startup
            from food.models import SignUp
            try:
                signup_row = SignUp.objects.get(user=request.user)
                if signup_row.status == 'blocked':
                    logout(request)
                    from django.shortcuts import redirect
                    return redirect('/login')
            except SignUp.DoesNotExist:
                pass
        response = self.get_response(request)
        return response


# Admin URLs — exact paths and prefixed (id-bearing) paths.
# NOTE: kept separate so e.g. /delete/<id> never matches /delete_account,
# and /settings (admin) never matches /setting (user page).
ADMIN_EXACT_PATHS = {
    '/dashboard', '/add_admin', '/admin_profile', '/menu_management',
    '/add_menu_item', '/export_menu_csv', '/order_management',
    '/update_order_status', '/delete_order', '/customers',
    '/export_customers_csv', '/settings', '/notifications',
}
ADMIN_PREFIX_PATHS = (
    '/edit_menu_item/', '/delete_menu_item/', '/toggle_menu_item/',
    '/block/', '/unblock/', '/delete/', '/view_single_user/',
    '/mark_notification_read/',
)


# Middleware gate: ONLY superusers/staff may access admin pages.
# Regular users are redirected home; anonymous visitors to login.
class AdminGateMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path.rstrip('/')
        is_admin_path = path in ADMIN_EXACT_PATHS or any(
            request.path.startswith(p) for p in ADMIN_PREFIX_PATHS
        )
        if is_admin_path:
            from django.shortcuts import redirect
            if not request.user.is_authenticated:
                return redirect('/login')
            if not (request.user.is_superuser or request.user.is_staff):
                messages.error(request, "Admin access only.")
                return redirect('/')
        return self.get_response(request)
