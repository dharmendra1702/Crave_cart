import json
import random
import razorpay
from decimal import Decimal
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils import timezone
from .models import Cart, CartItem, Order, OrderItem, User, UserExtraAddress, UserExtraMobile, UserProfile
from .models import Restaurant
from .models import Item
from .models import Coupon
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.shortcuts import render




# Create your views here.
def home(request):
    #Go to home page
    return render(request, "index.html")

def index(request):
    #Go to home page
    return render(request, "index.html")
    
def about(request):
    return render(request, "about.html")   

def resume_page(request):
    return render(request, "resume.html")

def open_signin(request):
    #Go to sign in page
    return render(request, 'signin.html')

def open_signup(request):
    #Go to sign up page
    return render(request, 'signup.html')

def signup(request):
    if request.method == "POST":
        username   = (request.POST.get('username') or "").strip()
        first_name = (request.POST.get('first_name') or "").strip()
        last_name  = (request.POST.get('last_name') or "").strip()
        password   = (request.POST.get('password') or "").strip()
        email      = (request.POST.get('email') or "").strip()
        mobile     = (request.POST.get('mobile') or "").strip()
        address    = (request.POST.get('address') or "").strip()

        # Basic validation
        if not all([username, first_name, last_name, password, email, mobile, address]):
            return render(request, "signup.html", {"error": "All fields are required"})

        # Check username exists
        if User.objects.filter(username=username).exists():
            return render(request, "signup.html", {"error": "Username already exists"})

        # Check email exists
        if User.objects.filter(email=email).exists():
            return render(request, "signup.html", {"error": "Email address already exists"})

        # ✅ saving user details properly
        user = User(
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
            email=email,
            mobile=mobile,
            address=address
        )
        user.save()

        # ✅ Redirect properly
        return redirect("open_signin")

    return render(request, "signup.html")

    

import hashlib
def signin(request):
    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        password = (request.POST.get("password") or "").strip()

        user = User.objects.filter(username=username, password=password).first()

        if not user:
            return render(request, "signin.html", {"error": "Invalid username or password"})

        request.session["username"] = user.username
        request.session.modified = True

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

from django.conf import settings
from decimal import Decimal
import razorpay

def checkout(request):
    username = request.session.get("username")
    if not username:
        return redirect("signin")

    if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
        return HttpResponse("Razorpay keys not configured", status=500)

    user = User.objects.get(username=username)

    cart = Cart.objects.filter(username=username).first()
    if not cart:
        return redirect("view_cart")

    totals = calculate_cart_totals(request, cart)

    # ✅ addresses from profile model
    addresses = UserExtraAddress.objects.filter(user=user).order_by("-is_default", "-id")
    default_addr = addresses.filter(is_default=True).first()
    default_address_id = default_addr.id if default_addr else None

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    razorpay_order = client.order.create({
        "amount": int(Decimal(str(totals["grand_total"])) * 100),
        "currency": "INR",
        "payment_capture": 1
    })

    request.session["razorpay_order_id"] = razorpay_order["id"]

    return render(request, "checkout.html", {
        "customer": user,
        "cart_items": CartItem.objects.filter(cart=cart),
        "addresses": addresses,                 # ✅ added
        "default_address_id": default_address_id,  # ✅ added
        **totals,
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        "order_id": razorpay_order["id"],
    })



import threading, traceback
from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.http import require_POST

