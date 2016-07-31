from django.contrib import admin
from .models import EndUser, ShippingUser, Order, OrderStatus, QuoteAssignShippingUser, Quote, QuoteBid

# Register your models here.
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'weight', 'shipping_user_id', 'sender',  'receiver',  'create_time')

class OrderStatusAdmin(admin.ModelAdmin):
	list_display = ('order', 'id', 'time', 'status', 'location', 'primKey')

class QuoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'weight', 'sender_address', 'receiver_address',  'create_time', 'height', 'width', 'length', 'sender_info', 'notes')

class QuoteAssignShippingUserAdmin(admin.ModelAdmin):
	list_display = ('quote', 'shipping_user_id', 'primKey')

class QuoteBidAdmin(admin.ModelAdmin):
	list_display = ('quote', 'shipping_user_id', 'bid_price', 'primKey')

class EndUserAdmin(admin.ModelAdmin):
	list_display = ('user_id', 'name', 'phone_number', 'company_name', 'address', 'postcode')

class ShippingUserAdmin(admin.ModelAdmin):
	list_display = ('user_id', 'name', 'phone_number', 'company_name', 'address', 'postcode')

admin.site.register(EndUser, EndUserAdmin)
admin.site.register(ShippingUser, ShippingUserAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderStatus, OrderStatusAdmin)
admin.site.register(Quote, QuoteAdmin)
admin.site.register(QuoteAssignShippingUser, QuoteAssignShippingUserAdmin)
admin.site.register(QuoteBid, QuoteBidAdmin)