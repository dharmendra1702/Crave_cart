from django.db import models


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
    picture = models.URLField()
    cuisine = models.CharField(max_length=100)
    rating = models.DecimalField(max_digits=2, decimal_places=1)
    location = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Item(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="items"
    )
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=200)
    price = models.FloatField()
    vegeterian = models.BooleanField(default=False)
    picture = models.URLField()

    def __str__(self):
        return self.name


class Cart(models.Model):
    username = models.CharField(max_length=150)

    def __str__(self):
        return f"Cart ({self.username})"



class CartItem(models.Model):
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE,related_name="items")
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.item.name} x {self.quantity}"

class Coupon(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount_type = models.CharField(
        max_length=10,
        choices=[("percent", "Percent"), ("flat", "Flat")]
    )
    discount_value = models.PositiveIntegerField()
    min_order_amount = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    # 🔒 NEW
    used_by = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.code

class Order(models.Model):
    STATUS_CHOICES = (
        ("PLACED", "Placed"),
        ("CANCELLED", "Cancelled"),
        ("DELIVERED", "Delivered"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_amount = models.FloatField()
    payment_id = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PLACED")
    created_at = models.DateTimeField(auto_now_add=True)



class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    item_name = models.CharField(max_length=200)
    price = models.FloatField()
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.item_name} x {self.quantity}"
    
