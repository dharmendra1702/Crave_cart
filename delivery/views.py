import json
import random
import razorpay
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import Cart, CartItem, Order, OrderItem, User
from .models import Restaurant
from .models import Item
from .models import Coupon

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
    

def signin(request):
    #Go to sign in page and authenticate user
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        # Authenticate user
        try:
            user = User.objects.get(username=username, password=password)

            # Set session
            request.session["username"] = user.username
            # Redirect based on user role if admin or normal user
            if user.username.lower() == "admin":
                return redirect("admin_dashboard")
            else:
                restaurants = Restaurant.objects.all()
            return render(request, 'user_dashboard.html',{"restaurants" : restaurants, "username" : username})
            # return render(request, "user_dashboard.html", {
        except User.DoesNotExist:
            return render(request, "fail.html")

    return render(request, "signin.html")

def admin_dashboard(request):
    username = request.session.get("username")

    # safety check
    if username != "admin":
        return redirect("signin")

    return render(request, "admin_dashboard.html", {
        "username": username
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

def add_restaurant(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        picture = request.POST.get('picture')
        cuisine = request.POST.get('cuisine')
        rating = request.POST.get('rating')
        location = request.POST.get('location')

        # check duplicate
        if Restaurant.objects.filter(name=name).exists():
            return render(request, "restaurant_fail.html", {
                "name": name
            })

        # save restaurant
        restaurant = Restaurant.objects.create(
            name=name,
            picture=picture,
            cuisine=cuisine,
            rating=rating,
            location=location
        )

        return render(request, "restaurant_success.html", {
            "restaurant": restaurant
        })

    return render(request, 'admin_dashboard.html')

def open_show_restaurants(request):
    restaurants = Restaurant.objects.all()
    return render(request, 'show_restaurants.html', {
        'restaurants': restaurants })

def open_update_restaurant(request, restaurant_id):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    return render(request, 'update_restaurant.html', {"restaurant" : restaurant})

def update_restaurant(request, restaurant_id):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        picture = request.POST.get('picture')
        cuisine = request.POST.get('cuisine')
        rating = request.POST.get('rating')
        location = request.POST.get('location')
        
        restaurant.name = name
        restaurant.picture = picture
        restaurant.cuisine = cuisine
        restaurant.rating = rating
        restaurant.location = location

        restaurant.save()

    return render(request, "restaurant_update_success.html", {
            "restaurant": restaurant
        })

def delete_restaurant(request, restaurant_id):
    if request.method == "POST":
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        restaurant.delete()
    return redirect("open_show_restaurants")


def open_update_menu(request, restaurant_id):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    itemList = restaurant.items.all()
    #itemList = Item.objects.all()
    return render(request, 'update_menu.html',{"itemList" : itemList, "restaurant" : restaurant})

def update_menu(request, restaurant_id):
    restaurant = Restaurant.objects.get(id=restaurant_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        vegeterian = request.POST.get('vegeterian') == 'on'
        picture = request.POST.get('picture')

        # duplicate check PER RESTAURANT
        if Item.objects.filter(restaurant=restaurant, name=name).exists():
            itemList = restaurant.items.all()
            return render(request, 'update_menu.html', {
                "restaurant": restaurant,
                "itemList": itemList,
                "error": "Item already exists"
            })

        Item.objects.create(
            restaurant=restaurant,
            name=name,
            description=description,
            price=price,
            vegeterian=vegeterian,
            picture=picture,
        )

    # reload menu page
    itemList = restaurant.items.all()
    return render(request, 'update_menu.html', {
        "restaurant": restaurant,
        "itemList": itemList,
        "success": "Item added successfully"
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

    restaurant = Restaurant.objects.get(id=restaurant_id)
    items = restaurant.items.all()

    cart = Cart.objects.filter(username=username).first()

    cart_quantities = {}
    if cart:
        for ci in CartItem.objects.filter(cart=cart):
            cart_quantities[ci.item_id] = ci.quantity

    return render(request, "view_menu.html", {
        "restaurant": restaurant,
        "itemList": items,
        "cart_quantities": cart_quantities
    })




@ensure_csrf_cookie
def open_customer_show_restaurants(request):
    username = request.session.get("username")
    if not username:
        return redirect("signin")

    restaurants = Restaurant.objects.all()
    return render(request, "customer_show_restaurants.html", {
        "restaurants": restaurants,
        "username": username
    })


@require_POST
def add_to_cart(request, item_id):
    username = request.session["username"]
    request.session.pop("applied_coupon", None)

    cart, _ = Cart.objects.get_or_create(username=username)
    item = Item.objects.get(id=item_id)
    ci, created = CartItem.objects.get_or_create(cart=cart, item=item)

    if not created:
        ci.quantity += 1
    ci.save()

    return JsonResponse({"success": True})


@require_POST
def decrease_cart_item(request, item_id):
    username = request.session["username"]
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

    if cart:
        for ci in CartItem.objects.filter(cart=cart):
            cart_items.append({
                "item": ci.item,
                "quantity": ci.quantity,
                "subtotal": ci.item.price * ci.quantity
            })
            cart_count += ci.quantity

    totals = calculate_cart_totals(request, cart)
    request.session["checkout_data"] = totals

    remaining = max(99 - totals["product_total"], 0)

    return render(request, "cart.html", {
        "cart_items": cart_items,
        "cart_count": cart_count,
        "remaining": remaining,
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
    username = request.session["username"]

    cart = Cart.objects.get(username=username)
    totals = calculate_cart_totals(request, cart)

    coupon = Coupon.objects.get(code__iexact=code, is_active=True)

    if totals["product_total"] < coupon.min_order_amount:
        return JsonResponse({"error": "Minimum order not met"})

    if coupon.discount_type == "percent":
        discount = totals["product_total"] * coupon.discount_value / 100
    else:
        discount = coupon.discount_value

    request.session["applied_coupon"] = {
        "code": coupon.code,
        "discount": round(discount, 2),
        "min_order": coupon.min_order_amount
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
    # 🔒 ADMIN CHECK (SESSION BASED)
    if request.session.get("username") != "admin":
        return redirect("signin")

    message = None

    if request.method == "POST":
        discount_type = request.POST.get("discount_type")
        discount_value = request.POST.get("discount_value")
        min_order_amount = request.POST.get("min_order_amount", 0)
        is_active = "is_active" in request.POST

        # 🔹 BULK CREATE
        if request.POST.get("bulk"):
            for _ in range(50):
                Coupon.objects.create(
                    code=generate_unique_coupon(),
                    discount_type=discount_type,
                    discount_value=discount_value,
                    min_order_amount=min_order_amount,
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
                    is_active=is_active
                )
                message = "✅ Coupon created successfully!"

    coupons = Coupon.objects.all().order_by("-id")

    # ✅ IMPORTANT: RENDER — NOT REDIRECT
    return render(request, "coupon.html", {
        "coupons": coupons,
        "message": message
    })




def toggle_coupon(request, cid):
    coupon = get_object_or_404(Coupon, id=cid)
    coupon.is_active = not coupon.is_active
    coupon.save()
    return redirect("create_coupon")

def place_order(request):
    username = request.session.get("username")
    user = User.objects.get(username=username)

    # ✅ order placed successfully here
    # Order.objects.create(...)

    coupon_data = request.session.get("applied_coupon")

    if coupon_data:
        coupon = Coupon.objects.get(code=coupon_data["code"])

        # ✅ mark used AFTER success
        coupon.used_by.add(user)

        # OPTIONAL: delete coupon permanently
        coupon.delete()

        request.session.pop("applied_coupon", None)

    Cart.objects.filter(username=username).delete()

    return render(request, "order_success.html")

import razorpay
from django.conf import settings

def checkout(request):
    username = request.session.get("username")
    if not username:
        return redirect("signin")

    user = User.objects.get(username=username)
    cart = Cart.objects.get(username=username)
    cart_items = CartItem.objects.filter(cart=cart)

    # 1️⃣ Calculate totals ONLY HERE
    product_total = sum(ci.item.price * ci.quantity for ci in cart_items)

    delivery_fee = 0 if product_total >= 99 else 40
    coupon_discount = request.session.get("applied_coupon", {}).get("discount", 0)

    taxable = product_total - coupon_discount
    gst = round(taxable * 0.05, 2)
    grand_total = round(taxable + gst + delivery_fee, 2)

    # 2️⃣ Create Razorpay Order
    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    razorpay_order = client.order.create({
        "amount": int(grand_total * 100),  # ✅ paise
        "currency": "INR",
        "payment_capture": 1
    })

    # 3️⃣ Save order_id in session (VERY IMPORTANT)
    request.session["razorpay_order_id"] = razorpay_order["id"]

    return render(request, "checkout.html", {
        "customer": user,
        "cart_items": cart_items,
        "product_total": product_total,
        "delivery_fee": delivery_fee,
        "gst": gst,
        "coupon_discount": coupon_discount,
        "grand_total": grand_total,
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        "order_id": razorpay_order["id"],  # ✅ SAME order
    })




@require_POST
def payment_success(request):
    username = request.session["username"]
    user = User.objects.get(username=username)
    checkout_data = request.session["checkout_data"]

    cart = Cart.objects.get(username=username)

    data = json.loads(request.body)

    if data.get("razorpay_order_id") != request.session.get("razorpay_order_id"):
        return JsonResponse({"error": "Order mismatch"}, status=400)
    
    order = Order.objects.create(
        user=user,
        total_amount=checkout_data["grand_total"],
        payment_id=json.loads(request.body).get("razorpay_payment_id")
    )

    for ci in CartItem.objects.filter(cart=cart):
        OrderItem.objects.create(
            order=order,
            item_name=ci.item.name,
            price=ci.item.price,
            quantity=ci.quantity
        )

    CartItem.objects.filter(cart=cart).delete()
    cart.delete()

    request.session.pop("applied_coupon", None)
    request.session.pop("checkout_data", None)

    return JsonResponse({"success": True})


def order_success(request):
    request.session.pop("checkout_data", None)
    request.session.pop("applied_coupon", None)
    Cart.objects.filter(username=request.session.get("username")).delete()
    return render(request, "order_success.html")

def order_history(request):
    user = User.objects.get(username=request.session["username"])
    orders = Order.objects.filter(user=user).order_by("-created_at")
    return render(request, "order_history.html", {"orders": orders})


from .models import CartItem

FREE_DELIVERY_LIMIT = 99
DELIVERY_CHARGE = 40
GST_RATE = 0.05

def calculate_cart_totals(request, cart):
    product_total = 0

    for ci in CartItem.objects.filter(cart=cart):
        product_total += ci.item.price * ci.quantity

    # Delivery
    delivery_fee = 0 if product_total >= FREE_DELIVERY_LIMIT else DELIVERY_CHARGE

    # Coupon
    coupon_data = request.session.get("applied_coupon")
    coupon_discount = 0

    if coupon_data:
        if product_total < coupon_data["min_order"]:
            request.session.pop("applied_coupon", None)
        else:
            coupon_discount = coupon_data["discount"]

    taxable = max(product_total - coupon_discount, 0)
    gst = round(taxable * GST_RATE, 2)
    grand_total = round(taxable + gst + delivery_fee, 2)

    return {
        "product_total": product_total,
        "delivery_fee": delivery_fee,
        "coupon_discount": coupon_discount,
        "gst": gst,
        "grand_total": grand_total
    }


@require_POST
def cancel_order(request, order_id):
    order = Order.objects.get(id=order_id, user__username=request.session["username"])
    if order.status == "PLACED":
        order.status = "CANCELLED"
        order.save()
    return redirect("order_history")
