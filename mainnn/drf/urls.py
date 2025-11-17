from . import views
from django.urls import path



urlpatterns = [
    path("product_list", views.product_list, name="product_list"),
    path("product/<slug:slug>/", views.product_details, name="product_details"),
    path("categories_list", views.categories_list, name="categories_list"),
    path("category/<slug:slug>/", views.category_detail, name="category_detail"),
    path("add_to_cart/", views.add_to_cart, name="add_to_cart"),
    path("update_cartitem_quantity/", views.update_cartitem_quantity, name="update_cartitem_quantity"),
    path('delete_cartitem/<int:cart_id>/', views.delete_cartitem, name='delete_cartitem'),
    path("add_review/", views.add_review, name="add_review"),
    path('search/', views.product_search, name='search'),
    path('update_review/<int:review_id>/', views.update_review, name='update_review'),
    path('delete_review/<int:review_id>/', views.delete_review, name='delete_review'),
    path('add_to_wishlist/', views.add_to_wishlist, name='add_to_wishlist'),

    path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
    path('webhook/', views.my_webhook_view, name='webhook'),
]
