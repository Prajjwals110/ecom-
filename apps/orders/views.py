from django.db import transaction
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Cart, CartItem, Order, OrderItem
from apps.products.models import Product
from .serializers import CartSerializer

class CartDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id = request.data.get("product")
        quantity = int(request.data.get("quantity", 1))

        product = get_object_or_404(Product, id=product_id, is_active=True)

        if product.stock < quantity:
            return Response(
                {"detail": "Not enough stock"},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart, _ = Cart.objects.get_or_create(user=request.user)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product
        )

        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity

        cart_item.save()
        return Response(
            {"detail": "Product added to cart"},
            status=status.HTTP_200_OK
        )


class UpdateCartItemView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, item_id):
        cart_item = get_object_or_404(
            CartItem,
            id=item_id,
            cart__user=request.user
        )

        quantity = int(request.data.get("quantity"))

        if quantity <= 0:
            cart_item.delete()
            return Response(
                {"detail": "Item removed"},
                status=status.HTTP_204_NO_CONTENT
            )

        if cart_item.product.stock < quantity:
            return Response(
                {"detail": "Not enough stock"},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_item.quantity = quantity
        cart_item.save()
        return Response(
            {"detail": "Quantity updated"},
            status=status.HTTP_200_OK
        )

class RemoveFromCartView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, item_id):
        cart_item = get_object_or_404(
            CartItem,
            id=item_id,
            cart__user=request.user
        )
        cart_item.delete()
        return Response(
            {"detail": "Item removed"},
            status=status.HTTP_204_NO_CONTENT
        )

class PlaceOrderView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        cart = Cart.objects.filter(user=request.user).first()

        if not cart or not cart.items.exists():
            return Response(
                {"detail": "Cart is empty"},
                status=status.HTTP_400_BAD_REQUEST
            )

        total = 0
        order = Order.objects.create(
            user=request.user,
            total_amount=0
        )

        for item in cart.items.select_related("product"):
            product = item.product

            if product.stock < item.quantity:
                raise Exception(
                    f"Insufficient stock for {product.name}"
                )

            product.stock -= item.quantity
            product.save()

            OrderItem.objects.create(
                order=order,
                product=product,
                price=product.price,
                quantity=item.quantity
            )

            total += product.price * item.quantity

        order.total_amount = total
        order.save()

        # Clear cart
        cart.items.all().delete()

        return Response(
            {"detail": "Order placed successfully"},
            status=status.HTTP_201_CREATED
        )
