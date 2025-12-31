from django.contrib import admin

from .models import User
from .models import Restaurant
from .models import Item   
from .models import Cart
from .models import Coupon
# Register your models here.
admin.site.register(User)
admin.site.register(Restaurant)
admin.site.register(Item)
admin.site.register(Cart)
admin.site.register(Coupon)