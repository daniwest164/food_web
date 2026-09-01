from django.db import models
from django.db.models import Avg, Sum
from django.contrib.auth.models import User, auth
from django_resized import ResizedImageField
import uuid


# Create your models here. 
# Lets create a table for signup

CATEGORY_CHOICES = [
    ('rice', 'Rice'),
    ('swallow', 'Swallow'),
    ('soups', 'Soups'),
    ('small_chops', 'Small Chops'),
    ('grills', 'Grills'),
    ('drinks', 'Drinks'),
    ('dessert', 'Dessert'),
    ('others', 'Others'),
]

class MenuItem(models.Model):
    image = models.ImageField(upload_to='menu_items/', null=True, blank=True)
    name = models.CharField(max_length=500, null=True, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.IntegerField(default=0, null=True, blank=True)
    prep_time = models.IntegerField(null=True, blank=True, help_text="Preparation time in minutes")
    description = models.TextField(null=True, blank=True)
    ingredients = models.TextField(null=True, blank=True, help_text="Comma-separated list of ingredients")
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now_add=True)
    orders_count = models.IntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)

    @property
    def discounted_price(self):
        if self.discount:
            return self.price * (100 - self.discount) / 100
        return self.price

    @property
    def image_url(self):
        if self.image and self.image.name:
            try:
                return self.image.url
            except Exception:
                return ''
        return ''

    class Meta:
        db_table = 'menu_item'
        ordering = ['-date_added']

    def __str__(self):
        return self.name

class SignUp(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) # link to defaul auth table
    passport = ResizedImageField(size=[320,300], upload_to="passport/", null=True, blank=True)
    name = models.CharField(max_length=500, null=True, blank=True)
    email = models.CharField(max_length=500, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)# Date of Birth
    gender = models.CharField(max_length=500, null=True, blank=True)
    location = models.CharField(max_length=500, null=True, blank=True)
    state = models.CharField(max_length=500, null=True, blank=True)
    city = models.CharField(max_length=500, null=True, blank=True)
    street = models.CharField(max_length=500, null=True, blank=True)
    username = models.CharField(max_length=500, null=True, blank=True)
    password = models.CharField(max_length=500, null=True, blank=True)
    #  form part for the signup and login section in the database control
    is_superuser = models.CharField(max_length=500, null=True, blank=True)# if admin(1) or user(0)
    reset = models.CharField(max_length=500, null=True, blank=True)
    uid = models.CharField(max_length=50, null=True, blank=True, unique=True)
    status = models.CharField(max_length=500, null=True, blank=True)
    otp = models.CharField(max_length=6, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    verify_token = models.CharField(max_length=100, null=True, blank=True, unique=True)

    @property
    def passport_url(self):
        if self.passport and self.passport.name:
            try:
                return self.passport.url
            except Exception:
                return ''
        return ''
    
    class Meta: # Class Meta are variables used to manage your table
        managed = True # Django should manage your table
        db_table = 'signup' # define your table name here

class Address(models.Model):
    LABEL_CHOICES = [
        ('home', 'Home'),
        ('work', 'Work'),
        ('other', 'Other'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    label = models.CharField(max_length=20, choices=LABEL_CHOICES, default='home')
    street = models.CharField(max_length=500)
    city = models.CharField(max_length=200)
    state = models.CharField(max_length=200)
    lga = models.CharField(max_length=200, blank=True, default='')
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'address'
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f'{self.label}: {self.street}, {self.city}, {self.state}'

    @property
    def full_address(self):
        return ', '.join(p for p in [self.street, self.lga, self.city, self.state] if p)

    def save(self, *args, **kwargs):
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cart'

    @property
    def total_items(self):
        return self.items.aggregate(total=Sum('quantity'))['total'] or 0

    @property
    def subtotal(self):
        return sum(item.total_price for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cart_item'
        unique_together = ('cart', 'menu_item')

    @property
    def total_price(self):
        return float(self.menu_item.discounted_price) * self.quantity

    def __str__(self):
        return f'{self.menu_item.name} x {self.quantity}'


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('preparing', 'Preparing'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_id = models.CharField(max_length=20, unique=True, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=20, default='card')
    # Paystack transaction reference returned after successful payment
    payment_reference = models.CharField(max_length=100, null=True, blank=True)
    # Tracks payment state: pending | paid | failed | refunded
    payment_status = models.CharField(max_length=20, default='pending')
    delivery_address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'order'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = 'PDORD-' + uuid.uuid4().hex[:8].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Order {self.order_id} - {self.user.username}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=500)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'order_item'

    def __str__(self):
        return f'{self.name} x {self.quantity}'


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='ratings')
    score = models.IntegerField(choices=[(1,1),(2,2),(3,3),(4,4),(5,5)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'rating'
        unique_together = ('user', 'menu_item')

    def __str__(self):
        return f'{self.user} - {self.menu_item} - {self.score}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_menu_item_rating()

    def delete(self, *args, **kwargs):
        menu_item = self.menu_item
        super().delete(*args, **kwargs)
        self.update_menu_item_rating(menu_item)

    def update_menu_item_rating(self, menu_item=None):
        if menu_item is None:
            menu_item = self.menu_item
        avg = menu_item.ratings.aggregate(Avg('score'))['score__avg'] or 0
        MenuItem.objects.filter(id=menu_item.id).update(rating=round(avg, 1))


class Notification(models.Model):
    AUDIENCE_CHOICES = [
        ('all', 'All Users'),
        ('customers', 'Customers Only'),
        ('vendors', 'Vendors Only'),
        ('riders', 'Riders Only'),
    ]
    title = models.CharField(max_length=255)
    body = models.TextField()
    target_audience = models.CharField(max_length=20, choices=AUDIENCE_CHOICES, default='all')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_read = models.BooleanField(default=False)
    notification_type = models.CharField(max_length=20, default='manual')  # 'manual' or 'system'

    class Meta:
        db_table = 'notification'
        ordering = ['-created_at']

    def __str__(self):
        return self.title