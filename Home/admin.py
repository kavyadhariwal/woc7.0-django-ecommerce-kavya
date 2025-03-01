from django.contrib import admin

# Register your models here.
from .models import Categorys, Product, Cart, Order, OrderItem,Rating

@admin.register(Categorys)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'created_at')
    list_filter = ('category',)

admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Rating)