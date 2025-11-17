import stripe
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view
from django.db.models import Q
from .models import *
from .serializer import *
from rest_framework.response import Response
import traceback
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse



stripe.api_key = settings.STRIPE_SECRET_KEY
endpoint_secret = settings.WEBHOOK_SECRET

# Create your views here.


@api_view(['GET'])
def product_list(request):
    product = Product.objects.filter(featured=True)
    serializer = ProductSerializer(product, many=True)

    return Response(serializer.data)


@api_view(['GET'])
def product_details(request, slug):
    product = Product.objects.get(slug=slug)
    serializer = ProductDetailSerializer(product)

    return (serializer.data)


@api_view(['GET'])
def categories_list(request):
    categories = Category.objects.all()
    serializer = CategoryDetailSerializer(categories, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def category_detail(request, slug):
    category = Category.objects.get(slug=slug)
    serializer = CategoryDetailSerializer(category)
    return Response(serializer.data)

@api_view(['POST'])
def add_to_cart(request):
    cart_code = request.data.get("cart_code")
    product_id = request.data.get('product_id')

    product = Product.objects.get(id=product_id)
    cart, created = Cart.objects.get_or_create(cart_code=cart_code)

    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    cart_item.quantity = 1
    cart_item.save()
    serializer = CartSerializer(cart)
    return Response(serializer.data)


@api_view(['PUT'])
def update_cartitem_quantity(request):
    cartitem_id = request.data.get('item_id')
    quantity = request.data.get('quantity')

    cartitem = CartItem.objects.get(id=cartitem_id)
    cartitem.quantity = quantity
    cartitem.save()
    cart = cartitem.cart # Retrieve the associated cart
    serializer = CartSerializer(cart) # Serializing the entire cart to reflect updated item quantity
    return Response({'data': serializer.data, "message": "Cart item quantity updated successfully"})


@api_view(['POST'])
def add_review(request):
    try:
        print("✅ Request received:", request.data)

        product_id = request.data.get('product_id')
        email = request.data.get('email')
        rating = request.data.get('rating')
        review_text = request.data.get('review_text')
        

        product = Product.objects.get(id=product_id) # Get the product instance
        user = CustomerUser.objects.get(email=email)   # Get the user instance by email

        if Review.objects.filter(product=product, user=user).exists():
            return Response({"error": "You have already reviewed this product."}, status=400)
        
        revieww = Review.objects.create(
            product=product,
            user=user,
            rating=rating,
            review_text=review_text
        )
        serializer = ReviewSerializer(revieww)
        return Response(serializer.data, status=201)

    except Exception as e:
        print("❌ ERROR:", e)
        traceback.print_exc()  # <-- This will show full error trace in terminal
        return Response({"error": str(e)}, status=500)

@api_view(['PUT'])
def update_review(request, review_id):
    try:
        print("request received:", request.data)

        review = Review.objects.get(id=review_id) # Get the review instance
        print("Review ID:", review_id)

        rating = request.data.get('rating')
        review_text = request.data.get('review_text')

        review.rating = rating
        review.review_text = review_text
        review.save()
        serializer = ReviewSerializer(review)
        return Response(serializer.data, status=200)

    except Exception as e:
        print(" ERROR:", e)
        traceback.print_exc()  
        return Response({"error": str(e)}, status=500)
    

@api_view(['DELETE'])
def delete_review(request, review_id):
    revieww = Review.objects.get(id=review_id)
    revieww.delete()
    return Response({"message": "Review deleted successfully."})


@api_view(['DELETE'])
def delete_cartitem(request, cart_id):
    cartitem = get_object_or_404(CartItem, id=cart_id)
    cartitem.delete()
    
    return Response({"message": "item deleted successfully."})


@api_view(['POST'])
def add_to_wishlist(request):
    email = request.data.get('email')
    product_id = request.data.get('product_id')

    user = CustomerUser.objects.get(email=email)
    product = Product.objects.get(id=product_id)

    wishlist = WishList.objects.filter(user=user, product=product)
    if wishlist:
        wishlist.delete()
        return Response('wishlisted removed', status=204)
    
    new_wishlist = WishList.objects.create(user=user, product=product)
    serializer = WishlistSerializer(new_wishlist)
    return Response(serializer.data)


@api_view(['GET'])
def product_search(request):
    query = request.query_params.get('query')
    if not query:
        return Response({"error": "No search query provided."}, status=400)

    product = Product.objects.filter(Q(name__icontains=query) 
                                     | Q(description__icontains=query) 
                                     | Q(category__name__icontains=query))
    
    serializer = ProductSerializer(product, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def create_checkout_session(request):
    cart_code = request.data.get("cart_code")
    email = request.data.get("email")
    cart = Cart.objects.get(cart_code=cart_code)
    try:
        checkout_session = stripe.checkout.Session.create(
            customer_email=email,
            payment_method_types=['card'],
            line_items=[
                {
                    "price_data": {
                        'currency': 'usd',
                        'product_data': {'name' : item.product.name},
                        "unit_amount" : int(item.product.price ) *100,

                    },
                    'quantity': item.quantity,
                }
                for item in cart.cartitems.all()
            ],
            mode='payment',
            success_url= "http://localhost:8000/success",
            cancel_url= "http://localhost:8000/cancel",
            metadata={"cart_code": cart_code}
        )
        return Response({'data': checkout_session})
    except Exception as e:
        return Response({'error': str(e)})

    

@csrf_exempt
def my_webhook_view(request):
  payload = request.body
  sig_header = request.META['HTTP_STRIPE_SIGNATURE']
  event = None

  try:
    event = stripe.Webhook.construct_event(
      payload, sig_header, endpoint_secret
    )
  except ValueError as e:
    # Invalid payload
    return HttpResponse(status=400)
  except stripe.error.SignatureVerificationError as e:
    # Invalid signature
    return HttpResponse(status=400)

  if (
    event['type'] == 'checkout.session.completed'
    or event['type'] == 'checkout.session.async_payment_succeeded'
  ):
    session = event['data']['object']
    cart_code = session.get("metadata", {}).get("cart_code")
    fulfill_checkout(session, cart_code)

  return HttpResponse(status=200)

def fulfill_checkout(session, cart_code):
    try:
        cart = Cart.objects.get(cart_code=cart_code)
    except Cart.DoesNotExist:
        print(f"Cart not found: {cart_code}")
        return
    
    order = Order.objects.create(stripe_checkout_id=session["id"],                             
                                amount=session["amount_total"],
                                currency=session["currency"],
                                customer_email=session["customer_email"],
                                status="Paid",
                                ) # Save the order instance
    
    cart = Cart.objects.get(cart_code=cart_code)
    cartitems = cart.cartitems.all()

    for item in cartitems:
        orderitem = OrderItem.objects.create(
            order=order,   # Link to the order
            product=item.product,   # Link to the product
            quantity=item.quantity,  # Quantity from the cart item
        )
    cart.delete()