@require_POST
def payment_success(request):
    username = request.session.get("username")
    if not username:
        return JsonResponse({"error": "Login required"}, status=401)

    user = User.objects.get(username=username)
    cart = Cart.objects.get(username=username)
    data = json.loads(request.body or "{}")

    if data.get("razorpay_order_id") != request.session.get("razorpay_order_id"):
        return JsonResponse({"error": "Order mismatch"}, status=400)

    totals = calculate_cart_totals(request, cart)

    address_id = request.session.get("selected_address_id")
    addr = UserExtraAddress.objects.filter(id=address_id, user=user).first() if address_id else None

    applied_coupon = request.session.get("applied_coupon")
    discount_amount = Decimal("0.00")
    coupon_code = None
    if applied_coupon:
        coupon_code = applied_coupon["code"]
        discount_amount = Decimal(str(applied_coupon["discount"]))

    order = Order.objects.create(
        user=user,
        subtotal=float(totals["product_total"]),
        gst_amount=float(totals["gst"]),
        delivery_fee=float(totals["delivery_fee"]),
        coupon_code=coupon_code,
        coupon_discount=float(discount_amount),
        total_amount=float(totals["grand_total"]),

        payment_id=data.get("razorpay_payment_id"),
        payment_method="ONLINE",
        payment_status="PAID",

        delivery_address_label=(addr.label if addr else None),
        delivery_address=(addr.address if addr else None),

        status="PLACED",
    )

    # coupon usage
    if coupon_code:
        coupon = Coupon.objects.get(code=coupon_code)
        coupon.used_count += 1
        if coupon.used_count >= coupon.usage_limit:
            coupon.is_active = False
        coupon.save()

    # order items
    for ci in CartItem.objects.filter(cart=cart):
        item = ci.item
        image_url = None
        try:
            if item.picture_file:
                image_url = item.picture_file.url
        except Exception:
            image_url = None
        if not image_url and item.picture:
            image_url = item.picture

        OrderItem.objects.create(
            order=order,
            item_name=item.name,
            price=item.price,
            quantity=ci.quantity,
            item_image=image_url
        )

    # clear cart + session
    CartItem.objects.filter(cart=cart).delete()
    cart.delete()

    request.session.pop("applied_coupon", None)
    request.session.pop("checkout_data", None)
    request.session.pop("razorpay_order_id", None)
    request.session.pop("selected_address_id", None)
    request.session.pop("pay_method", None)

    # ✅ placed emails (USER + ADMIN)
    def _send():
        try:
            send_order_emails(order, request=request)
        except Exception:
            logger.error("Placed email failed:\n%s", traceback.format_exc())

    threading.Thread(target=_send, daemon=True).start()

    return JsonResponse({"success": True})


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

NOTIFY_USER_STATUSES = {"PREPARING", "OUT_FOR_DELIVERY", "DELIVERED", "CANCELLED"}

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


def cancel_order(request, order_id):
    order = Order.objects.get(id=order_id, user__username=request.session["username"])

    if order.status == "PLACED":
        order.status = "CANCELLED"
        order.save()

        # ✅ status mail USER ONLY
        threading.Thread(
            target=send_order_status_email,
            args=(order, "CANCELLED", request),
            daemon=True
        ).start()

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


# views.py
from decimal import Decimal, ROUND_HALF_UP
from django.shortcuts import redirect, get_object_or_404

def rate_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        raw = request.POST.get("rating", "0")

        # force 1-decimal precision without losing value
        rating = Decimal(raw).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)

        # clamp to 0..5
        if rating < 0: rating = Decimal("0.0")
        if rating > 5: rating = Decimal("5.0")

        order.rating = rating
        order.review = request.POST.get("review", "").strip()
        order.save(update_fields=["rating", "review"])

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
    if request.session.get("username") != "admin":
        return redirect("signin")

    order = get_object_or_404(Order, id=order_id)
    old_status = order.status
    new_status = request.POST.get("status")

    if new_status in dict(Order.STATUS_CHOICES) and new_status != old_status:
        order.status = new_status

        if new_status == "DELIVERED" and order.delivered_at is None:
            order.delivered_at = timezone.now()

        if new_status == "DELIVERED" and order.payment_method == "COD":
            order.payment_status = "PAID"

        order.save()

        # ✅ status mail USER ONLY for these statuses
        if new_status in NOTIFY_USER_STATUSES:
            threading.Thread(
                target=send_order_status_email,
                args=(order, new_status, request),
                daemon=True
            ).start()

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
        
        if new_status == "DELIVERED" and order.payment_method == "COD":
            order.payment_status = "PAID"


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

from django.db.models import Sum

def order_history(request):
    username = request.session.get("username")
    if not username:
        return redirect("signin")

    user = User.objects.get(username=username)
    nav_profile, _ = UserProfile.objects.get_or_create(user=user)

    # cart count for header badge
    cart = Cart.objects.filter(username=username).first()
    cart_count = 0
    if cart:
        cart_count = CartItem.objects.filter(cart=cart).aggregate(
            total=Sum("quantity")
        )["total"] or 0

    orders = Order.objects.filter(user=user).order_by("-created_at")

    return render(request, "order_history.html", {
        "orders": orders,
        "nav_user": user,
        "nav_profile": nav_profile,
        "cart_count": cart_count,
    })

