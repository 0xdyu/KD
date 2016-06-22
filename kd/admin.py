from django.contrib import admin
from .models import EndUser, ShippingUser, Order, OrderStatus

# Register your models here.
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'weight', 'shipping_user_id', 'sender_id', 'receiver_id')

class OrderStatusAdmin(admin.ModelAdmin):
	list_display = ('order_id', 'time', 'status', 'location', 'primKey')

class EndUserAdmin(admin.ModelAdmin):
	list_display = ('user_id', 'name', 'phone_number', 'company_name', 'address', 'postcode')

class ShippingUserAdmin(admin.ModelAdmin):
	list_display = ('user_id', 'name', 'phone_number', 'company_name', 'address', 'postcode')

admin.site.register(EndUser, EndUserAdmin)
admin.site.register(ShippingUser, ShippingUserAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderStatus, OrderStatusAdmin)