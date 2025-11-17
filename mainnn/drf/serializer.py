from rest_framework import serializers
from .models import *


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'description', 'image_feild', 'price']



class ProductDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'description', 'image_feild', 'price']



class CategoryDetailSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    class Meta:
        model = Category
        fields = ['id', 'name', 'image', 'products']

class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'image', 'slug']


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    sub_total = serializers.SerializerMethodField()
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'sub_total']

    def get_sub_total(self, cartitem):
        total = cartitem.product.price * cartitem.quantity
        return total
        
class CartSerializer(serializers.ModelSerializer):
    cartitems = CartItemSerializer(read_only=True, many=True)
    cart_total = serializers.SerializerMethodField()
    class Meta:
        model = Cart
        fields = ['id', 'cart_code', 'cartitems', 'cart_total']

    def get_cart_total(self, cart):
        items = cart.cartitems.all()
        total = sum([item.quantity * item.product.price for item in items])
        return total
    
class CartStatSerializer(serializers.ModelSerializer):
    total_quantity = serializers.SerializerMethodField()
    class Meta:
        model = Cart
        feilds = ['id', 'cart_code', 'quantity']

    def get_cart_quantity(self, cart):
        items = cart.cartitems.all()
        total = sum([item.quantity for item in items])
        return total
    


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile_picture_url']


class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Review
        fields = ['id', 'user', 'rating', 'review_text', 'created_at', 'updated_at']
    

class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = WishList
        fields = ['id', 'user', 'product', 'added_at']