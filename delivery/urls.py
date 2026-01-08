
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView


urlpatterns = [
    path("", views.index, name="home"),

    path("open_signin", views.open_signin, name="open_signin"),
    path("open_signup", views.open_signup, name="open_signup"),
    path("signup", views.signup, name="signup"),
    path("signin", views.signin, name="signin"),
    path("logout", views.logout, name="logout"),

    path("admin_dashboard", views.admin_dashboard, name="admin_dashboard"),
    path("user_dashboard", views.user_dashboard, name="user_dashboard"),

    path("open_add_restaurant", views.open_add_restaurant),
    path("add_restaurant", views.add_restaurant),
    path("open_show_restaurants", views.open_show_restaurants),
    path("open_update_restaurant/<int:restaurant_id>", views.open_update_restaurant),
    path("update_restaurant/<int:restaurant_id>", views.update_restaurant),
    path("delete_restaurant/<int:restaurant_id>", views.delete_restaurant),

    path("open_update_menu/<int:restaurant_id>", views.open_update_menu),
    path("update_menu/<int:restaurant_id>", views.update_menu),
    path("open_update_item/<int:item_id>/<int:restaurant_id>", views.open_update_item),
    path("delete_item/<int:item_id>/<int:restaurant_id>", views.delete_item),

    path("view_menu/<int:restaurant_id>/", views.view_menu),
    path("open_customer_show_restaurants", views.open_customer_show_restaurants),

    path("add_to_cart/<int:item_id>/", views.add_to_cart),
    path("decrease_cart/<int:item_id>/", views.decrease_cart_item),
    path("remove_cart/<int:item_id>/", views.remove_cart_item),

    path("cart/", views.view_cart),
    path("checkout/", views.checkout),
    path("payment-success/", views.payment_success),

    path("orders/", views.order_history),
    path("orders/<int:order_id>/rate/", views.rate_order),
    path("reorder/<int:order_id>/", views.reorder),

    path("admin-panel/orders/", views.admin_orders),
    path("admin-panel/orders/<int:order_id>/", views.admin_order_detail),
    path("admin-panel/orders/<int:order_id>/update/", views.admin_update_order_status),

    path("admin-panel/create-coupon/", views.create_coupon),
    path("admin-panel/toggle-coupon/<int:cid>/", views.toggle_coupon),
    path("admin-panel/ratings/", views.admin_ratings_dashboard),

    path("invoice/<int:order_id>/", views.download_invoice),
    path("order-status/<int:order_id>/", views.order_status_api),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)