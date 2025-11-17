from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin



# Register your models here.
class CustomerUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name']

admin.site.register(CustomerUser, CustomerUserAdmin)


class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'description',  'featured']

admin.site.register(Product, ProductAdmin )

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']

admin.site.register(Category, CategoryAdmin)



admin.site.register([Cart, CartItem, Review, ProductRating, WishList, Order, OrderItem])