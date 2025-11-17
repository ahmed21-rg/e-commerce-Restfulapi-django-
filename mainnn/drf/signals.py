from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import *
from django.db.models import Avg


@receiver(post_save, sender=Review)
def update_product_rating_onsave(sender, instance, **kwargs):
    product = instance.product # Get the associated product
    reviews = Review.objects.filter(product=product) # Get all reviews for the product
    total_reviews = reviews.count()
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0.0 # Calculate average rating

    product_rating, created = ProductRating.objects.get_or_create(product=product)  # Get or create ProductRating
    product_rating.average_rating = average_rating # Update average rating
    product_rating.total_reviews = total_reviews    # Update total reviews
    product_rating.save()                          # Save the changes