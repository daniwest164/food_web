from django.contrib import admin
from .models import MenuItem, SignUp, Cart, CartItem

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'discount', 'is_available', 'is_featured', 'date_added')
    list_filter = ('category', 'is_available', 'is_featured')
    search_fields = ('name', 'description', 'ingredients')

admin.site.register(SignUp)
admin.site.register(Cart)
admin.site.register(CartItem)