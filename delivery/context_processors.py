from .models import Cart, CartItem
from django.db.models import Sum
from .models import User, UserProfile

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



def user_dropdown(request):
    username = request.session.get("username")
    if not username:
        return {}

    try:
        user = User.objects.get(username=username)
        profile, _ = UserProfile.objects.get_or_create(user=user)
        return {"nav_user": user, "nav_profile": profile}
    except User.DoesNotExist:
        return {}
    

from .models import User, UserProfile, Cart, CartItem
from django.db.models import Sum

def nav_context(request):
    username = request.session.get("username")
    if not username:
        return {}

    user = User.objects.filter(username=username).first()
    if not user:
        return {}

    profile, _ = UserProfile.objects.get_or_create(user=user)
    cart = Cart.objects.filter(username=username).first()
    cart_count = 0
    if cart:
        cart_count = CartItem.objects.filter(cart=cart).aggregate(
            total=Sum("quantity")
        )["total"] or 0

    return {
        "nav_user": user,
        "nav_profile": profile,
        "cart_count": cart_count,
    }

