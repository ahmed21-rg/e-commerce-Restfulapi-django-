from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from django.conf import settings


# Create your models here.
class CustomerUser(AbstractUser):
    email = models.EmailField(unique=True)
    profile_picture_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.email
    
class Category(models.Model):
    name = models.TextField()
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to="category_image", blank=True, null=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            unique_slug = self.slug
            counter = 1
            if Product.objects.filter(slug=unique_slug).exists():
                unique_slug = f'{self.slug}-{counter}'
                counter += 1

            self.slug = unique_slug
        super().save(*args, **kwargs)

class Product(models.Model):
    name = models.TextField()
    description = models.TextField(max_length=400, null=True)
    price = models.DecimalField( max_digits=40, decimal_places=2)
    slug = models.SlugField(unique=True, blank=True)
    image_feild = models.ImageField(upload_to="product_image", blank=False)
    featured = models.BooleanField(default=True)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE, blank=True)
     
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            unique_slug = self.slug
            counter = 1
            if Product.objects.filter(slug=unique_slug).exists():
                unique_slug = f'{self.slug}-{counter}'
                counter += 1

            self.slug = unique_slug
        super().save(*args, **kwargs)


class Cart(models.Model):
    cart_code = models.CharField(max_length=11, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.cart_code
    

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cartitems')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='items')
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f'{self.quantity} * {self.product.price} in cart {self.cart.cart_code}'
    

class Review(models.Model):

    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    ]
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=RATING_CHOICES)
    review_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'Review of {self.product.name} by {self.user.username}'
    class Meta:
        unique_together = ['product', 'user'] # Ensure one review per user per product
        ordering = ['-created_at']


class ProductRating(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='ratings')
    average_rating = models.FloatField(default=0.0)
    total_reviews = models.IntegerField(default=0)

    def __str__(self):
        return f'Rating for {self.product.name}: {self.average_rating} ({self.total_reviews} reviews)'


class WishList(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlists')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlisted')
    added_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.user.username} wishlisted {self.product.name}'
    class Meta:
        unique_together = ['user', 'product']  # Ensure one wishlist entry per user per product



class Order(models.Model):
    stripe_checkout_id = models.CharField(max_length=255, unique=True)  #Stripe Checkout Session ID
    amount = models.DecimalField(max_digits=40, decimal_places=2)
    currency = models.CharField(max_length=10)
    customer_email = models.EmailField()
    status = models.CharField(max_length=50, choices=[('Pending', 'Pending'), ('Completed', 'Completed'), ('Paid', 'Paid'), ('Failed', 'Failed')], default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Order {self.stripe_checkout_id} - {self.status}'
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f'{self.product.name} {self.order.stripe_checkout_id}'