from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import JsonResponse

from .models import Product, Category, Cart, Order

import razorpay
import json


# ================= HOME =================

def home(request):

    products = Product.objects.all()
    categories = Category.objects.all()

    category_id = request.GET.get("category")
    if category_id:
        products = products.filter(category_id=category_id)

    query = request.GET.get("query")
    if query:
        products = products.filter(name__icontains=query)

    cart_count = 0
    if request.user.is_authenticated:
        cart_count = Cart.objects.filter(user=request.user).count()

    return render(request, "home.html", {
        "products": products,
        "categories": categories,
        "cart_count": cart_count
    })


# ================= REGISTER =================

def register(request):

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("register")

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(request, "Account created successfully")
        return redirect("login")

    return render(request, "register.html")


# ================= LOGIN =================

def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            messages.success(request, "Login Successful")
            return redirect("home")
        else:
            messages.error(request, "Invalid Username or Password")

    return render(request, "login.html")


# ================= LOGOUT =================

def logout_view(request):
    logout(request)
    return redirect("login")


# ================= THANK YOU =================

def thankyou(request):
    return render(request, "thankyou.html")


# ================= PRODUCT DESCRIPTION =================

def product_description(request, id):

    product = get_object_or_404(Product, id=id)

    return render(request, "product_description.html", {
        "product": product
    })


# ================= ADD TO CART =================

@login_required
def add_to_cart(request, id):

    product = get_object_or_404(Product, id=id)

    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect("home")


# ================= CART =================
@login_required
def cart(request):

    cart_items = Cart.objects.filter(user=request.user)

    total = sum(item.product.price * item.quantity for item in cart_items)

    # Razorpay client
    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    # Create order
    payment = client.order.create({
        "amount": int(total * 100),   # paisa
        "currency": "INR",
        "payment_capture": 1
    })

    return render(request, "cart.html", {
        "cart_items": cart_items,
        "total": total,
        "payment": payment,
        "RAZORPAY_KEY_ID": settings.RAZORPAY_KEY_ID
    })

# ================= REMOVE FROM CART =================

@login_required
def remove_from_cart(request, id):

    cart_item = get_object_or_404(Cart, id=id, user=request.user)
    cart_item.delete()

    return redirect("cart")


# ================= INCREASE QUANTITY =================

@login_required
def increase_quantity(request, id):

    cart_item = get_object_or_404(Cart, id=id, user=request.user)
    cart_item.quantity += 1
    cart_item.save()

    return redirect("cart")


# ================= DECREASE QUANTITY =================

@login_required
def decrease_quantity(request, id):

    cart_item = get_object_or_404(Cart, id=id, user=request.user)

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()

    return redirect("cart")


# ================= CHECKOUT =================

@login_required
def checkout(request):

    cart_items = Cart.objects.filter(user=request.user)
    total = sum(item.product.price * item.quantity for item in cart_items)

    # ✅ Razorpay client
    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    # ✅ Create Razorpay order
    payment = client.order.create({
        "amount": int(total * 100),
        "currency": "INR",
        "payment_capture": 1
    })

    if request.method == "POST":

        address = request.POST.get("address")
        phone = request.POST.get("phone")
        payment_method = request.POST.get("payment_method")

        # ✅ COD FLOW
        if payment_method == "COD":

            for item in cart_items:
                Order.objects.create(
                    customer=request.user,
                    product=item.product,
                    quantity=item.quantity,
                    total=item.product.price * item.quantity,
                    address=address,
                    phone=phone,
                    payment_method="COD"
                )

            cart_items.delete()
            return redirect("order_success")

        # ✅ Razorpay → wait for success API
        return redirect("checkout")

    return render(request, "checkout.html", {
        "cart_items": cart_items,
        "total": total,
        "payment": payment,
        "order_id": payment["id"],
        "RAZORPAY_KEY_ID": settings.RAZORPAY_KEY_ID
    })


# ================= PAYMENT SUCCESS =================

@login_required
def payment_success(request):

    if request.method == "POST":

        data = json.loads(request.body)

        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

        try:
            # ✅ VERIFY PAYMENT
            client.utility.verify_payment_signature({
                'razorpay_order_id': data['razorpay_order_id'],
                'razorpay_payment_id': data['razorpay_payment_id'],
                'razorpay_signature': data['razorpay_signature']
            })

            cart_items = Cart.objects.filter(user=request.user)

            for item in cart_items:
                Order.objects.create(
                    customer=request.user,
                    product=item.product,
                    quantity=item.quantity,
                    total=item.product.price * item.quantity,
                    payment_method="RAZORPAY"
                )

            cart_items.delete()

            return JsonResponse({"status": "success"})

        except:
            return JsonResponse({"status": "failed"})


# ================= ORDER SUCCESS =================

def order_success(request):
    return render(request, "order_success.html")


# ================= MY ORDERS =================

@login_required
def my_orders(request):

    orders = Order.objects.filter(
        customer=request.user
    ).order_by("-id")

    return render(request, "my_orders.html", {
        "orders": orders
    })
    
import json
from django.http import JsonResponse
from .utils import send_sms   # we will create this

def payment_success(request):
    if request.method == "POST":

        data = json.loads(request.body)
        payment_id = data.get("payment_id")

        # 👉 (IMPORTANT) Update your order/cart here
        # Example:
        # order.status = "PAID"
        # order.save()

        # 👉 Send SMS
        send_sms("9307750580", f"Payment successful. ID: {payment_id}")

        return JsonResponse({"status": "success"})