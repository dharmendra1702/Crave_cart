
# from django.contrib import admin
# from django.urls import path, include
# from django.contrib.auth import views as auth_views
# from . import views
# from django.conf import settings
# from django.conf.urls.static import static
# from django.views.generic import RedirectView
# from django.views.generic.base import RedirectView



# urlpatterns = [
#     path('', views.index),
#     path('open_signin', views.open_signin, name='open_signin'),
#     path('open_signup', views.open_signup, name='open_signup'),
#     path('signup', views.signup, name='signup'),
#     path('signin', views.signin, name='signin'),
#     path('home', views.index, name='home'),
#     path('', views.index, name='logout'),
#     path('admin_dashboard', views.admin_dashboard, name='admin_dashboard'),
#     path('user_dashboard', views.user_dashboard, name='user_dashboard'),
#     path('open_add_restaurant', views.open_add_restaurant, name='open_add_restaurant'),
#     path('add_restaurant', views.add_restaurant, name='add_restaurant'),
#     path('open_show_restaurants', views.open_show_restaurants, name='open_show_restaurants'),
#     path('open_update_restaurant/<int:restaurant_id>', views.open_update_restaurant, name='open_update_restaurant'),  
#     path('update_restaurant/<int:restaurant_id>', views.update_restaurant, name='update_restaurant'), 
#     path('delete_restaurant/<int:restaurant_id>', views.delete_restaurant, name='delete_restaurant'), 
#     path('open_update_menu/<int:restaurant_id>', views.open_update_menu, name='open_update_menu'), 
#     path('delete_item/<int:item_id>/<int:restaurant_id>',views.delete_item,name='delete_item'),
#     path('update_menu/<int:restaurant_id>', views.update_menu, name='update_menu'),
#     path('view_menu/<int:restaurant_id>/', views.view_menu, name='view_menu'),
#     path('open_customer_show_restaurants',views.open_customer_show_restaurants,name='open_customer_show_restaurants'),
#     path('open_update_item/<int:item_id>/<int:restaurant_id>',views.open_update_item,name='open_update_item'),
#     path("add_to_cart/<int:item_id>/", views.add_to_cart),
#     path("decrease_cart/<int:item_id>/", views.decrease_cart_item),
#     path("remove_cart/<int:item_id>/", views.remove_cart_item, name="remove_cart_item"),
#     path("cart/", views.view_cart, name="view_cart"),
#     path("apply-coupon/", views.apply_coupon, name="apply_coupon"),
#     path("remove-coupon/", views.remove_coupon, name="remove_coupon"),
#     path("admin-panel/create-coupon/", views.create_coupon, name="create_coupon"),
#     path("admin-panel/toggle-coupon/<int:cid>/",views.toggle_coupon,name="toggle_coupon"),
#     path("checkout/", views.checkout, name="checkout"),
#     path("payment-success/", views.payment_success, name="payment_success"),
#     path("orders/", views.order_history, name="order_history"),
#     path("logout", views.logout, name="logout"),
#     path("invoice/<int:order_id>/", views.download_invoice, name="download_invoice"),
#     path("reorder/<int:order_id>/", views.reorder, name="reorder"),
#     path("order-status/<int:order_id>/", views.order_status_api, name="order_status_api"),
#     path("admin-panel/orders/", views.admin_orders, name="admin_orders"),
#     path("admin-panel/orders/<int:order_id>/", views.admin_order_detail, name="admin_order_detail"),
#     path("admin-panel/orders/<int:order_id>/update/", views.admin_update_order_status, name="admin_update_order_status"),
#     path("admin-panel/ratings/", views.admin_ratings_dashboard, name="admin_ratings"),
#     path("orders/<int:order_id>/rate/", views.rate_order, name="rate_order"),
#     path("favicon.ico",RedirectView.as_view(url="/static/images/faviconn.png",permanent=True)),
#     path("profile/", profile_view, name="profile"),





# ]

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

from . import views


