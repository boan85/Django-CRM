from django.contrib import admin

# Register your models here.
from wc_orders.models import OrderShipping, OrderBilling, Order, CustomFields, OrderNote

admin.site.register(OrderShipping)
admin.site.register(OrderBilling)
admin.site.register(Order)
admin.site.register(CustomFields)
admin.site.register(OrderNote)