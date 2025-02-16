from .models import Cart, Wishlist

def cart_context(request):
    cart_count = Cart.total_items(request.user) if request.user.is_authenticated else 0
    wishlist_count = Wishlist.get_wishlist(request.user).total_items() if request.user.is_authenticated else 0
    
    return {
        'cart_count': cart_count, 
        'wishlist_count': wishlist_count
    }