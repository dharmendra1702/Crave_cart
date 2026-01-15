from django.db import models
from cloudinary.models import CloudinaryField
import random
from django.shortcuts import render
from django.utils.timezone import localtime
from django.utils import timezone

class User(models.Model):
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30) 
    password = models.CharField(max_length=128)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=15)
    address = models.TextField()

    def __str__(self):
        return self.username


class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    cuisine = models.CharField(max_length=255)
    rating = models.DecimalField(max_digits=3, decimal_places=1)
    location = models.CharField(max_length=255)

    picture = models.URLField(blank=True, null=True)
    picture_file = CloudinaryField("restaurant_image", blank=True, null=True)

    def __str__(self):
        return self.name


class Item(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    vegeterian = models.BooleanField(default=False)

    picture = models.URLField(blank=True, null=True)
    picture_file = CloudinaryField("menu_image", blank=True, null=True)

    def __str__(self):
        return self.name


class Cart(models.Model):
    username = models.CharField(max_length=150)

    def __str__(self):
        return f"Cart ({self.username})"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.item.name} x {self.quantity}"


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)

    DISCOUNT_CHOICES = (
        ("percent", "Percentage"),
        ("flat", "Flat"),
    )
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_CHOICES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)

    min_order_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )

    is_active = models.BooleanField(default=True)

    # ✅ USAGE LIMIT SYSTEM
    usage_limit = models.PositiveIntegerField(default=1)
    used_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(default=timezone.now)

    def is_available(self):
        return self.is_active and self.used_count < self.usage_limit

    def __str__(self):
        return self.code



from django.utils import timezone

from django.db import models
from django.utils import timezone
from django.utils.timezone import localtime
import random

class Order(models.Model):
    STATUS_CHOICES = [
        ("PLACED", "Placed"),
        ("PREPARING", "Preparing"),
        ("OUT_FOR_DELIVERY", "Out for Delivery"),
        ("DELIVERED", "Delivered"),
        ("CANCELLED", "Cancelled"),
    ]

    order_number = models.CharField(max_length=11, unique=True, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    coupon_code = models.CharField(max_length=50, blank=True, null=True)
    coupon_discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    subtotal = models.FloatField(default=0)
    gst_percent = models.PositiveIntegerField(default=5)
    gst_amount = models.FloatField(default=0)
    delivery_fee = models.FloatField(default=0)
    total_amount = models.FloatField(default=0)

    payment_id = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PLACED")

    created_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    rating = models.PositiveSmallIntegerField(null=True, blank=True)
    review = models.TextField(blank=True)

    @property
    def delivery_minutes(self):
        if self.delivered_at:
            delta = localtime(self.delivered_at) - localtime(self.created_at)
            return max(1, int(delta.total_seconds() // 60))
        return None

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = str(random.randint(10**10, 10**11 - 1))

        if self.status == "DELIVERED" and self.delivered_at is None:
            self.delivered_at = timezone.now()

        super().save(*args, **kwargs)



class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name="items",
        on_delete=models.CASCADE
    )
    item_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.IntegerField()
    coupon_discount = models.DecimalField(max_digits=10,decimal_places=2,default=0)


    # 🖼 Snapshot image
    item_image = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.item_name} x {self.quantity}"


class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    profile_photo = CloudinaryField("profile_image", blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return self.user.username


class UserExtraMobile(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="extra_mobiles"
    )
    mobile = models.CharField(max_length=15)

    def __str__(self):
        return self.mobile


class UserExtraAddress(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="extra_addresses"
    )
    label = models.CharField(max_length=20)
    address = models.TextField()

    def __str__(self):
        return self.label

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

rating = models.DecimalField(
    max_digits=2,
    decimal_places=1,
    null=True,
    blank=True,
    validators=[MinValueValidator(0), MaxValueValidator(5)]
)
