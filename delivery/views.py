import json
import random
import razorpay
from decimal import Decimal
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils import timezone
from .models import Cart, CartItem, Order, OrderItem, User
from .models import Restaurant
from .models import Item
from .models import Coupon
from django.db.models import Sum



# Create your views here.
def home(request):
    #Go to home page
    return render(request, "index.html")

def index(request):
    #Go to home page
    return render(request, "index.html")
    
def open_signin(request):
    #Go to sign in page
    return render(request, 'signin.html')

def open_signup(request):
    #Go to sign up page
    return render(request, 'signup.html')

def signup(request):
     #Go to sign up page and save user details
    if request.method == "POST":
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        address = request.POST.get('address')
        
        # Check username exists
        if User.objects.filter(username=username).exists():
            return render(request, "signup.html", {
                "error": "Username already exists"
            })

        # Check email exists
        if User.objects.filter(email=email).exists():
            return render(request, "signup.html", {
                "error": "Email address already exists"
            })
        
        # saving user details
        user = User(username=username, password=password, email=email, mobile=mobile, address=address)
        user.save()

        # Redirect to signin page after successful signup
        return render(request, 'signin.html')
    else:
        return HttpResponse("Invalid response.")
    

import hashlib
def signin(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = User.objects.filter(username=username, password=password).first()

        if not user:
            return render(request, "signin.html", {
                "error": "Invalid username or password"
            })

        request.session["username"] = user.username

        if user.username.lower() == "admin":
            return redirect("admin_dashboard")

        return redirect("open_customer_show_restaurants")

    return render(request, "signin.html")


def admin_dashboard(request):
    if request.session.get("username") != "admin":
        return redirect("signin")

    show_rating_alert = request.session.pop("new_rating", False)

    return render(request, "admin_dashboard.html", {
        "username": "admin",
        "show_rating_alert": show_rating_alert,
    })


def user_dashboard(request):
    username = request.session.get("username")

    if not username:
        return redirect("signin")

    return render(request, "user_dashboard.html", {
        "username": username
    })

def open_add_restaurant(request):
    return render(request, 'add_restaurant.html')

from decimal import Decimal, InvalidOperation
from django.db import IntegrityError

def add_restaurant(request):
    if request.method == "POST":
        restaurant = Restaurant(
            name=request.POST.get("name"),
            cuisine=request.POST.get("cuisine"),
            location=request.POST.get("location"),
            rating=Decimal(request.POST.get("rating", "0")),
        )

        image_url = request.POST.get("picture", "").strip()
        image_file = request.FILES.get("picture_file")

        # 🔥 Priority: FILE > URL
        if image_file:
            restaurant.picture_file = image_file
            restaurant.picture = None
        elif image_url:
            if not image_url.startswith(("http://", "https://")):
                image_url = "https://" + image_url
            restaurant.picture = image_url

        restaurant.save()
        return redirect("open_show_restaurants")

    return redirect("admin_dashboard")




def open_show_restaurants(request):
    restaurants = Restaurant.objects.all()
    return render(request, 'show_restaurants.html', {
        'restaurants': restaurants })

def open_update_restaurant(request, restaurant_id):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    return render(request, 'update_restaurant.html', {"restaurant" : restaurant})

from decimal import Decimal, InvalidOperation
from django.shortcuts import get_object_or_404, render, redirect


def update_restaurant(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    if request.method == "POST":
        restaurant.name = request.POST.get("name")
        restaurant.cuisine = request.POST.get("cuisine")
        restaurant.location = request.POST.get("location")
        restaurant.rating = Decimal(request.POST.get("rating", "0"))

        image_url = request.POST.get("picture", "").strip()
        image_file = request.FILES.get("picture_file")

        if image_file:
            restaurant.picture_file = image_file
            restaurant.picture = None
        elif image_url:
            if not image_url.startswith(("http://", "https://")):
                image_url = "https://" + image_url
            restaurant.picture = image_url
            restaurant.picture_file = None

        restaurant.save()
        return redirect("open_show_restaurants")

    return render(request, "update_restaurant.html", {"restaurant": restaurant})



def delete_restaurant(request, restaurant_id):
    if request.method == "POST":
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        restaurant.delete()
    return redirect("open_show_restaurants")


def open_update_menu(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    # ✅ SAME STYLE AS SHOW RESTAURANTS
    itemList = Item.objects.filter(restaurant_id=restaurant_id)

    return render(request, "update_menu.html", {
        "restaurant": restaurant,
        "itemList": itemList
    })



from cloudinary.uploader import upload

def update_menu(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        price = request.POST.get("price")
        vegeterian = request.POST.get("vegeterian") == "on"

        image_url = request.POST.get("picture", "").strip()
        image_file = request.FILES.get("picture_file")

        print("📦 image_file:", image_file)

        item = Item.objects.create(
            restaurant=restaurant,
            name=name,
            description=description,
            price=price,
            vegeterian=vegeterian
        )

        if image_file:
            result = upload(image_file)
            item.picture_file = result["public_id"]
            item.picture = None
        elif image_url:
            item.picture = image_url

        item.save()
        print("✅ Item saved:", item.id)

    itemList = Item.objects.filter(restaurant=restaurant)
    return render(request, "update_menu.html", {
        "restaurant": restaurant,
        "itemList": itemList
    })



def open_update_item(request, item_id, restaurant_id):
    item = get_object_or_404(Item, id=item_id, restaurant_id=restaurant_id)
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    if request.method == "POST":
        item.name = request.POST.get("name")
        item.description = request.POST.get("description")
        item.price = request.POST.get("price")
        item.vegeterian = request.POST.get("vegeterian") == "on"
        item.picture = request.POST.get("picture")
        item.save()

        return redirect("open_update_menu", restaurant_id=restaurant_id)

    return render(request, "update_item.html", {
        "item": item,
        "restaurant": restaurant
    })


def delete_item(request, item_id, restaurant_id):
    item = get_object_or_404(
        Item,
        id=item_id,
        restaurant_id=restaurant_id
    )

    item.delete()

    return redirect('open_update_menu', restaurant_id=restaurant_id)

@ensure_csrf_cookie
def view_menu(request, restaurant_id):
    username = request.session.get("username")
    if not username:
        return redirect("signin")

    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    # ✅ SAME STYLE AS SHOW RESTAURANTS (NO restaurant.items)
    itemList = Item.objects.filter(restaurant_id=restaurant_id)

    cart = Cart.objects.filter(username=username).first()

    cart_quantities = {}
    if cart:
        for ci in CartItem.objects.filter(cart=cart):
            cart_quantities[ci.item_id] = ci.quantity

    return render(request, "view_menu.html", {
        "restaurant": restaurant,
        "itemList": itemList,   # ✅ FIXED
        "cart_quantities": cart_quantities
    })





@ensure_csrf_cookie
def open_customer_show_restaurants(request):
    username = request.session.get("username")
    if not username:
        return redirect("signin")

    restaurants = Restaurant.objects.all()

    cart = Cart.objects.filter(username=username).first()
    cart_count = 0

    return render(
        request,
        "customer_show_restaurants.html",
        {
            "restaurants": restaurants,
            "cart_count": cart_count,
        }
    )




@require_POST
def add_to_cart(request, item_id):
    username = request.session.get("username")
    if not username:
        return JsonResponse({"error": "Login required"}, status=401)

    request.session.pop("applied_coupon", None)

    cart, _ = Cart.objects.get_or_create(username=username)
    item = get_object_or_404(Item, id=item_id)
    ci, created = CartItem.objects.get_or_create(cart=cart, item=item)

    if not created:
        ci.quantity += 1
    ci.save()

    return JsonResponse({"success": True})



@require_POST
def decrease_cart_item(request, item_id):
    username = request.session.get("username")
    if not username:
        return redirect("signin")
    request.session.pop("applied_coupon", None)

    cart = Cart.objects.get(username=username)
    ci = CartItem.objects.get(cart=cart, item_id=item_id)

    ci.quantity -= 1
    if ci.quantity <= 0:
        ci.delete()
    else:
        ci.save()

    return JsonResponse({"success": True})


def view_cart(request):
    username = request.session.get("username")
    if not username:
        return redirect("signin")

    cart = Cart.objects.filter(username=username).first()

    cart_items = []
    cart_count = 0
    product_total = Decimal("0.00")

    if cart:
        for ci in CartItem.objects.filter(cart=cart):
            subtotal = ci.item.price * ci.quantity
            product_total += subtotal
            cart_count += ci.quantity
            cart_items.append({
                "item": ci.item,
                "quantity": ci.quantity,
                "subtotal": subtotal
            })

        totals = calculate_cart_totals(request, cart)
    else:
        totals = {
            "product_total": Decimal("0.00"),
            "delivery_fee": Decimal("0.00"),
            "coupon_discount": Decimal("0.00"),
            "gst": Decimal("0.00"),
            "grand_total": Decimal("0.00"),
        }

    return render(request, "cart.html", {
        "cart_items": cart_items,
        "cart_count": cart_count,
        **totals
    })



@require_POST
def remove_cart_item(request, item_id):
    username = request.session.get("username")
    if not username:
        return JsonResponse({"error": "Login required"}, status=401)

    cart = get_object_or_404(Cart, username=username)
    cart_item = get_object_or_404(CartItem, cart=cart, item_id=item_id)

    cart_item.delete()

    return JsonResponse({"removed": True})

@require_POST
def apply_coupon(request):
    code = request.POST.get("code", "").strip()
    username = request.session.get("username")

    if not username:
        return JsonResponse({"error": "Login required"}, status=401)

    cart = Cart.objects.filter(username=username).first()
    if not cart:
        return JsonResponse({"error": "Cart is empty"})

    totals = calculate_cart_totals(request, cart)

    try:
        coupon = Coupon.objects.get(code__iexact=code, is_active=True)
    except Coupon.DoesNotExist:
        return JsonResponse({"error": "Invalid or expired coupon ❌"})

    # 🚫 CHECK USAGE LIMIT
    if coupon.used_count >= coupon.usage_limit:
        return JsonResponse({"error": "Coupon usage limit reached ❌"})

    min_order = Decimal(str(coupon.min_order_amount))
    if totals["product_total"] < min_order:
        return JsonResponse({
            "error": f"Minimum order ₹{min_order} required"
        })

    # Calculate discount
    if coupon.discount_type == "percent":
        discount = (totals["product_total"] * Decimal(coupon.discount_value)) / 100
    else:
        discount = Decimal(coupon.discount_value)

    print("🔥 APPLY COUPON HIT 🔥")

    request.session["applied_coupon"] = {
        "code": coupon.code,
        "discount": float(round(discount, 2)),
        "min_order": float(min_order),
    }

    return JsonResponse({"success": True})



@require_POST
def remove_coupon(request):
    request.session.pop("applied_coupon", None)
    return JsonResponse({"success": True})

from django.db import IntegrityError


COUPON_CHARS = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"

def generate_unique_coupon():
    while True:
        code = "CRAVE" + "".join(random.choices(COUPON_CHARS, k=6))
        if not Coupon.objects.filter(code=code).exists():
            return code

def create_coupon(request):
    if request.session.get("username") != "admin":
        return redirect("signin")

    message = None

    if request.method == "POST":
        discount_type = request.POST.get("discount_type")
        discount_value = request.POST.get("discount_value")
        min_order_amount = request.POST.get("min_order_amount", 0)
        is_active = "is_active" in request.POST
        usage_limit = int(request.POST.get("usage_limit", 1))

        # 🔹 BULK CREATE
        if request.POST.get("bulk"):
            for _ in range(50):
                Coupon.objects.create(
                    code=generate_unique_coupon(),
                    discount_type=discount_type,
                    discount_value=discount_value,
                    min_order_amount=min_order_amount,
                    usage_limit=usage_limit,
                    used_count=0,
                    is_active=is_active
                )
            message = "✅ 50 coupons generated successfully!"

        # 🔹 SINGLE CREATE
        elif request.POST.get("single"):
            code = request.POST.get("code", "").strip().upper()
            if not code:
                code = generate_unique_coupon()

            if Coupon.objects.filter(code=code).exists():
                message = "❌ Coupon already exists"
            else:
                Coupon.objects.create(
                    code=code,
                    discount_type=discount_type,
                    discount_value=discount_value,
                    min_order_amount=min_order_amount,
                    usage_limit=usage_limit,
                    used_count=0,
                    is_active=is_active
                )
                message = "✅ Coupon created successfully!"

    coupons = Coupon.objects.all().order_by("-id")
    return render(request, "coupon.html", {
        "coupons": coupons,
        "message": message
    })


def toggle_coupon(request, cid):
    coupon = get_object_or_404(Coupon, id=cid)
    coupon.is_active = not coupon.is_active
    coupon.save()
    return redirect("create_coupon")

import razorpay
from django.conf import settings

def checkout(request):
    username = request.session.get("username")
    if not username:
        return redirect("signin")

    if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
        return HttpResponse("Razorpay keys not configured", status=500)

    user = User.objects.get(username=username)
    cart = Cart.objects.get(username=username)

    totals = calculate_cart_totals(request, cart)

    client = razorpay.Client(auth=(
        settings.RAZORPAY_KEY_ID,
        settings.RAZORPAY_KEY_SECRET
    ))

    razorpay_order = client.order.create({
        "amount": int(totals["grand_total"] * 100),
        "currency": "INR",
        "payment_capture": 1
    })

    request.session["razorpay_order_id"] = razorpay_order["id"]

    return render(request, "checkout.html", {
        "customer": user,
        "cart_items": CartItem.objects.filter(cart=cart),
        **totals,
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        "order_id": razorpay_order["id"],
    })

    cart = Cart.objects.filter(username=username).first()
    if not cart:
        return redirect("view_cart")



@require_POST
def payment_success(request):
    username = request.session.get("username")
    if not username:
        return redirect("signin")

    user = User.objects.get(username=username)
    cart = Cart.objects.get(username=username)

    data = json.loads(request.body)

    if data.get("razorpay_order_id") != request.session.get("razorpay_order_id"):
        return JsonResponse({"error": "Order mismatch"}, status=400)

    totals = calculate_cart_totals(request, cart)

    applied_coupon = request.session.get("applied_coupon")

    discount_amount = Decimal("0.00")
    coupon_code = None

    if applied_coupon:
        coupon_code = applied_coupon["code"]
        discount_amount = Decimal(str(applied_coupon["discount"]))


    order = Order.objects.create(
    user=user,
    subtotal=totals["product_total"],
    gst_amount=totals["gst"],
    delivery_fee=totals["delivery_fee"],
    coupon_code=coupon_code,                # ✅ STRING ONLY
    coupon_discount=discount_amount,        # ✅ DECIMAL
    total_amount=totals["grand_total"],
    payment_id=data.get("razorpay_payment_id")
)
    # ✅ INCREMENT COUPON USAGE
    if coupon_code:
        coupon = Coupon.objects.get(code=coupon_code)
        coupon.used_count += 1

        if coupon.used_count >= coupon.usage_limit:
            coupon.is_active = False

        coupon.save()


    coupon_data = request.session.get("applied_coupon")
    coupon_discount = Decimal("0.00")

    if coupon_data:
        coupon_discount = Decimal(str(coupon_data["discount"]))

    for ci in CartItem.objects.filter(cart=cart):

        item = ci.item   # ✅ CORRECT

        image_url = None

        # Priority: Cloudinary > URL
        if item.picture_file:
            image_url = item.picture_file.url
        elif item.picture:
            image_url = item.picture

        OrderItem.objects.create(
            order=order,
            item_name=item.name,
            price=item.price,
            quantity=ci.quantity,
            item_image=image_url   # ✅ FIXED
        )

    CartItem.objects.filter(cart=cart).delete()
    cart.delete()

    request.session.pop("applied_coupon", None)
    request.session.pop("checkout_data", None)
    request.session.pop("razorpay_order_id", None)

    return JsonResponse({"success": True})

    cart = Cart.objects.filter(username=username).first()
    if not cart:
        return redirect("view_cart")
    
    request.session.pop("applied_coupon", None)
    request.session.pop("razorpay_order_id", None)





def order_success(request):
    request.session.pop("checkout_data", None)
    request.session.pop("applied_coupon", None)
    Cart.objects.filter(username=request.session.get("username")).delete()
    return render(request, "order_success.html")

# def order_history(request):
#     user = User.objects.get(username=request.session["username"])
#     orders = Order.objects.filter(user=user).order_by("-created_at")
#     return render(request, "order_history.html", {"orders": orders})


from .models import CartItem

FREE_DELIVERY_LIMIT = Decimal("99")
DELIVERY_CHARGE = Decimal("40")
GST_RATE = Decimal("0.05")



def calculate_cart_totals(request, cart):
    product_total = Decimal("0.00")

    for ci in CartItem.objects.filter(cart=cart):
        product_total += ci.item.price * ci.quantity

    # Delivery fee
    delivery_fee = (
        Decimal("0.00")
        if product_total >= FREE_DELIVERY_LIMIT
        else DELIVERY_CHARGE
    )

    # Coupon
    coupon_data = request.session.get("applied_coupon")
    coupon_discount = Decimal("0.00")

    if coupon_data:
        if product_total < Decimal(str(coupon_data["min_order"])):
            request.session.pop("applied_coupon", None)
        else:
            coupon_discount = Decimal(str(coupon_data["discount"]))

    taxable = max(product_total - coupon_discount, Decimal("0.00"))
    gst = (taxable * GST_RATE).quantize(Decimal("0.01"))
    grand_total = (taxable + gst + delivery_fee).quantize(Decimal("0.01"))

    return {
        "product_total": product_total,
        "delivery_fee": delivery_fee,
        "coupon_discount": coupon_discount,
        "gst": gst,
        "grand_total": grand_total,
    }


@require_POST
def cancel_order(request, order_id):
    order = Order.objects.get(id=order_id, user__username=request.session["username"])
    if order.status == "PLACED":
        order.status = "CANCELLED"
        order.save()
    return redirect("order_history")


def logout(request):
    request.session.flush()
    return redirect("signin")


def serialize_decimals(data: dict):
    """
    Convert Decimal values to float for session storage
    """
    return {
        k: float(v) if isinstance(v, Decimal) else v
        for k, v in data.items()
    }


from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from django.http import HttpResponse

def download_invoice(request, order_id):
    order = Order.objects.get(id=order_id, user__username=request.session["username"])

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="invoice_{order.id}.pdf"'

    doc = SimpleDocTemplate(response)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(f"<b>Crave Cart Invoice</b>", styles["Title"]))
    elements.append(Paragraph(f"Order ID: {order.id}", styles["Normal"]))
    elements.append(Paragraph(f"Total: ₹{order.total_amount}", styles["Normal"]))

    for item in order.items.all():
        elements.append(
            Paragraph(f"{item.item_name} × {item.quantity} – ₹{item.price}", styles["Normal"])
        )

    doc.build(elements)
    return response


@require_POST
def rate_order(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        user__username=request.session["username"]
    )

    if order.status != "DELIVERED":
        return redirect("order_history")

    order.rating = int(request.POST.get("rating"))
    order.review = request.POST.get("review", "")
    order.save()

    # 🔔 ADMIN NOTIFICATION FLAG
    request.session["new_rating"] = True

    return redirect("order_history")




def reorder(request, order_id):
    order = Order.objects.get(id=order_id, user__username=request.session["username"])
    cart, _ = Cart.objects.get_or_create(username=request.session["username"])

    CartItem.objects.filter(cart=cart).delete()

    for item in order.items.all():
        menu_item = Item.objects.filter(name=item.item_name).first()
        if menu_item:
            CartItem.objects.create(
                cart=cart,
                item=menu_item,
                quantity=item.quantity
            )

    return redirect("view_cart")


from django.http import JsonResponse
from .models import Order

def order_status_api(request, order_id):
    order = Order.objects.get(id=order_id)
    return JsonResponse({
        "status": order.status,
        "status_display": order.get_status_display()
    })

def admin_orders(request):
    # 🔒 Admin check
    if request.session.get("username") != "admin":
        return redirect("signin")

    orders = Order.objects.all().order_by("-created_at")

    return render(request, "admin_orders.html", {
        "orders": orders
    })


def admin_order_detail(request, order_id):
    if request.session.get("username") != "admin":
        return redirect("signin")

    order = get_object_or_404(Order, id=order_id)

    return render(request, "admin_order_detail.html", {
        "order": order
    })


@require_POST
def admin_update_order_status(request, order_id):
    # 🔐 Admin check
    if request.session.get("username") != "admin":
        return redirect("signin")

    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()

    return redirect("admin_order_detail", order_id=order.id)

@require_POST
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        new_status = request.POST.get("status")
        order.status = new_status

        # ✅ SET DELIVERY TIME ONLY ONCE
        if new_status == "DELIVERED" and order.delivered_at is None:
            order.delivered_at = timezone.now()

        order.save()
        return redirect("admin_order_detail", order_id=order.id)



from django.db.models import Avg, Count

def admin_ratings_dashboard(request):
    if request.session.get("username") != "admin":
        return redirect("signin")

    data = (
        Order.objects
        .filter(status="DELIVERED", rating__isnull=False)
        .values("items__item_name")
        .annotate(
            avg_rating=Avg("rating"),
            total_reviews=Count("rating")
        )
    )

    return render(request, "admin_ratings.html", {
        "data": data
    })

def order_history(request):
    user = User.objects.get(username=request.session["username"])

    orders = Order.objects.filter(user=user).order_by("-created_at")

    return render(request, "order_history.html", {
        "orders": orders
    })
