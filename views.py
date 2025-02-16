from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import Categorys, Product, Cart, Order, OrderItem,Rating,Wishlist
import json
from decimal import Decimal

@login_required(login_url="login")
def Home(request):
    categories = Categorys.objects.all()
    return render(request, "home.html", {'categories': categories})

def about(request):
    return render(request, "about.html")

def SignupPage(request):
    if request.method == 'POST':
        uname = request.POST.get('username')
        email = request.POST.get('email')
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')

        if pass1 != pass2:
            return HttpResponse("Your password is wrong")
        else:
            my_user = User.objects.create_user(uname, email, pass1)
            my_user.save()
            return redirect('login')

    return render(request, "home/signup.html")

def LoginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        pass1 = request.POST.get('password')
        user = authenticate(request, username=username, password=pass1)

        if user is not None:
            login(request, user)
            return redirect('all_products')
        else:
            return HttpResponse("Username or password is wrong")

    return render(request, "home/login.html")

def LogoutPage(request):
    logout(request)
    return redirect('login')

def product_list(request):
    categories = Categorys.objects.all()
    category_id = request.GET.get('category', None)
    if category_id:
        category = get_object_or_404(Categorys, id=category_id)
        products = Product.objects.filter(category=category)
    else:
        products = Product.objects.all()
    
    return render(request, 'all_products.html', {'products': products, 'categories': categories})

def category_products(request, id):
    categories = Categorys.objects.all()
    category = get_object_or_404(Categorys, id=id)
    products = Product.objects.filter(category=category)
    return render(request, 'all_products.html', {'products': products, 'categories': categories, 'category': category})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    else:
        cart_item.quantity = 1
        cart_item.save()

    return redirect('all_products')  

@login_required
def cart(request):
    cart_items = Cart.objects.filter(user=request.user)

    
    total_price = 0
    for item in cart_items:
        item.total_price = item.product.price * item.quantity
        total_price += item.total_price  

    return render(request, "cart.html", {"cart_items": cart_items, "total_price": total_price})

def update_cart(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            item_id = data.get('item_id')
            quantity = int(data.get('quantity', 0))

            cart_item = get_object_or_404(Cart, id=item_id, user=request.user)

            if quantity > 0:
                cart_item.quantity = quantity
                cart_item.save()
                item_total = cart_item.product.price * cart_item.quantity
            else:
                cart_item.delete()
                item_total = 0

            cart_items = Cart.objects.filter(user=request.user)
            grand_total = sum(item.product.price * item.quantity for item in cart_items)

            return JsonResponse({
    'success': True, 
    'item_total': round(item_total, 2),  
    'grand_total': round(grand_total, 2)
})

        except (json.JSONDecodeError, ValueError):
            return JsonResponse({'success': False, 'error': 'Invalid data format'}, status=400)

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


def confirm_order(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({"success": False, "error": "User not authenticated"}, status=401)

        user_name = request.POST.get("user_name")
        user_email = request.POST.get("user_email")

        if not user_name or not user_email:
            return JsonResponse({"success": False, "error": "Missing required fields"}, status=400)

        cart_items = Cart.objects.filter(user=request.user)

        if not cart_items.exists():
            return JsonResponse({"success": False, "error": "Cart is empty"}, status=400)

        total_price = sum(item.product.price * item.quantity for item in cart_items)
        total_price = float(total_price) 
       
        order = Order.objects.create(user=request.user, total_price=total_price)

        order_items = []
        for item in cart_items:
            order_item = OrderItem(order=order, product=item.product, quantity=item.quantity, price=item.product.price)
            order_items.append(order_item)

        OrderItem.objects.bulk_create(order_items)

        
        request.session['order_items'] = [
            {'product_name': item.product.name, 'product_id': item.product.id, 'quantity': item.quantity, 'price': float(item.product.price)}
            for item in order_items
        ]
        request.session['total_price'] = total_price 

       
        cart_items.delete()

        return redirect('confirm_order')

    order_items = request.session.get('order_items', [])
    total_price = float(request.session.get('total_price', 0)) 

    return render(request, "confirm_order.html", {"order_items": order_items, "total_price": total_price})

def update_average_rating(self):
    ratings = self.ratings.all()  
    total_ratings = ratings.count()
    if total_ratings > 0:
        self.average_rating = sum(rating.rating for rating in ratings) / total_ratings
    else:
        self.average_rating = 0
    self.save()

@csrf_exempt
@login_required
def submit_ratings(request):
    if request.method == 'POST':
        print(request.POST) 

        for key, value in request.POST.items():
            if key.startswith("rating_"):
                product_id = key.split("_")[1]
                rating_value = int(value)
                product = get_object_or_404(Product, id=product_id)

                order_item = OrderItem.objects.filter(order__user=request.user, product=product).order_by('-order__id').first()

                if order_item:
                
                    existing_rating = Rating.objects.filter(
                        product=product, user=request.user, order=order_item.order
                    ).exists()

                    if not existing_rating:
                      
                        Rating.objects.create(
                            product=product, user=request.user, order=order_item.order, rating=rating_value
                        )

                        
                        product.update_average_rating()
                        product.refresh_from_db() 

                else:
                    return JsonResponse({"success": False, "error": "No order found for this product"}, status=400)

        return JsonResponse({"success": True, "new_average_rating": product.average_rating})

    return JsonResponse({"success": False}, status=400)


def cart_count_view(request):
    if request.user.is_authenticated:
        count = Cart.objects.filter(user=request.user).count()
    else:
        count = 0
    return JsonResponse({'cart_count': count})

def wishlist_view(request):
    wishlist = Wishlist.get_wishlist(request.user)
    wishlist_items = wishlist.products.all()
    return render(request, 'wishlist.html', {'wishlist_items': wishlist_items})

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist = Wishlist.get_wishlist(request.user)
    
    wishlist.products.add(product)  
    return JsonResponse({"success": True, "wishlist_count": wishlist.total_items()})

@login_required
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist = Wishlist.get_wishlist(request.user)
    
    wishlist.products.remove(product)  
    return JsonResponse({"success": True})

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist = Wishlist.get_wishlist(request.user)

    if product in wishlist.products.all():
        wishlist.products.remove(product)
        added = False 
    else:
        wishlist.products.add(product)
        added = True 

    return JsonResponse({"success": True, "added": added, "wishlist_count": wishlist.total_items()})



def wishlist_count(request):
    if request.user.is_authenticated:
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        count = wishlist.products.count()
    else:
        count = 0
    return JsonResponse({'wishlist_count': count})

def add_to_cart_from_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    
    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    wishlist = Wishlist.get_wishlist(request.user)
    wishlist.products.remove(product)
    
    return redirect('wishlist')