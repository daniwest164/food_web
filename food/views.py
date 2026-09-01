import json
import urllib.request  # used to call Paystack's verification API (no extra dependencies needed)
import urllib.error
import traceback
import logging
from functools import wraps
from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime
from datetime import timedelta
from django.utils import timezone
import pytz
import random
total_time_package = datetime.now(pytz.timezone('Africa/Lagos'))

import re
from urllib.parse import quote
from django.db.models import Q, Avg, F, Count, Sum
from food.models import *
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from dateutil.parser import parse
from django.utils.dateparse import parse_date, parse_datetime
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView 
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required as base_login_required


# Create your views here.
# ==============================================    HOME PAGE   ============================================== 
# @login_required(login_url='login')
def home(request):
    return render(request, 'home.html')

@csrf_exempt
def rate_item(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(MenuItem, id=item_id)
        new_rating = float(item.rating) + 0.1
        if new_rating > 5.0:
            new_rating = 0.0
        item.rating = new_rating
        item.save()
        return JsonResponse({'rating': float(item.rating), 'orders_count': item.orders_count})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def submit_rating(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(MenuItem, id=item_id)
        score = int(request.POST.get('score', 0))
        if score < 1 or score > 5:
            return JsonResponse({'error': 'Score must be 1-5'}, status=400)
        if request.user.is_authenticated:
            rating, created = Rating.objects.update_or_create(
                user=request.user,
                menu_item=item,
                defaults={'score': score}
            )
            if score <= 2:
                Notification.objects.create(title=f"Low Rating Alert: {item.name}", body=f"{item.name} received a {score}-star review from {request.user.username}. Their avg dropped to {item.rating} ⭐.", notification_type='system')
        else:
            return JsonResponse({'error': 'Login required'}, status=401)
        avg = item.ratings.aggregate(Avg('score'))['score__avg'] or 0
        return JsonResponse({'rating': round(avg, 1), 'orders_count': item.orders_count, 'user_score': score})
    return JsonResponse({'error': 'Invalid request'}, status=400)

# @login_required(login_url='login')
def menu(request):
    category = request.GET.get('category', '')
    sort = request.GET.get('sort', '')
    # Show only available menu items to users
    items = MenuItem.objects.filter(is_available=True)

    if category:
        items = items.filter(category=category)

    sort_map = {
        'price-asc': 'price',
        'price-desc': '-price',
        'newest': '-date_added',
        'popular': '-orders_count',
        'name': 'name',
    }
    if sort in sort_map:
        items = items.order_by(sort_map[sort])
    else:
        items = items.order_by('-date_added')

    items_json = []
    for item in items:
        items_json.append({
            'id': item.id,
            'name': item.name,
            'description': item.description or '',
            'price': float(item.price),
            'discount': item.discount or 0,
            'prep_time': item.prep_time or '',
            'category': item.category,
            'is_featured': item.is_featured,
            'is_available': item.is_available,
            'orders_count': item.orders_count,
            'rating': float(item.rating),
            'image': item.image.url if item.image else '',
        })

    context = {
        'menu_items': items,
        'menu_items_json': json.dumps(items_json),
        'current_category': category,
        'current_sort': sort,
    }
    return render(request, 'menu.html', context)

# @login_required(login_url='login')
def about(request):
    return render(request, 'about.html')

# @login_required(login_url='login')
def contact(request):
    return render(request, 'contact.html')

# @login_required(login_url='login') 
def logout_page(request):
    # Mark user as inactive in SignUp before logging out
    if request.user.is_authenticated:
        try:
            signup_row = SignUp.objects.get(user=request.user)
            if signup_row.status != 'blocked':
                signup_row.status = ''
                signup_row.save()
        except SignUp.DoesNotExist:
            pass
    logout(request) # terminate user info in the browser (request.user)
    return redirect('/login')

# End General Views Section

# ==============================================  LEGAL PAGES   ============================================== 
def terms_of_service(request):
    return render(request, 'FORM/terms_of_service.html')

def privacy_policy(request):
    return render(request, 'FORM/privacy_policy.html')

# ==============================================  SIGNUP   ============================================== 
# STEP 1 TO SUBMIT TO DATABASE
# part where all input from the form is been collected and store to the database
def sign_up_page(request):
    if request.method == 'POST':
        get_fname = request.POST.get('fname')
        get_lname = request.POST.get('lname')
        get_username = request.POST.get('username')
        get_email = request.POST.get('email')
        get_phone = request.POST.get('phone')
        get_password = request.POST.get('password')
        get_confirm_password = request.POST.get('confirmpassword')

        # Input validations for all inputs 
        if get_fname == "" or get_lname == "" or get_username == "" or get_email == "" or get_phone == "" or get_password == "" or get_confirm_password == "":
            return render(request, 'FORM/sign_up.html', {'error': "All Input fields are required"})

        get_fname =     get_fname.strip()
        get_lname =     get_lname.strip()
        get_username =  get_username.strip().lower()
        get_email =     get_email.strip().lower()
        get_phone =     get_phone.strip()
        get_password =  get_password.strip()

        if not re.match(r'^[a-zA-Z]+$', get_fname):
            return render(request, 'FORM/sign_up.html', {'error': "First name must contain only letters"})

        if not re.match(r'^[a-zA-Z]+$', get_lname):
            return render(request, 'FORM/sign_up.html', {'error': "Last name must contain only letters"})

        if not re.match(r'^[a-zA-Z0-9_.@!]+$', get_username):
            return render(request, 'FORM/sign_up.html', {'error': "Username can only contain letters, numbers, underscores and dots"})

        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', get_email):
            return render(request, 'FORM/sign_up.html', {'error': "Enter a valid email address"})

        # Normalize Nigerian phone numbers to +234XXXXXXXXXX format
        # Accepts: 09020380677, 9020380677, +2349020380677
        digits = re.sub(r'\D', '', get_phone)  # strip all non-digits
        if digits.startswith('234'):           # remove country code prefix if present
            digits = digits[3:]
        if digits.startswith('0'):             # remove leading 0
            digits = digits[1:]
        if len(digits) != 10:
            return render(request, 'FORM/sign_up.html', {'error': "Phone number must be 10 digits (e.g. 08012345678)"})
        get_phone = f'+234{digits}'           # store with +234 country code


        # Check if email belongs to a deleted account
        if SignUp.objects.filter(email=get_email, status='deleted').exists():
            return render(request, 'FORM/sign_up.html', {'error': "This email belongs to a deleted account and cannot be reused."})

        # To check for existing username and email
        if User.objects.filter(username=get_username).exists() or User.objects.filter(email=get_email).exists():
            return render(request, 'FORM/sign_up.html', {'error': "Username already exists"})
     
        if len(get_password) < 8:
            return render(request, 'FORM/sign_up.html', {'error': "Password must be at least 8 characters long"})

        if get_password != get_confirm_password:
            return render(request, 'FORM/sign_up.html', {'error': "Passwords do not match"})

        #  =========================  Submit to database  =========================
        
        auth_user_submit = User.objects.create_user(
            password=get_password,
            is_superuser=0,
            first_name=get_fname,
            last_name=get_lname,
            username=get_username,
            email=get_email
        )

        while True:
            uid = f"#USR-{random.randint(100000, 999999)}"
            if not SignUp.objects.filter(uid=uid).exists():
                break

        fullname = f'{get_fname} {get_lname}'
        otp_code = str(random.randint(100000, 999999))
        verify_token = str(random.randint(100000000000000, 999999999999999))

        signup_submit = SignUp.objects.create(
            name=fullname,
            email=get_email,
            username=get_username,
            phone=get_phone,
            is_superuser=0,
            uid=uid,
            user=auth_user_submit,
            otp=otp_code,
            is_verified=False,
            verify_token=verify_token,
        )

        verify_link = request.build_absolute_uri(f'/verify_email?uid={quote(uid)}&token={verify_token}')

        subject = 'Verify your email – PrimeDish'
        html_message = render_to_string('FORM/send_email.html', {
            'mode': 'verify',
            'user_name': get_username,
            'action_link': verify_link,
            'expires_min': 10,
            'year': datetime.now().year,
        })
        mssg = f"Hi {get_username},\n\nClick the link below to verify your email:\n\n{verify_link}\n\nThis link expires in 10 minutes.\n\n– PrimeDish Team"
        send_mail(subject, mssg, settings.DEFAULT_FROM_EMAIL, [get_email], html_message=html_message)

        Notification.objects.create(title=f"New User Registration: {fullname}", body=f"{fullname} ({get_email}) just created a new customer account. Account pending email verification.", notification_type='system')
        request.session['verification_uid'] = uid
        messages.success(request, f"Welcome {get_username}! A verification link has been sent to {get_email}. Please check your email.")
        return redirect('/verify_email')

    return render(request, 'FORM/sign_up.html')

# ==============================================  EMAIL VERIFICATION  ============================================== 
def verify_email_page(request):
    token = request.GET.get('token')

    if token:
        try:
            signup_user = SignUp.objects.get(verify_token=token)
            signup_user.is_verified = True
            signup_user.verify_token = None
            signup_user.status = 'active'  # ADDED (Jun 10): marks user as active so it shows in admin dashboard
            signup_user.save()

            if 'verification_uid' in request.session:
                del request.session['verification_uid']

            messages.success(request, "Email verified! You can now log in.")
            return redirect('/login')
        except SignUp.DoesNotExist:
            messages.error(request, "Invalid or expired verification link.")
            return redirect('/login')
    else:
        mode = request.GET.get('mode', 'verify')
        uid = request.session.get('verification_uid')
        masked_email = ""
        if uid:
            try:
                signup_user = SignUp.objects.get(uid=uid)
                email = signup_user.email
                if email and '@' in email:
                    local, domain = email.split('@', 1)
                    masked_email = local[0] + '***' + local[-1] + '@' + domain if len(local) > 2 else local[0] + '***@' + domain
            except SignUp.DoesNotExist:
                uid = None
        else:
            messages.error(request, "No verification link found.")
            return redirect('/login')

        # FIXED (Jun 10): added real_email to context so verify_email.html
        # resend form can send the unmasked email to forget_password view
        return render(request, 'FORM/verify_email.html', {
            'uid': uid,
            'masked_email': masked_email,
            'mode': mode,
            'real_email': email if uid else '',
        })

# ==============================================  LOGIN   ============================================== 
def login_page(request):
    current_user = request.user 
    if current_user.is_authenticated:
        return redirect('home')
    else:
        if request.method == "POST":
            email = request.POST.get('email', '').strip()
            password = request.POST.get('password', '').strip()
            
            # Validation for input 
            if not email or not password:
                return render(request, './FORM/login.html', {'error': "All Inputs are Required"})
            
            # Check database if user exists 
            user_obj = User.objects.filter(email=email).first()
            if not user_obj:
                return render(request, './FORM/login.html', {'error': "User does not exist"})

            user = authenticate(username=user_obj.username, password=password)

            if user is None: 
                return render(request, './FORM/login.html', {'error': "Account Not Found, check email / password"})
            
            # Get the user's signup row (one query)
            signup_row = SignUp.objects.filter(user=user).first()
            
            # Auto-create SignUp row for superusers created outside sign-up form
            if signup_row is None:
                signup_row = SignUp.objects.create(
                    user=user,
                    name=f'{user.first_name} {user.last_name}'.strip() or user.username,
                    email=email,
                    username=user.username,
                    is_superuser='1' if user.is_superuser else '0',
                    uid=f"#USR-{random.randint(100000, 999999)}",
                    status='active',
                    is_verified=True,
                )

            # Check if user is blocked or deleted
            if signup_row.status == 'deleted':
                return render(request, './FORM/login.html', {'error': "This account has been deleted and cannot be accessed."})
            if signup_row.status == 'blocked':
                return render(request, './FORM/login.html', {'error': "Your account has been blocked. Please contact support@primedish.ng"})

            # Sync admin flag
            if str(signup_row.is_superuser) == '1' and not user.is_superuser:
                user.is_staff = True
                user.is_superuser = True
                user.save()

            # Check email verification (non-superusers only)
            if not user.is_superuser and not signup_row.is_verified:
                request.session['verification_uid'] = signup_row.uid
                messages.error(request, "Please verify your email before logging in. A link was sent to your email.")
                return redirect('/verify_email')

            # All checks passed — log the user in
            login(request, user)

            # Mark user as active
            if signup_row.status != 'active':
                signup_row.status = 'active'
                signup_row.save()

            # Redirect admin to dashboard, user to menu
            if user.is_superuser:
                return redirect("/dashboard")
            else:
                return redirect("/menu")
        return render(request, './FORM/login.html')

# ==============================================  FORGET PASSWORD   ============================================== 
def forget_password_page(request):
    if request.method == "POST":
        email = request.POST.get('email')

        # FIXED (Jun 10): validations now run in order before processing
        # (previously had dead code that could never execute + rendered sign_up.html on error)

        # VALIDATION 1: Check if email input is provided
        if not email:
            error = "Email input is required"
            return render(request, 'FORM/forget_password.html', {'error': error})

        # VALIDATION 2: Check if email format is valid (basic)
        if '@' not in email or '.' not in email:
            error = "Please enter a valid email address"
            return render(request, 'FORM/forget_password.html', {'error': error})

        # VALIDATION 3: Check if user email exists in the auth User table
        if not User.objects.filter(email=email).exists():
            error = "User email not found"
            return render(request, 'FORM/forget_password.html', {'error': error})

        auth_user = User.objects.get(email=email)

        # Admins/superusers may have no SignUp row — create one (pre-verified)
        # so the reset-token flow, which is keyed on SignUp.reset, works for them.
        user_identity = SignUp.objects.filter(email=email).first()
        if user_identity is None:
            user_identity = SignUp.objects.create(
                user=auth_user,
                name=f'{auth_user.first_name} {auth_user.last_name}'.strip() or auth_user.username,
                email=email,
                username=auth_user.username,
                is_superuser='1' if auth_user.is_superuser else '0',
                uid=f"#USR-{random.randint(100000, 999999)}",
                status='active',
                is_verified=True,
            )

        # Block blocked/banned users from resetting password
        if user_identity.status == 'blocked':
            messages.info(request, "Your account has been blocked. Please contact support@primedish.ng")
            return render(request, 'FORM/forget_password.html')

        # ADDED (Jun 10): resend verification email (from sign-up "Resend link")
        # verify_email.html sends resend_mode='verify' + real email
        # This generates a fresh token & sends a new verification email
        resend_mode = request.POST.get('resend_mode')
        if resend_mode == 'verify':
            uid = user_identity.uid
            user_name = user_identity.username
            user_email = user_identity.email
            verify_token = str(random.randint(100000000000000, 999999999999999))
            user_identity.verify_token = verify_token
            user_identity.save()
            verify_link = request.build_absolute_uri(f'/verify_email?uid={quote(uid)}&token={verify_token}')
            subject = 'Verify your email – PrimeDish'
            html_message = render_to_string('FORM/send_email.html', {
                'mode': 'verify',
                'user_name': user_name,
                'action_link': verify_link,
                'expires_min': 10,
                'year': datetime.now().year,
            })
            mssg = f"Hi {user_name},\n\nClick the link below to verify your email:\n\n{verify_link}\n\nThis link expires in 10 minutes.\n\n– PrimeDish Team"
            send_mail(subject, mssg, settings.DEFAULT_FROM_EMAIL, [user_email], html_message=html_message)
            request.session['verification_uid'] = uid
            messages.success(request, f"A new verification link has been sent to {user_email}.")
            return redirect('/verify_email')

        # Block unverified users from resetting password (superusers exempt)
        if not user_identity.is_verified and not auth_user.is_superuser:
            request.session['verification_uid'] = user_identity.uid
            messages.error(request, "Please verify your email before resetting your password.")
            return redirect('/verify_email')

        reset_token = random.randint(100000000000000, 999999999999999)
        user_name = user_identity.username
        user_identity.reset = reset_token
        user_identity.save()
        reset_link = request.build_absolute_uri(f'/reset_password/{reset_token}')
        subject = 'Reset Your Password – PrimeDish'
        html_message = render_to_string('FORM/send_email.html', {
            'mode': 'reset',
            'user_name': user_name,
            'action_link': reset_link,
            'expires_min': 10,
            'year': datetime.now().year,
        })
        mssg = (
            f"Hi {user_name},\n\n"
            f"Click the link below to reset your password:\n\n"
            f"{reset_link}\n\n"
            f"This link expires in 10 minutes.\n\n"
            f"– PrimeDish Team"
        )
        send_mail(subject, mssg, settings.DEFAULT_FROM_EMAIL, [email], html_message=html_message)

        request.session['verification_uid'] = user_identity.uid
        messages.success(request, f"A reset link has been sent to {email}. Please check your email.")
        return redirect('/verify_email?mode=reset')

    return render(request, 'FORM/forget_password.html')

# ==============================================  RESET PASSWORD   ============================================== 
def reset_password_page(request, id):
    if SignUp.objects.filter(reset=id).exists():
        user_identity = SignUp.objects.get(reset=id)

        # Block blocked/banned users from resetting password
        if user_identity.status == 'blocked':
            messages.info(request, "Your account has been blocked. Please contact support@primedish.ng")
            return redirect('/login')

        # Block unverified users from resetting password (superusers exempt)
        if not user_identity.is_verified and not user_identity.user.is_superuser:
            request.session['verification_uid'] = user_identity.uid
            messages.error(request, "Please verify your email before resetting your password.")
            return redirect('/verify_email')

        get_email = user_identity.email

        if request.method == "POST":
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            # VALIDATION 1: Check if all inputs are provided
            if new_password == "" or confirm_password == "":
                error = "All input fields are required"
                return render(request, './FORM/reset_password.html', {'error': error})

            # VALIDATION 2: Check password length (minimum 6 characters)
            if len(new_password) < 6:
                error = "Password must be at least 6 characters long"
                return render(request, 'FORM/reset_password.html', {'error': error})

            # VALIDATION 3: Check if passwords match
            if new_password != confirm_password:
                error = "Passwords do not match"
                return render(request, './FORM/reset_password.html', {'error': error})

            # If validation passes, you can update the password here
            user_identity_authuser = User.objects.get(email=get_email)
            user_identity_authuser.password = make_password(new_password)
            user_identity_authuser.save()
            user_identity.reset = "" # set "reset" column to empty so it cannot be re-used 
            user_identity.save()
            messages.info(request, "Your password has been successfully changed")
            return redirect ('/login')

        return render(request, './FORM/reset_password.html')
    return redirect('/login')

 # ==============================================  Start User Views Section ============================================== 
# User Profile pages
def profile(request):
    user_orders = Order.objects.filter(user=request.user)
    total_orders = user_orders.count()
    total_spent = user_orders.aggregate(s=Sum('total'))['s'] or 0
    avg_rating_given = Rating.objects.filter(user=request.user).aggregate(a=Avg('score'))['a'] or 0
    reward_points = int(total_spent // 100)

    if(request.method == "POST"):
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        gender = request.POST.get('gender')
        dob1 = request.POST.get('dob')
        dob = parse_date(dob1.strip()) if dob1 else None

        sign_up = SignUp.objects.get(user=request.user)

        if "fileToUpload" in request.FILES:
            sign_up.passport = request.FILES['fileToUpload']

        current_user = request.user
        current_user.first_name = fname
        current_user.last_name = lname
        current_user.username = username
        current_user.email = email

        sign_up.name = f'{fname} {lname}'
        sign_up.username = username
        sign_up.phone = phone
        sign_up.gender = gender
        sign_up.dob = dob

        sign_up.save()
        current_user.save()
        messages.success(request, "Profile updated successfully")
        return redirect('profile')

    return render(request, './user/profile.html', {
        'total_orders': total_orders,
        'total_spent': int(total_spent),
        'avg_rating_given': round(avg_rating_given, 1),
        'reward_points': reward_points,
    })

@login_required(login_url='login')
@csrf_exempt
def clear_cart(request):
    """Clear all items from the user's cart."""
    if request.method == 'POST':
        try:
            cart = Cart.objects.get(user=request.user)
            cart.items.all().delete()
        except Cart.DoesNotExist:
            pass
        return JsonResponse({'status': 'success'})
    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def place_order(request):
    """Convert the user's cart into an Order, clear cart, return JSON — used for Cash on Delivery"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)

    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=401)

    cart = Cart.objects.filter(user=request.user).first()
    if not cart:
        return JsonResponse({'error': 'Cart is empty'}, status=400)
    cart_items = list(cart.items.select_related('menu_item').all())
    if not cart_items:
        return JsonResponse({'error': 'Cart is empty'}, status=400)

    # Read payment method from POST body
    try:
        body = json.loads(request.body) if request.body else {}
        payment_method = body.get('payment_method', request.POST.get('payment_method', 'card'))
    except json.JSONDecodeError:
        payment_method = request.POST.get('payment_method', 'card')

    # Build delivery address from Address model
    delivery_address = _get_delivery_address(request.user)

    subtotal = round(sum(float(item.total_price) for item in cart_items), 2)
    delivery = 500.0 if subtotal > 0 else 0.0
    total_discount = sum(
        (float(item.menu_item.price) - float(item.menu_item.discounted_price)) * item.quantity
        for item in cart_items
    )
    total = round(subtotal + delivery, 2)

    # Create the order
    order = Order.objects.create(
        user=request.user,
        status='pending',
        subtotal=subtotal,
        delivery=delivery,
        discount=round(total_discount, 2),
        total=total,
        payment_method=payment_method,
        delivery_address=delivery_address,
    )

    # Create order items from cart items
    for ci in cart_items:
        mi = ci.menu_item
        OrderItem.objects.create(
            order=order,
            menu_item=mi,
            name=mi.name,
            quantity=ci.quantity,
            price=mi.price,
            discounted_price=mi.discounted_price,
            total_price=float(mi.discounted_price) * ci.quantity,
        )
        # Increment orders_count on the menu item
        MenuItem.objects.filter(id=mi.id).update(orders_count=F('orders_count') + ci.quantity)

    # Clear the cart
    cart.items.all().delete()

    messages.success(request, 'Your order has been placed successfully!')

    return JsonResponse({
        'status': 'success',
        'order_id': order.order_id,
        'total': float(total),
    })


def orders(request):
    user_orders = Order.objects.filter(user=request.user).prefetch_related('items', 'items__menu_item')
    # Build a score lookup and annotate each item
    user_ratings = {
        r.menu_item_id: r.score
        for r in Rating.objects.filter(user=request.user)
    }
    for order in user_orders:
        for item in order.items.all():
            item.user_score = user_ratings.get(item.menu_item_id, 0) if item.menu_item else 0
    return render(request, './user/orders.html', {
        'orders': user_orders,
    })

# ------------------------------------------------------------
#   Helper: returns full cart data as dict for JSON responses
# ------------------------------------------------------------
# ------------------------------------------------------------
#   Helper: get delivery address from Address model (with fallback)
# ------------------------------------------------------------
def _get_delivery_address(user):
    default_addr = Address.objects.filter(user=user, is_default=True).first()
    if default_addr:
        return default_addr.full_address
    addr = Address.objects.filter(user=user).first()
    if addr:
        return addr.full_address
    if hasattr(user, 'signup'):
        s = user.signup
        parts = [s.street, s.city, s.state]
        return ', '.join(p for p in parts if p)
    return ''


def _cart_items(request):
    if not request.user.is_authenticated:
        return None, []
    cart, _ = Cart.objects.get_or_create(user=request.user)
    return cart, cart.items.select_related('menu_item').all()


def _cart_count(request):
    if not request.user.is_authenticated:
        return 0
    cart, _ = Cart.objects.get_or_create(user=request.user)
    total = 0
    for item in cart.items.all():
        total += item.quantity
    return total


def _get_cart_json(request):
    """Build full cart data dict used by cart_data + cart operation views"""
    cart, cart_items = _cart_items(request)
    user = request.user
    items_data = []
    total_discount = 0.0  # accumulated savings from menu-item discounts

    for item in cart_items:
        mi = item.menu_item
        og_price = float(mi.price)
        disc_price = float(mi.discounted_price)  # respects discount %
        item_total = disc_price * item.quantity
        item_saving = (og_price - disc_price) * item.quantity
        total_discount += item_saving

        items_data.append({
            'id': mi.id,
            'name': mi.name,
            'description': mi.description or '',
            'category': mi.category,
            'price': og_price,                    # original unit price
            'discounted_price': disc_price,       # discounted unit price
            'quantity': item.quantity,
            'total_price': round(item_total, 2), # line total after discount
            'discount_pct': mi.discount or 0,    # e.g. 15 means 15%
        })

    subtotal = round(sum(item.total_price for item in cart_items), 2)
    delivery = 500.0 if subtotal > 0 else 0.0
    total = round(subtotal + delivery, 2)

    # delivery address from Address model
    delivery_address = _get_delivery_address(request.user) if request.user.is_authenticated else ''

    return {
        'status': 'success',
        'items': items_data,
        'subtotal': subtotal,
        'delivery': delivery,
        'discount': round(total_discount, 2),   # total savings from discounts
        'total': total,
        'cart_count': _cart_count(request),
        'item_count': len(items_data),
        'delivery_address': delivery_address,
    }

@csrf_exempt
def cart_data(request):
    """GET endpoint – returns full cart JSON for JS-driven cart page"""
    if request.method == 'GET':
        return JsonResponse(_get_cart_json(request))
    return JsonResponse({'error': 'Invalid request'}, status=400)

def cart(request):
    """Render the cart page – items & summary rendered by Django template"""
    cart, cart_items = _cart_items(request)
    subtotal = sum(item.total_price for item in cart_items)
    delivery = 500 if subtotal > 0 else 0
    # total savings from menu-item discounts
    total_discount = sum(
        (float(item.menu_item.price) - float(item.menu_item.discounted_price)) * item.quantity
        for item in cart_items
    )
    total = subtotal + delivery
    if request.user.is_authenticated:
        delivery_address = _get_delivery_address(request.user)
        addresses = Address.objects.filter(user=request.user)
    else:
        delivery_address = ''
        addresses = []
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'delivery': delivery,
        'discount': total_discount,
        'total': total,
        'cart_count': _cart_count(request),
        'delivery_address': delivery_address,
        'addresses': addresses,
        'paystack_public_key': settings.PAYSTACK_PUBLIC_KEY,
    }
    return render(request, 'cart.html', context)

@csrf_exempt
def add_to_cart(request, item_id):
    """Add item to cart (or +1 if already in cart), return full cart JSON"""
    if request.method == 'POST':
        menu_item = get_object_or_404(MenuItem, id=item_id, is_available=True)
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, menu_item=menu_item)
        if not created:
            cart_item.quantity += 1
            cart_item.save()
        return JsonResponse(_get_cart_json(request))
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def update_cart(request, item_id):
    """Update item quantity (reads from POST or JSON body), return full cart JSON"""
    if request.method == 'POST':
        # Support both form-encoded and JSON bodies
        try:
            body = json.loads(request.body) if request.body else {}
            qty = int(body.get('quantity', request.POST.get('quantity', 1)))
        except (ValueError, json.JSONDecodeError):
            qty = int(request.POST.get('quantity', 1))

        cart = get_object_or_404(Cart, user=request.user)
        cart_item = get_object_or_404(CartItem, cart=cart, menu_item_id=item_id)
        if qty <= 0:
            cart_item.delete()
        else:
            cart_item.quantity = qty
            cart_item.save()

        return JsonResponse(_get_cart_json(request))
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def remove_from_cart(request, item_id):
    """Remove item from cart, return full cart JSON"""
    if request.method == 'POST':
        cart = get_object_or_404(Cart, user=request.user)
        CartItem.objects.filter(cart=cart, menu_item_id=item_id).delete()
        return JsonResponse(_get_cart_json(request))
    return JsonResponse({'error': 'Invalid request'}, status=400)

# ==============================================  PAYSTACK PAYMENT  ==============================================
# Called by the frontend after Paystack popup completes successfully.
# Verifies the transaction with Paystack API, then creates the order.
# Jumia-style flow: verify → create order → clear cart → return order_id
# ==============================================
@csrf_exempt
def verify_paystack_payment(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)

    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=401)

    logger = logging.getLogger(__name__)

    try:
        body = json.loads(request.body)
        reference = body.get('reference')
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({'error': 'Invalid request body'}, status=400)

    if not reference:
        return JsonResponse({'error': 'Reference is required'}, status=400)

    # Idempotency: if this reference was already used, return the existing order (Jumia doesn't double-charge)
    existing = Order.objects.filter(payment_reference=reference, user=request.user).first()
    if existing:
        # Ensure cart is cleared even if previous request cleared it already
        try:
            cart = Cart.objects.get(user=request.user)
            cart.items.all().delete()
        except Cart.DoesNotExist:
            pass
        return JsonResponse({'status': 'success', 'order_id': existing.order_id, 'already_verified': True})

    # ---------------------------------------------------------------
    # Step 1: Verify the transaction with Paystack's verification API
    # ---------------------------------------------------------------
    # The secret key is sent in the Authorization header.
    # Paystack returns the transaction details including amount and status.
    url = f'https://api.paystack.co/transaction/verify/{reference}'
    req = urllib.request.Request(url, headers={
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
    })
    # Try to verify with Paystack. In DEBUG / local with placeholder keys,
    # network blocked or 401 should NOT prevent order creation (frontend already charged via PaystackPop).
    paystack_verified = False
    amount_paid_kobo = None
    try:
        response = urllib.request.urlopen(req, timeout=30)
        result = json.loads(response.read())
    except urllib.error.HTTPError as e:
        body = ''
        try:
            body = e.read().decode('utf-8', 'replace')
        except Exception:
            pass
        logger.error('Paystack verify HTTP %s for ref %s: %s', e.code, reference, body)
        if settings.DEBUG:
            logger.warning('DEBUG=True: bypassing Paystack verification for %s — creating order anyway (simple Paystack mode)', reference)
            result = None
        else:
            return JsonResponse({'error': 'Payment verification failed (HTTP %s): %s' % (e.code, body[:200])}, status=400)
    except Exception:
        logger.error('Paystack verify request failed for ref %s:\n%s', reference, traceback.format_exc())
        if settings.DEBUG:
            logger.warning('DEBUG=True: bypassing Paystack verification for %s — creating order anyway', reference)
            result = None
        else:
            return JsonResponse({'error': 'Payment verification failed. Check network / PAYSTACK_SECRET_KEY.'}, status=400)

    if result is not None:
        # Check that the Paystack API call itself succeeded
        if not result.get('status'):
            logger.error('Paystack verify returned status false for ref %s: %s', reference, result.get('message'))
            if settings.DEBUG:
                logger.warning('DEBUG bypass: treating as verified')
            else:
                return JsonResponse({'error': 'Payment verification failed: %s' % result.get('message','')}, status=400)

        # Confirm the transaction status is 'success' (not failed/abandoned)
        data = result['data']
        if data['status'] != 'success':
            logger.error('Paystack transaction %s status is %s', reference, data.get('status'))
            if settings.DEBUG:
                logger.warning('DEBUG bypass: transaction %s status %s but continuing', reference, data.get('status'))
            else:
                return JsonResponse({'error': 'Payment was not successful (%s)' % data.get('status')}, status=400)

        # Amount is in kobo (Paystack's smallest currency unit).
        amount_paid_kobo = data['amount']
        paystack_verified = True
    else:
        # DEBUG bypass — no amount to check
        paystack_verified = False

    # ---------------------------------------------------------------
    # Step 2: Recalculate the cart total on the server side
    # ---------------------------------------------------------------
    # This prevents tampering — we never trust the amount from the client.
    # We compute the total fresh from the database and compare it
    # against what Paystack reports was actually paid.
    cart = Cart.objects.filter(user=request.user).first()
    if not cart:
        return JsonResponse({'error': 'Cart is empty'}, status=400)
    cart_items = list(cart.items.select_related('menu_item').all())
    if not cart_items:
        return JsonResponse({'error': 'Cart is empty'}, status=400)

    subtotal = round(sum(float(item.total_price) for item in cart_items), 2)
    delivery = 500.0 if subtotal > 0 else 0.0
    total = round(subtotal + delivery, 2)
    total_kobo = int(round(total * 100))

    # Security check: only enforce amount if Paystack was actually verified
    if paystack_verified and amount_paid_kobo is not None:
        if abs(amount_paid_kobo - total_kobo) > 1:
            logger.error('Amount mismatch for ref %s: paid=%s expected=%s', reference, amount_paid_kobo, total_kobo)
            if settings.DEBUG:
                logger.warning('DEBUG bypass: amount mismatch but continuing')
            else:
                return JsonResponse({'error': 'Amount mismatch — expected ₦%s but paid ₦%s' % (total, amount_paid_kobo/100)}, status=400)

    # ---------------------------------------------------------------
    # Step 3: Build the delivery address from the Address model
    # ---------------------------------------------------------------
    delivery_address = _get_delivery_address(request.user)

    # Calculate the total discount applied across all cart items
    total_discount = sum(
        (float(item.menu_item.price) - float(item.menu_item.discounted_price)) * item.quantity
        for item in cart_items
    )

    # ---------------------------------------------------------------
    # Step 4: Create the order and order items in the database
    # ---------------------------------------------------------------
    # The order is marked as 'pending' (awaiting restaurant confirmation)
    # but the payment_status is set to 'paid' since Paystack confirmed it.
    order = Order.objects.create(
        user=request.user,
        status='pending',
        subtotal=subtotal,
        delivery=delivery,
        discount=round(total_discount, 2),
        total=total,
        payment_method='card',
        payment_reference=reference,
        payment_status='paid',
        delivery_address=delivery_address,
    )

    # Create one OrderItem per CartItem and update the menu item's order count
    for ci in cart_items:
        mi = ci.menu_item
        OrderItem.objects.create(
            order=order,
            menu_item=mi,
            name=mi.name,
            quantity=ci.quantity,
            price=mi.price,
            discounted_price=mi.discounted_price,
            total_price=float(mi.discounted_price) * ci.quantity,
        )
        MenuItem.objects.filter(id=mi.id).update(orders_count=F('orders_count') + ci.quantity)

    # Clear the user's cart now that the order has been created
    cart.items.all().delete()

    Notification.objects.create(title=f"New Order Placed: #{order.order_id}", body=f"Order #{order.order_id} for ₦{total} was placed by {request.user.username}.", notification_type='system')
    messages.success(request, 'Your order has been placed successfully!')

    return JsonResponse({
        'status': 'success',
        'order_id': order.order_id,
    })

    

def track_order(request):
    return render(request, './user/track_order.html')

def setting(request):
    addresses = Address.objects.filter(user=request.user)
    return render(request, './user/setting.html', {'addresses': addresses})


@login_required(login_url='login')
def add_address(request):
    if request.method == 'POST':
        label = request.POST.get('label', 'home')
        street = request.POST.get('street', '').strip()
        city = request.POST.get('city', '').strip()
        state = request.POST.get('state', '').strip()
        lga = request.POST.get('lga', '').strip()

        if not street or not city or not state:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'error': 'All address fields are required.'}, status=400)
            messages.error(request, "All address fields are required.")
            return redirect('/setting')

        is_default = Address.objects.filter(user=request.user).count() == 0
        addr = Address.objects.create(
            user=request.user,
            label=label,
            street=street,
            city=city,
            state=state,
            lga=lga,
            is_default=is_default,
        )
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'address_id': addr.id})
        messages.success(request, f"{label.capitalize()} address added successfully.")
    return redirect('/setting')


@login_required(login_url='login')
def edit_address(request, address_id):
    if request.method == 'POST':
        addr = get_object_or_404(Address, id=address_id, user=request.user)
        addr.label = request.POST.get('label', addr.label)
        addr.street = request.POST.get('street', addr.street).strip()
        addr.city = request.POST.get('city', addr.city).strip()
        addr.state = request.POST.get('state', addr.state).strip()
        addr.lga = request.POST.get('lga', addr.lga).strip()
        addr.save()
        messages.success(request, "Address updated successfully.")
    return redirect('/setting')


@login_required(login_url='login')
def delete_address(request, address_id):
    if request.method == 'POST':
        addr = get_object_or_404(Address, id=address_id, user=request.user)
        was_default = addr.is_default
        addr.delete()
        if was_default:
            first = Address.objects.filter(user=request.user).first()
            if first:
                first.is_default = True
                first.save()
        messages.success(request, "Address deleted successfully.")
    return redirect('/setting')


@login_required(login_url='login')
def set_default_address(request, address_id):
    if request.method == 'POST':
        addr = get_object_or_404(Address, id=address_id, user=request.user)
        Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
        addr.is_default = True
        addr.save()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})
        messages.success(request, "Default address updated.")
    return redirect('/setting')

def delete_account_page(request):
    if request.method == 'POST':
        try:
            signup_row = SignUp.objects.get(user=request.user)
            Notification.objects.create(title="Account Self-Deleted", body=f"{signup_row.name} ({signup_row.email}) has deleted their own account.", notification_type='system')
            signup_row.status = 'deleted'
            signup_row.is_verified = False
            signup_row.save()
        except SignUp.DoesNotExist:
            pass
        logout(request)
        messages.success(request, "Your account has been deleted. You can no longer access this account.")
        return redirect('/')
    return redirect('/setting')

# ==============================================  End User Views Section ============================================== 


# ==============================================  ADMIN PAGES ============================================== 
# @admin_required
def dashboard_page(request):
    return render(request, './ADMIN/dashboard.html')

# @admin_required
def add_admin_page(request):
    return render(request, './ADMIN/for_admin/add_admin.html')

# @admin_required
def admin_profile_page(request):
    return render(request, './ADMIN/for_admin/admin_profile.html')

# ==============================================   Menu Management  ============================================== 
# @admin_required
def menu_management_page(request):
    category_filter = request.GET.get('category', '')
    sort_by = request.GET.get('sort', '-date_added')

    menu_items = MenuItem.objects.all()

    if category_filter:
        menu_items = menu_items.filter(category=category_filter)

    sort_options = {
        'newest': '-date_added',
        'oldest': 'date_added',
        'price_low': 'price',
        'price_high': '-price',
        'name_asc': 'name',
        'name_desc': '-name',
        'orders': '-orders_count',
    }
    menu_items = menu_items.order_by(sort_options.get(sort_by, '-date_added'))

    total_items = MenuItem.objects.all().count()
    in_stock = menu_items.filter(is_available=True).count()
    out_of_stock = menu_items.filter(is_available=False).count()
    avg_rating = MenuItem.objects.aggregate(Avg('rating'))['rating__avg'] or 0

    context = {
        'menu_items': menu_items,
        'total_items': total_items,
        'in_stock': in_stock,
        'out_of_stock': out_of_stock,
        'avg_rating': avg_rating,
        'current_category': category_filter,
        'current_sort': sort_by,
    }
    return render(request, './ADMIN/menu_management.html', context)

# @admin_required
def add_menu_item(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        category = request.POST.get('category')
        price = request.POST.get('price')
        discount = request.POST.get('discount') or 0
        prep_time = request.POST.get('prep_time') or None
        description = request.POST.get('description')
        ingredients = request.POST.get('ingredients')
        is_available = request.POST.get('is_available') == 'on'
        is_featured = request.POST.get('is_featured') == 'on'
        image = request.FILES.get('image')

        MenuItem.objects.create(
            name=name,
            category=category,
            price=price,
            discount=discount,
            prep_time=prep_time,
            description=description,
            ingredients=ingredients,
            is_available=is_available,
            is_featured=is_featured,
            image=image,
        )
        Notification.objects.create(title=f"New Menu Item: {name}", body=f"A new menu item '{name}' was added to the {category} category at ₦{price}.", notification_type='system')
        messages.success(request, 'Menu item added successfully.')
    return redirect('menu_management')

# @admin_required
def edit_menu_item(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)
    if request.method == 'POST':
        item.name = request.POST.get('name')
        item.category = request.POST.get('category')
        item.price = request.POST.get('price')
        item.discount = request.POST.get('discount') or 0
        item.prep_time = request.POST.get('prep_time') or None
        item.description = request.POST.get('description')
        item.ingredients = request.POST.get('ingredients')
        item.is_available = request.POST.get('is_available') == 'on'
        item.is_featured = request.POST.get('is_featured') == 'on'
        if request.FILES.get('image'):
            item.image = request.FILES['image']
        item.save()
        Notification.objects.create(title=f"Menu Item Updated: {item.name}", body=f"Menu item '{item.name}' was updated.", notification_type='system')
        messages.success(request, 'Menu item updated successfully.')
    return redirect('menu_management')

# @admin_required
def delete_menu_item(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)
    name = item.name
    item.delete()
    Notification.objects.create(title=f"Menu Item Deleted: {name}", body=f"Menu item '{name}' was deleted from the platform.", notification_type='system')
    messages.success(request, 'Menu item deleted successfully.')
    return redirect('menu_management')

# @admin_required
def toggle_menu_item(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)
    item.is_available = not item.is_available
    item.save()
    return redirect('menu_management')

import csv
# @admin_required
def export_menu_csv(request):
    category_filter = request.GET.get('category', '')
    sort_by = request.GET.get('sort', '-date_added')

    items = MenuItem.objects.all()

    if category_filter:
        items = items.filter(category=category_filter)

    sort_options = {
        'newest': '-date_added',
        'oldest': 'date_added',
        'price_low': 'price',
        'price_high': '-price',
        'name_asc': 'name',
        'name_desc': '-name',
        'orders': '-orders_count',
    }
    items = items.order_by(sort_options.get(sort_by, '-date_added'))

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="menu_items.csv"'

    writer = csv.writer(response)
    writer.writerow(['S/N', 'Name', 'Category', 'Price (₦)', 'Discount (%)', 'Prep Time (min)',
                     'Description', 'Ingredients', 'Available', 'Featured', 'Date Added', 'Orders'])

    for i, item in enumerate(items, start=1):
        writer.writerow([
            i,
            item.name,
            item.get_category_display(),
            item.price,
            item.discount or 0,
            item.prep_time or '',
            item.description or '',
            item.ingredients or '',
            'Yes' if item.is_available else 'No',
            'Yes' if item.is_featured else 'No',
            item.date_added.strftime('%Y-%m-%d %H:%M') if item.date_added else '',
            item.orders_count,
        ])

    return response

# ==============================================   Order Management  ============================================== 
# @admin_required
def order_management_page(request):
    orders = Order.objects.all().prefetch_related('items', 'user__signup')

    # Sorting
    sort_by = request.GET.get('sort_by', '')
    if sort_by == 'newest':
        orders = orders.order_by('-created_at')
    elif sort_by == 'oldest':
        orders = orders.order_by('created_at')
    elif sort_by == 'amount_high':
        orders = orders.order_by('-total')
    elif sort_by == 'amount_low':
        orders = orders.order_by('total')
    else:
        orders = orders.order_by('-created_at')

    total_orders = Order.objects.count()
    pending = Order.objects.filter(status='pending').count()
    preparing = Order.objects.filter(status='preparing').count()
    out_for_delivery = Order.objects.filter(status='out_for_delivery').count()
    delivered = Order.objects.filter(status='delivered').count()
    cancelled = Order.objects.filter(status='cancelled').count()
    revenue = sum(o.total for o in Order.objects.filter(status='delivered'))

    context = {
        'orders': orders,
        'total_orders': total_orders,
        'pending_count': pending,
        'preparing_count': preparing,
        'delivering_count': out_for_delivery,
        'delivered_count': delivered,
        'cancelled_count': cancelled,
        'revenue': revenue,
    }
    return render(request, './ADMIN/order_management.html', context)


# @admin_required
@csrf_exempt
def update_order_status(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)
    order_id = request.POST.get('order_id', '')
    status = request.POST.get('status', '')
    valid_statuses = dict(Order.STATUS_CHOICES).keys()
    if status not in valid_statuses:
        return JsonResponse({'error': 'Invalid status'}, status=400)
    try:
        order = Order.objects.get(order_id=order_id)
        order.status = status
        order.save()
        if status == 'delivered':
            Notification.objects.create(title=f"Order Delivered: #{order_id}", body=f"Order #{order_id} was delivered successfully to {order.user.username}.", notification_type='system')
        return JsonResponse({'status': 'success'})
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)


# @admin_required
@csrf_exempt
def delete_order(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)
    order_id = request.POST.get('order_id', '')
    try:
        Order.objects.get(order_id=order_id).delete()
        return JsonResponse({'status': 'success'})
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)

# ============================================== customers_page ============================================== 
# @admin_required
def customers_page(request):
    """Display all non-admin users with optional name search, status filter, and autocomplete.

    The template always needs the full list of users for the autocomplete widget,
    so we include `get_all_users` in every render context.
    """

    base_qs = SignUp.objects.filter(is_superuser=0).select_related('user')
    # Annotate each user with real order count & total spent from Order model
    all_users = base_qs.annotate(
        total_orders=Count('user__orders'),
        total_spent=Sum('user__orders__total'),
    )
    
    # Handle sorting
    sort_by = request.GET.get('sort_by')
    if sort_by == 'newest':
        all_users = all_users.order_by('-user__date_joined')
    elif sort_by == 'spend':
        all_users = all_users.order_by('-total_spent')
    elif sort_by == 'name_asc':
        all_users = all_users.order_by('name')
    elif sort_by == 'orders':
        all_users = all_users.order_by('-total_orders')
    else:
        all_users = all_users.order_by('name')
    
    # --- STATUS FILTER: ?status=active | banned | inactive ---
    # Allows the customers list to be filtered by account status
    status_filter = request.GET.get('status')
    if status_filter == 'active':
        all_users = all_users.filter(status='active')
    elif status_filter == 'banned':
        all_users = all_users.filter(status='blocked')
    elif status_filter == 'deleted':
        all_users = all_users.filter(status='deleted')
    elif status_filter == 'inactive':
        # Inactive = users whose status is neither active, blocked, nor deleted (NULL or empty)
        all_users = all_users.exclude(status__in=['active', 'blocked', 'deleted']).filter(Q(status__isnull=True) | Q(status=''))
    
    # --- STATS COUNTS for dashboard cards ---
    count_all_user = SignUp.objects.filter(is_superuser=0).count()
    thirty_days_ago = timezone.now() - timedelta(days=30)
    count_active_user = SignUp.objects.filter(is_superuser=0, status='active').count()
    count_banned_user = SignUp.objects.filter(is_superuser=0, status='blocked').count()
    count_deleted_user = SignUp.objects.filter(is_superuser=0, status='deleted').count()
    count_inactive_user = SignUp.objects.filter(is_superuser=0).exclude(status__in=['active', 'blocked', 'deleted']).count()
    count_new_user = SignUp.objects.filter(is_superuser=0, user__date_joined__gte=thirty_days_ago).count()

    context = {
        'count_all_user': count_all_user,
        'count_active_user': count_active_user,
        'count_new_user': count_new_user,
        'count_banned_user': count_banned_user,
        'count_deleted_user': count_deleted_user,
        'count_inactive_user': count_inactive_user,
        'current_status': status_filter or '',
    }

    if request.method == 'POST':
        search_name = request.POST.get('search_name', '').strip()
        get_filter = base_qs.filter(
            Q(name__icontains=search_name) | Q(email__icontains=search_name),
        ).annotate(
            total_orders=Count('user__orders'),
            total_spent=Sum('user__orders__total'),
        )
        get_filter_count = get_filter.count()
        context.update({'get_filter': get_filter, 'get_filter_count': get_filter_count, 'get_all_users': all_users})
    else:
        context.update({'get_all_users': all_users})

    return render(request, './ADMIN/customers.html', context)

# @admin_required
def export_customers_csv(request):
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    users = SignUp.objects.filter(is_superuser=0).select_related('user').annotate(
        total_orders=Count('user__orders'),
        total_spent=Sum('user__orders__total'),
    ).order_by('name')

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Customers'

    # Styles
    header_font = Font(name='Calibri', bold=True, color='FFFFFF', size=12)
    header_fill = PatternFill(start_color='FF6600', end_color='FF6600', fill_type='solid')
    header_align = Alignment(horizontal='center', vertical='center')
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin'),
    )
    center_align = Alignment(horizontal='center', vertical='center')

    # Headers
    headers = ['S/N', 'Name', 'Email', 'Phone', 'Gender', 'Total Orders', 'Total Spent (₦)', 'Joined', 'Status']
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=h)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_align
        cell.border = thin_border

    # Data rows
    for i, u in enumerate(users, start=1):
        row = i + 1
        values = [
            i,
            u.name or '',
            u.email or '',
            u.phone or '',
            u.gender or '',
            u.total_orders or 0,
            u.total_spent or 0,
            u.user.date_joined.strftime('%Y-%m-%d') if u.user.date_joined else '',
            u.status if u.status in ('active', 'blocked') else 'inactive',
        ]
        for col, v in enumerate(values, 1):
            cell = ws.cell(row=row, column=col, value=v)
            cell.alignment = center_align
            cell.border = thin_border

    # Auto-column widths
    for col in range(1, len(headers) + 1):
        ws.column_dimensions[get_column_letter(col)].width = 18

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="customers.xlsx"'
    wb.save(response)
    return response

# @admin_required
def blockpage(request, id):
    get_row_id = SignUp.objects.get(user_id=id)
    get_row_id.status = "blocked"
    get_name = get_row_id.name
    get_row_id.save()
    Notification.objects.create(title=f"User Banned: {get_name}", body=f"{get_name} was banned following admin action. All active sessions revoked.", notification_type='system')
    messages.info(request, f"You have successfully blocked {get_name}")
    return redirect('customers')

# @admin_required
def unblockpage(request, id):
    get_row_id = SignUp.objects.get(user_id=id)
    get_row_id.status = "active"
    get_name = get_row_id.name
    get_row_id.save()
    Notification.objects.create(title=f"User Unblocked: {get_name}", body=f"{get_name} was unblocked and can now access the platform.", notification_type='system')
    messages.info(request, f"You have successfully unblocked {get_name}")
    return redirect('customers')

# @admin_required
def deletepage(request, id):
    get_row_id = SignUp.objects.get(user_id=id)
    get_name = get_row_id.name
    get_auth_row = get_row_id.user
    get_row_id.delete()
    get_auth_row.delete()
    Notification.objects.create(title=f"User Deleted: {get_name}", body=f"{get_name} was permanently deleted from the platform.", notification_type='system')
    messages.info(request, f"You have successfully deleted {get_name}")
    return redirect('customers')
# ============================================== customers_page ============================================== 

# @admin_required
def view_single_user_page(request, user_id):
    get_user_row = SignUp.objects.get(user_id = user_id)
    
    # Stats counts displayed in the view_single_user dashboard cards
    count_all_user = SignUp.objects.filter(is_superuser=0).count()
    count_active_user = SignUp.objects.filter(is_superuser=0, status='active').count()
    count_new_user = SignUp.objects.filter(is_superuser=0).count()
    count_banned_user = SignUp.objects.filter(is_superuser=0, status='blocked').count()
    count_deleted_user = SignUp.objects.filter(is_superuser=0, status='deleted').count()
    count_inactive_user = SignUp.objects.filter(is_superuser=0).exclude(status__in=['active', 'blocked', 'deleted']).count()
    
    return render(request, './ADMIN/view_single_user.html', {
        'get_user_row': get_user_row,
        'count_all_user': count_all_user,
        'count_active_user': count_active_user,
        'count_new_user': count_new_user,
        'count_banned_user': count_banned_user,
        'count_deleted_user': count_deleted_user,
        'count_inactive_user': count_inactive_user,
    })


# @admin_required
def settings_page(request):
    return render(request, './ADMIN/settings.html')

from django.views.decorators.http import require_POST

@require_POST
def mark_notification_read(request):
    try:
        data = json.loads(request.body)
        nid = data.get('id')
    except Exception:
        nid = request.POST.get('id')
    if nid:
        Notification.objects.filter(id=nid).update(is_read=True)
        return JsonResponse({'ok': True})
    # Mark all as read
    Notification.objects.filter(is_read=False).update(is_read=True)
    return JsonResponse({'ok': True})


# @admin_required
def notifications_page(request):
    all_notifications = Notification.objects.all()
    # For autocomplete in search
    get_all_users = SignUp.objects.filter(is_superuser=0)

    if request.method == 'POST':
        title = request.POST.get('notif_title', '').strip()
        body = request.POST.get('notif_body', '').strip()
        audience = request.POST.get('notif_audience', 'all')
        if title and body:
            Notification.objects.create(title=title, body=body, target_audience=audience)
            messages.success(request, f"Notification sent to {audience}")
        else:
            messages.error(request, "Title and body are required.")
        return redirect('notifications')

    return render(request, './ADMIN/notifications.html', {
        'notifications': all_notifications,
        'get_all_users': get_all_users,
    })


def user_notifications_page(request):
    notifications = Notification.objects.filter(is_active=True)
    return render(request, './user/notifications.html', {
        'notifications': notifications,
    })