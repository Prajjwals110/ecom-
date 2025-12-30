from django.urls import path
from .views import (
    CartDetailView,
    AddToCartView,
    UpdateCartItemView,
    RemoveFromCartView,
    PlaceOrderView
)

urlpatterns = [
    path("cart/", CartDetailView.as_view()),
    path("cart/add/", AddToCartView.as_view()),
    path("cart/item/<int:item_id>/", UpdateCartItemView.as_view()),
    path("cart/item/<int:item_id>/delete/", RemoveFromCartView.as_view()),
    path("orders/place/", PlaceOrderView.as_view()),
]