from decimal import Decimal
from django.shortcuts import redirect

from decimal import Decimal
from django.shortcuts import redirect
import threading
import traceback
import logging

logger = logging.getLogger(__name__)

def place_cod_order(request):
    username = request.session.get("username")
    if not username:
        return redirect("signin")

    user = User.objects.get(username=username)
    cart = Cart.objects.filter(username=username).first()
    if not cart:
        return redirect("view_cart")

    address_id = request.session.get("selected_address_id")
    if not address_id:
        return redirect("checkout")

    addr = UserExtraAddress.objects.filter(id=address_id, user=user).first()
    if not addr:
        return redirect("checkout")

    totals = calculate_cart_totals(request, cart)

    applied_coupon = request.session.get("applied_coupon")
    discount_amount = Decimal("0.00")
    coupon_code = None
    if applied_coupon:
        coupon_code = applied_coupon["code"]
        discount_amount = Decimal(str(applied_coupon["discount"]))

    order = Order.objects.create(
        user=user,
        subtotal=float(totals["product_total"]),
        gst_amount=float(totals["gst"]),
        delivery_fee=float(totals["delivery_fee"]),
        coupon_code=coupon_code,
        coupon_discount=float(discount_amount),
        total_amount=float(totals["grand_total"]),

        payment_id="COD",
        payment_method="COD",
        payment_status="PENDING",

        delivery_address_label=addr.label,
        delivery_address=addr.address,

        status="PLACED",
    )

    for ci in CartItem.objects.filter(cart=cart):
        item = ci.item
        image_url = None
        try:
            if item.picture_file:
                image_url = item.picture_file.url
        except Exception:
            image_url = None
        if not image_url and item.picture:
            image_url = item.picture

        OrderItem.objects.create(
            order=order,
            item_name=item.name,
            price=item.price,
            quantity=ci.quantity,
            item_image=image_url
        )

    if coupon_code:
        coupon = Coupon.objects.get(code=coupon_code)
        coupon.used_count += 1
        if coupon.used_count >= coupon.usage_limit:
            coupon.is_active = False
        coupon.save()

    CartItem.objects.filter(cart=cart).delete()
    cart.delete()

    request.session.pop("applied_coupon", None)
    request.session.pop("razorpay_order_id", None)
    request.session.pop("selected_address_id", None)
    request.session.pop("pay_method", None)

    # ✅ placed emails (USER + ADMIN)
    def _send():
        try:
            send_order_emails(order, request=request)
        except Exception:
            logger.error("COD placed email failed:\n%s", traceback.format_exc())

    threading.Thread(target=_send, daemon=True).start()

    return redirect("order_history")



def profile_view(request):
    username = request.session.get("username")
    if not username:
        return redirect("signin")

    user = User.objects.get(username=username)
    profile, created = UserProfile.objects.get_or_create(user=user)

    extra_mobiles = user.extra_mobiles.all().order_by("-is_primary", "-id")
    extra_addresses = user.extra_addresses.all().order_by("-is_default", "-id")

    # ✅ pick primary from extra mobiles, else fallback to user.mobile
    primary_extra = extra_mobiles.filter(is_primary=True).first()
    primary_mobile = primary_extra.mobile if primary_extra else user.mobile

    return render(request, "profile.html", {
        "user": user,
        "profile": profile,
        "extra_mobiles": extra_mobiles,
        "extra_addresses": extra_addresses,
        "primary_mobile": primary_mobile,   # ✅ send to template
    })



from django.views.decorators.http import require_POST
from django.shortcuts import redirect
from .models import User, UserProfile

