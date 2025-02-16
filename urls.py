from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from Home.views import (
    SignupPage, LoginPage, LogoutPage, product_list, cart, update_cart, confirm_order,
    category_products, add_to_cart, about, Home, submit_ratings, cart_count_view, wishlist_view, add_to_wishlist, remove_from_wishlist, add_to_cart, wishlist_count,add_to_cart_from_wishlist
)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', Home, name='home'),
    path('about/', about, name='about'),
    path('admin/', admin.site.urls),
    path('all-products/', product_list, name='all_products'),
    path('category/<int:id>/', category_products, name='category_products'),
    path('signup/', SignupPage, name='signup'),
    path('login/', LoginPage, name='login'),
    path('logout/', LogoutPage, name='logout'),
    path('add-to-cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/', cart, name='cart'),
    path('update-cart/', update_cart, name='update_cart'),
    path('confirm-order/', confirm_order, name='confirm_order'), 
    path('submit-ratings/', submit_ratings, name='submit_ratings'),
    path('cart/count/', cart_count_view, name='cart_count'), 
      path('wishlist/', wishlist_view, name='wishlist'),
    path('wishlist/add/<int:product_id>/', add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/add-to-cart/<int:product_id>/', add_to_cart_from_wishlist, name='add_to_cart_from_wishlist'),  # ✅ Fixing URL
    path('wishlist/count/', wishlist_count, name='wishlist_count'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
