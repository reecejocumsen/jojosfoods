from django.contrib import admin
from django.contrib.sessions.models import Session

from .models import Item, OrderItem, Order, UserHistory, Cart

# Register your models here.

admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(UserHistory)
admin.site.register(Cart)

admin.site.register(Session)