@require_POST
def update_profile(request):
    user = User.objects.get(username=request.session["username"])
    profile, _ = UserProfile.objects.get_or_create(user=user)

    # basic fields
    user.first_name = request.POST.get("first_name", "").strip()
    user.last_name  = request.POST.get("last_name", "").strip()

    profile.gender = request.POST.get("gender", "").strip()
    profile.date_of_birth = request.POST.get("date_of_birth") or None

    # username (optional)
    new_username = request.POST.get("username", "").strip()
    if new_username and new_username != user.username:
        if User.objects.filter(username=new_username).exclude(id=user.id).exists():
            return redirect("profile")
        user.username = new_username
        request.session["username"] = new_username

    # ✅ email (optional)
    new_email = request.POST.get("email", "").strip()
    if new_email and new_email != user.email:
        if User.objects.filter(email=new_email).exclude(id=user.id).exists():
            return redirect("profile")
        user.email = new_email

    user.save()
    profile.save()
    return redirect("profile")

import re

MOBILE_10_RE = re.compile(r"^[6-9]\d{9}$")

@require_POST
def add_extra_mobile(request):
    user = User.objects.get(username=request.session["username"])
    mobile = (request.POST.get("mobile") or "").strip()

    if not MOBILE_10_RE.match(mobile):
        return JsonResponse({"error": "Invalid mobile. Enter 10 digits (starts with 6-9)."}, status=400)

    # prevent duplicates
    if UserExtraMobile.objects.filter(user=user, mobile=mobile).exists():
        return JsonResponse({"error": "This mobile number already exists"}, status=400)

    make_primary = not UserExtraMobile.objects.filter(user=user, is_primary=True).exists()

    m = UserExtraMobile.objects.create(
        user=user,
        mobile=mobile,
        is_primary=make_primary
    )
    return JsonResponse({"id": m.id, "mobile": m.mobile, "is_primary": m.is_primary})



# @require_POST
# def delete_extra_mobile(request, mid):
#     UserExtraMobile.objects.filter(id=mid).delete()
#     return JsonResponse({"success": True})

@require_POST
def add_extra_address(request):
    user = User.objects.get(username=request.session["username"])

    addr = UserExtraAddress.objects.create(
        user=user,
        label=request.POST.get("label"),
        address=request.POST.get("address")
    )

    return JsonResponse({
        "id": addr.id,
        "label": addr.label,
        "address": addr.address
    })


@require_POST
def delete_extra_address(request, aid):
    UserExtraAddress.objects.filter(id=aid).delete()
    return JsonResponse({"success": True})

@require_POST
def update_profile_photo(request):
    user = User.objects.get(username=request.session["username"])
    profile, _ = UserProfile.objects.get_or_create(user=user)

    if request.FILES.get("profile_photo"):
        profile.profile_photo = request.FILES["profile_photo"]
        profile.save()

    return redirect("profile")


@require_POST
def verify_email_password(request):
    user = User.objects.get(username=request.session["username"])
    password = request.POST.get("password")

    if user.password != password:
        return JsonResponse({"success": False, "message": "Incorrect password"})

    request.session["email_pwd_verified"] = True
    return JsonResponse({"success": True})


@require_POST
def update_email(request):
    if not request.session.get("email_pwd_verified"):
        return redirect("profile")

    user = User.objects.get(username=request.session["username"])
    new_email = request.POST.get("new_email")

    if User.objects.filter(email=new_email).exists():
        return redirect("profile")

    user.email = new_email
    user.save()

    request.session.pop("email_pwd_verified")
    return redirect("profile")


@require_POST
def verify_username_password(request):
    user = User.objects.get(username=request.session["username"])
    password = request.POST.get("password")

    if user.password != password:
        return JsonResponse({"success": False, "message": "Incorrect password"})

    request.session["username_pwd_verified"] = True
    return JsonResponse({"success": True})

@require_POST
def update_username(request):
    if not request.session.get("username_pwd_verified"):
        return redirect("profile")

    user = User.objects.get(username=request.session["username"])
    new_username = request.POST.get("new_username")

    if User.objects.filter(username=new_username).exists():
        return render(request, "profile.html", {
            "user": user,
            "profile": user.profile,
            "extra_mobiles": user.extra_mobiles.all(),
            "extra_addresses": user.extra_addresses.all(),
            "username_error": "Username already taken"
        })

    user.username = new_username
    user.save()

    # IMPORTANT: update session username
    request.session["username"] = new_username
    request.session.pop("username_pwd_verified")

    return redirect("profile")

