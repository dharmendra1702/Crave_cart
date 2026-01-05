from .models import Cart, CartItem
from django.db.models import Sum

def cart_count_processor(request):
    cart_count = 0

    username = request.session.get("username")
    if username:
        cart = Cart.objects.filter(username=username).first()
        if cart:
            cart_count = (
                CartItem.objects
                .filter(cart=cart)
                .aggregate(total=Sum("quantity"))["total"]
                or 0
            )

    return {
        "cart_count": cart_count
    }
