from django.urls import path
from . import views


urlpatterns = [

    path(
        '',
        views.home,
        name='home'
    ),

    path(
        'signup/',
        views.register,
        name='register'
    ),

    path(
        'login/',
        views.login_view,
        name='login'
    ),
path(
    'add-to-cart/<int:id>/',
    views.add_to_cart,
    name='add_to_cart'
),
    path(
        'logout/',
        views.logout_view,
        name='logout'
    ),

    path(
        'thankyou/',
        views.thankyou,
        name='thankyou'
    ),


    # Cart
    path(
        'cart/',
        views.cart,
        name='cart'
    ),


    # Remove item from cart
    path(
        'remove-cart/<int:id>/',
        views.remove_from_cart,
        name='remove_from_cart'
    ),
path('payment-success/', views.payment_success, name='payment_success'),

    # Increase quantity
    path(
        'increase/<int:id>/',
        views.increase_quantity,
        name='increase_quantity'
    ),


    # Decrease quantity
    path(
        'decrease/<int:id>/',
        views.decrease_quantity,
        name='decrease_quantity'
    ),


    # Checkout
    path(
        'checkout/',
        views.checkout,
        name='checkout'
    ),


    # Order success
    path(
        'order-success/',
        views.order_success,
        name='order_success'
    ),


    # Product description
    path(
        'product-description/<int:id>/',
        views.product_description,
        name='product_description'
    ),
    path(
    "orders/",
    views.my_orders,
    name="my_orders"
),

 path('payment-success/', views.payment_success, name='payment_success'),
]