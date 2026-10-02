from django.contrib import admin
from .models import MenuItem, SignUp, Cart, CartItem, Notification, NotificationRead


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'visibility', 'target_audience', 'user', 'is_active', 'is_read', 'created_at')
    list_filter = ('visibility', 'notification_type', 'target_audience', 'is_active', 'is_read')
    search_fields = ('title', 'body')
    readonly_fields = ('created_at',)


@admin.register(NotificationRead)
class NotificationReadAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification', 'read_at')
    list_filter = ('read_at',)

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'discount', 'is_available', 'is_featured', 'date_added')
    list_filter = ('category', 'is_available', 'is_featured')
    search_fields = ('name', 'description', 'ingredients')

admin.site.register(SignUp)
admin.site.register(Cart)
admin.site.register(CartItem)