# ✅ ADD / KEEP THESE IMPORTS (only once in your file)
import os
import logging
from decimal import Decimal
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone

logger = logging.getLogger(__name__)

# ✅ ADD THIS HELPER (once) – forces public URL for email assets (logo)
def _public_site_root(request=None) -> str:
    """
    Always return a public https site root for email assets.
    Priority:
      1) settings.SITE_URL (set in .env / Render env)
      2) request.build_absolute_uri("/") (only if request exists)
      3) fallback Render URL
    """
    site_url = (getattr(settings, "SITE_URL", "") or "").strip()

    if not site_url and request:
        # request could be local (127.0.0.1) - avoid that in emails
        try:
            built = (request.build_absolute_uri("/") or "").strip()
            # use only if it's not localhost/127
            if built and ("127.0.0.1" not in built) and ("localhost" not in built):
                site_url = built
        except Exception:
            pass

    if not site_url:
        site_url = "https://crave-cart-82wd.onrender.com/"

    return site_url.rstrip("/")


# ✅ REPLACE YOUR send_order_emails WITH THIS FULL FUNCTION
def send_order_emails(order, request=None):
    # items
    items_manager = getattr(order, "items", None)
    items_qs = items_manager.all() if items_manager else order.orderitem_set.all()

    items = []
    for i in items_qs:
        line_total = (Decimal(str(i.price)) * int(i.quantity))
        items.append({
            "name": i.item_name,
            "qty": i.quantity,
            "price": i.price,
            "line_total": line_total
        })

    site_root = _public_site_root(request)
    site_url = f"{site_root}/"
    admin_url = f"{site_root}/admin/"

    context = {
        "order_id": order.id,
        "payment_id": order.payment_id,
        "order_date": timezone.localtime(order.created_at).strftime("%d %b %Y, %I:%M %p"),
        "items": items,
        "subtotal": order.subtotal,
        "gst": order.gst_amount,
        "delivery_fee": order.delivery_fee,
        "coupon_code": order.coupon_code or "N/A",
        "discount": order.coupon_discount,
        "total": order.total_amount,
        "year": timezone.now().year,
        "site_url": site_url,
        "admin_url": admin_url,
        "user_name": order.user.username,
        "user_email": order.user.email,
        # ✅ absolute logo URL for email clients
        "logo_url": f"{site_root}/static/images/logoo.png",
    }

    # USER mail
    if order.user.email:
        subject = f"Your Order #{order.id} is Placed ✅"
        text_body = render_to_string("emails/user_order.txt", context)
        html_body = render_to_string("emails/user_order.html", context)

        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.user.email],
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send(fail_silently=False)

    # ADMIN mail
    admin_to = getattr(settings, "ADMIN_ORDER_EMAIL", None)
    if admin_to:
        subject = f"New Order Received: #{order.id} 🚀"
        text_body = render_to_string("emails/admin_order.txt", context)
        html_body = render_to_string("emails/admin_order.html", context)

        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[admin_to],
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send(fail_silently=False)


# ✅ REPLACE YOUR send_order_status_email WITH THIS FULL FUNCTION
def send_order_status_email(order, new_status, request=None):
    # only send for required statuses (extra safety)
    if new_status not in NOTIFY_USER_STATUSES:
        return

    status_label = dict(order.STATUS_CHOICES).get(new_status, new_status)

    site_root = _public_site_root(request)
    site_url = f"{site_root}/"

    context = {
        "order_id": order.id,
        "status": new_status,
        "status_label": status_label,
        "updated_at": timezone.localtime(timezone.now()).strftime("%d %b %Y, %I:%M %p"),
        "user_name": order.user.username,
        "year": timezone.now().year,
        "site_url": site_url,
        # ✅ absolute logo URL for email clients
        "logo_url": f"{site_root}/static/images/logoo.png",
    }

    subject_map = {
        "PREPARING": f"Order #{order.id} is Being Prepared 🍳",
        "OUT_FOR_DELIVERY": f"Order #{order.id} is Out for Delivery 🛵",
        "DELIVERED": f"Order #{order.id} Delivered ✅",
        "CANCELLED": f"Order #{order.id} Cancelled ❌",
    }
    subject = subject_map.get(new_status, f"Order #{order.id} Update: {status_label}")

    text_body = render_to_string("emails/order_status.txt", context)
    html_body = render_to_string("emails/order_status.html", context)

    if order.user.email:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.user.email],
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send(fail_silently=False)


