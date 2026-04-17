from django.contrib import admin
from .models import Order, OrderItem, OrderStatus, PickupPoint

admin.site.register(OrderStatus)
admin.site.register(PickupPoint)
admin.site.register(Order)
admin.site.register(OrderItem)
