
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index),
    path('open_signin', views.open_signin, name='open_signin'),
    path('open_signup', views.open_signup, name='open_signup'),
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('home', views.index, name='home'),
    path('', views.index, name='logout'),
    path('admin_dashboard', views.admin_dashboard, name='admin_dashboard'),
    path('user_dashboard', views.user_dashboard, name='user_dashboard'),
    path('open_add_restaurant', views.open_add_restaurant, name='open_add_restaurant'),
    path('add_restaurant', views.add_restaurant, name='add_restaurant'),
    path('open_show_restaurants', views.open_show_restaurants, name='open_show_restaurants'),
    path('open_update_restaurant/<int:restaurant_id>', views.open_update_restaurant, name='open_update_restaurant'),  
    path('update_restaurant/<int:restaurant_id>', views.update_restaurant, name='update_restaurant'), 
    path('delete_restaurant/<int:restaurant_id>', views.delete_restaurant, name='delete_restaurant'), 
    path('open_update_menu/<int:restaurant_id>', views.open_update_menu, name='open_update_menu'), 
    path('delete_item/<int:item_id>/<int:restaurant_id>',views.delete_item,name='delete_item'),
    path('update_menu/<int:restaurant_id>', views.update_menu, name='update_menu'),
    path('view_menu/<int:restaurant_id>/', views.view_menu, name='view_menu'),
    path('open_customer_show_restaurants',views.open_customer_show_restaurants,name='open_customer_show_restaurants'),
    path('open_update_item/<int:item_id>/<int:restaurant_id>',views.open_update_item,name='open_update_item'),
    path("add_to_cart/<int:item_id>/", views.add_to_cart),
    path("decrease_cart/<int:item_id>/", views.decrease_cart_item),
    path("remove_cart/<int:item_id>/", views.remove_cart_item, name="remove_cart_item"),
    path("cart/", views.view_cart, name="view_cart"),
    path("apply-coupon/", views.apply_coupon),
    path("remove-coupon/", views.remove_coupon),
    path("admin-panel/create-coupon/", views.create_coupon, name="create_coupon"),
    path("admin-panel/toggle-coupon/<int:cid>/",views.toggle_coupon,name="toggle_coupon"),
    path("checkout/", views.checkout, name="checkout"),
    path("payment-success/", views.payment_success, name="payment_success"),
    path("orders/", views.order_history, name="order_history"),
    path("logout", views.logout, name="logout"),


]

urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)
