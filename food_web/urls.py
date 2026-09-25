"""
URL configuration for food_web project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from food import views

#for images upload as well
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # NAVBAR LINKS PAGES
    path('', views.home, name="home"),
    path('menu', views.menu,  name="menu"),
    path('about', views.about, name="about"),
    path('contact', views.contact, name="contact"),
    #  ========================== CART  ========================== 
    path('cart', views.cart, name="cart"),
    path('cart-data/', views.cart_data, name="cart_data"),
    path('clear-cart/', views.clear_cart, name="clear_cart"),
    path('add_to_cart/<int:item_id>', views.add_to_cart, name="add_to_cart"),
    path('update_cart/<int:item_id>', views.update_cart, name="update_cart"),
    path('remove_from_cart/<int:item_id>', views.remove_from_cart, name="remove_from_cart"),
    path('place_order/', views.place_order, name="place_order"),
    # Paystack payment verification — called by cart.js after successful Paystack popup
    path('verify-paystack-payment/', views.verify_paystack_payment, name="verify_paystack_payment"),
    
    # FORM PAGES
    path('sign_up', views.sign_up_page, name="sign_up"),
    path('verify_email', views.verify_email_page, name="verify_email"),
    path('login', views.login_page, name="login"),
    path('forget_password', views.forget_password_page, name="forget_password"),
    path('reset_password/<int:id>', views.reset_password_page, name="reset_password"), 

    # GOOGLE OAUTH
    path('auth/google', views.google_auth_initiate, name="google_auth"),
    path('auth/google/callback', views.google_auth_callback, name="google_auth_callback"), 

    # LEGAL PAGES
    path('terms', views.terms_of_service, name="terms_of_service"),
    path('privacy', views.privacy_policy, name="privacy_policy"), 

    # User Profile pages
    path('profile', views.profile, name="profile"),
    path('orders', views.orders, name="orders"),
    # Jumia-style order detail: shows like https://www.jumia.com.ng/customer/order/detail/<id>/
    path('order/<str:order_id>/', views.order_detail, name="order_detail"),
    path('customer/order/detail/<str:order_id>/', views.order_detail, name="jumia_order_detail"),
    # Jumia-style track: https://www.jumia.com.ng/customer/order/track/<id>/
    path('order/track/<str:order_id>/', views.track_order, name="order_track"),
    path('customer/order/track/<str:order_id>/', views.track_order, name="jumia_order_track"),
    path('cancel_order/<str:order_id>/', views.cancel_order, name="cancel_order"),


    path('track_order', views.track_order, name="track_order"),
    path('track_order/<str:order_id>/', views.track_order, name="track_order_with_id"),
    path('setting', views.setting, name="setting"),
    path('add_address', views.add_address, name="add_address"),
    path('edit_address/<int:address_id>', views.edit_address, name="edit_address"),
    path('delete_address/<int:address_id>', views.delete_address, name="delete_address"),
    path('set_default_address/<int:address_id>', views.set_default_address, name="set_default_address"),
    path('logout', views.logout_page),
    path('delete_account', views.delete_account_page, name="delete_account"),

    # ADMIN PAGES
    path('dashboard', views.dashboard_page, name="dashboard"),
    path('add_admin', views.add_admin_page, name="add_admin"), 
    path('admin_profile', views.admin_profile_page, name="admin_profile"), 
    path('menu_management', views.menu_management_page, name="menu_management"), 

    path('add_menu_item', views.add_menu_item, name="add_menu_item"),
    path('edit_menu_item/<int:item_id>', views.edit_menu_item, name="edit_menu_item"),
    path('delete_menu_item/<int:item_id>', views.delete_menu_item, name="delete_menu_item"),
    path('toggle_menu_item/<int:item_id>', views.toggle_menu_item, name="toggle_menu_item"),
    path('export_menu_csv', views.export_menu_csv, name="export_menu_csv"),
    path('rate_item/<int:item_id>', views.rate_item, name="rate_item"),
    path('submit_rating/<int:item_id>', views.submit_rating, name="submit_rating"),
    
    path('order_management', views.order_management_page, name="order_management"),
    path('update_order_status/', views.update_order_status, name="update_order_status"),
    path('delete_order/', views.delete_order, name="delete_order"),
    path('customers', views.customers_page, name="customers"),
    path('export_customers_csv/', views.export_customers_csv, name="export_customers_csv"),

    path('block/<int:id>', views.blockpage, name="block"),
    path('unblock/<int:id>', views.unblockpage, name="unblock"),
    path('delete/<int:id>', views.deletepage, name="delete"),

    path('view_single_user/<int:user_id>', views.view_single_user_page, name="view_single_user"), 


    path('settings', views.settings_page, name="settings"), 
    path('notifications', views.notifications_page, name="notifications"),
    path('mark_notification_read/', views.mark_notification_read, name="mark_notification_read"), 

    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)