# ✅ KEEP YOUR contact_submit AS-IS (NO CHANGE NEEDED FOR LOGO)
# but ensure EMAIL works via Brevo backend and settings.ADMIN_ORDER_EMAIL exists


@require_POST
def delete_extra_mobile(request, mid):
    user = User.objects.get(username=request.session["username"])
    UserExtraMobile.objects.filter(id=mid, user=user).delete()
    return JsonResponse({"success": True})

@require_POST
def delete_extra_address(request, aid):
    user = User.objects.get(username=request.session["username"])
    UserExtraAddress.objects.filter(id=aid, user=user).delete()
    return JsonResponse({"success": True})


from django.db import transaction

@require_POST
def make_primary_mobile(request, mid):
    user = User.objects.get(username=request.session["username"])

    with transaction.atomic():
        # set all false first
        UserExtraMobile.objects.filter(user=user).update(is_primary=False)
        # set selected true
        UserExtraMobile.objects.filter(user=user, id=mid).update(is_primary=True)

    return JsonResponse({"success": True})


@require_POST
def make_default_address(request, aid):
    user = User.objects.get(username=request.session["username"])

    with transaction.atomic():
        UserExtraAddress.objects.filter(user=user).update(is_default=False)
        UserExtraAddress.objects.filter(user=user, id=aid).update(is_default=True)

    return JsonResponse({"success": True})


import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

@require_POST
def add_address_ajax(request):
    data = json.loads(request.body or "{}")
    # validate minimally
    required = ["name","mobile","house_no","area","city","state","pincode"]
    if not all(data.get(k) for k in required):
        return JsonResponse({"ok": False, "error": "All address fields are required"})

    # create address model (change model/fields as per your project)
    addr = UserExtraAddress.objects.create(
        user=request.user,   # or your session user mapping
        name=data["name"],
        mobile=data["mobile"],
        house_no=data["house_no"],
        area=data["area"],
        city=data["city"],
        state=data["state"],
        pincode=data["pincode"],
    )
    return JsonResponse({"ok": True, "id": addr.id})

@require_POST
def set_checkout_selection(request):
    username = request.session.get("username")
    if not username:
        return JsonResponse({"ok": False, "error": "Login required"}, status=401)

    user = User.objects.get(username=username)
    data = json.loads(request.body or "{}")

    address_id = data.get("address_id")
    pay_method = data.get("pay_method")

    if pay_method not in ["ONLINE", "COD"]:
        return JsonResponse({"ok": False, "error": "Invalid payment method"})

    if not UserExtraAddress.objects.filter(id=address_id, user=user).exists():
        return JsonResponse({"ok": False, "error": "Invalid address"})

    request.session["selected_address_id"] = int(address_id)
    request.session["pay_method"] = pay_method
    return JsonResponse({"ok": True})


from django.core.mail import EmailMessage
from django.conf import settings
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
import logging

logger = logging.getLogger(__name__)

@require_POST
def contact_submit(request):
    name = (request.POST.get("name") or "").strip()
    email = (request.POST.get("email") or "").strip()
    phone = (request.POST.get("phone") or "").strip()
    subject = (request.POST.get("subject") or "").strip()
    message = (request.POST.get("message") or "").strip()

    if not (name and email and phone and subject and message):
        return redirect("/about?sent=0")

    mail_subject = f"[CraveCart Contact] {subject}"
    mail_body = (
        f"New contact form submission:\n\n"
        f"Name: {name}\n"
        f"Email: {email}\n"
        f"Mobile: {phone}\n"
        f"Subject: {subject}\n\n"
        f"Message:\n{message}\n"
    )

    try:
        msg = EmailMessage(
            subject=mail_subject,
            body=mail_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.ADMIN_ORDER_EMAIL],
            reply_to=[email],
        )
        msg.send(fail_silently=False)
        return redirect("/about?sent=1")
    except Exception as e:
        logger.exception("Email sending failed: %s", e)
        return redirect("/about?sent=0")