urlpatterns = [
    # Home
    path('', views.index, name='home'),
    path("contact/", views.contact_submit, name="contact_submit"),
    path("about/", views.about, name="about"),

    # Auth
    path('open_signin', views.open_signin, name='open_signin'),
    path('open_signup', views.open_signup, name='open_signup'),
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('logout', views.logout, name='logout'),

    # Dashboards
    path('admin_dashboard', views.admin_dashboard, name='admin_dashboard'),
    path('user_dashboard', views.user_dashboard, name='user_dashboard'),

    # Profile ✅
    path("profile/photo/", views.update_profile_photo, name="update_profile_photo"),
    path("profile/", views.profile_view, name="profile"),
    path("profile/update/", views.update_profile, name="update_profile"),
    path("profile/email/verify-password/",views.verify_email_password, name="verify_email_password"),
    path("profile/email/update/",views.update_email, name="update_email"),
    path("profile/username/verify-password/",views.verify_username_password,name="verify_username_password"),
    path("profile/username/update/",views.update_username,name="update_username"),
    path("add-extra-mobile/", views.add_extra_mobile, name="add_extra_mobile"),
    path("delete-extra-mobile/<int:mid>/", views.delete_extra_mobile, name="delete_extra_mobile"),
    path("add-extra-address/", views.add_extra_address, name="add_extra_address"),
    path("delete-extra-address/<int:aid>/", views.delete_extra_address, name="delete_extra_address"),
    path("make-primary-mobile/<int:mid>/", views.make_primary_mobile, name="make_primary_mobile"),
    path("make-default-address/<int:aid>/", views.make_default_address, name="make_default_address"),




    # Restaurant
    path('open_add_restaurant', views.open_add_restaurant, name='open_add_restaurant'),
    path('add_restaurant', views.add_restaurant, name='add_restaurant'),
    path('open_show_restaurants', views.open_show_restaurants, name='open_show_restaurants'),
    path('open_update_restaurant/<int:restaurant_id>', views.open_update_restaurant, name='open_update_restaurant'),
    path('update_restaurant/<int:restaurant_id>', views.update_restaurant, name='update_restaurant'),
    path('delete_restaurant/<int:restaurant_id>', views.delete_restaurant, name='delete_restaurant'),

    # Menu
    path('open_update_menu/<int:restaurant_id>', views.open_update_menu, name='open_update_menu'),
    path('update_menu/<int:restaurant_id>', views.update_menu, name='update_menu'),
    path('open_update_item/<int:item_id>/<int:restaurant_id>', views.open_update_item, name='open_update_item'),
    path('delete_item/<int:item_id>/<int:restaurant_id>', views.delete_item, name='delete_item'),
    path('view_menu/<int:restaurant_id>/', views.view_menu, name='view_menu'),

    # Customer
    path('open_customer_show_restaurants', views.open_customer_show_restaurants, name='open_customer_show_restaurants'),

    # Cart
    path("add_to_cart/<int:item_id>/", views.add_to_cart),
    path("decrease_cart/<int:item_id>/", views.decrease_cart_item),
    path("remove_cart/<int:item_id>/", views.remove_cart_item, name="remove_cart_item"),
    path("cart/", views.view_cart, name="view_cart"),

    # Coupon
    path("apply-coupon/", views.apply_coupon, name="apply_coupon"),
    path("remove-coupon/", views.remove_coupon, name="remove_coupon"),
    path("admin-panel/create-coupon/", views.create_coupon, name="create_coupon"),
    path("admin-panel/toggle-coupon/<int:cid>/", views.toggle_coupon, name="toggle_coupon"),

    # Checkout & Orders
    path("checkout/", views.checkout, name="checkout"),
    path("payment-success/", views.payment_success, name="payment_success"),
    path("orders/", views.order_history, name="order_history"),
    path("orders/<int:order_id>/rate/", views.rate_order, name="rate_order"),
    path("invoice/<int:order_id>/", views.download_invoice, name="download_invoice"),
    path("reorder/<int:order_id>/", views.reorder, name="reorder"),
    path("order-status/<int:order_id>/", views.order_status_api, name="order_status_api"),
    path("order/<int:order_id>/cancel/", views.cancel_order, name="cancel_order"),
    path("checkout/add-address/", views.add_address_ajax, name="add_address_ajax"),
    path("checkout/set-selection/", views.set_checkout_selection, name="set_checkout_selection"),
    path("checkout/cod/", views.place_cod_order, name="place_cod_order"),

    

    # Admin Orders
    path("admin-panel/orders/", views.admin_orders, name="admin_orders"),
    path("admin-panel/orders/<int:order_id>/", views.admin_order_detail, name="admin_order_detail"),
    path("admin-panel/orders/<int:order_id>/update/", views.admin_update_order_status, name="admin_update_order_status"),
    path("admin-panel/ratings/", views.admin_ratings_dashboard, name="admin_ratings"),

    # Favicon
    path(
        "favicon.ico",
        RedirectView.as_view(
            url="/static/images/faviconn.png",
            permanent=True
        )
    ),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
