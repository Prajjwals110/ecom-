from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from .models import Product
from .serializers import (
    ProductSerializer,
    ProductCreateUpdateSerializer
)
from .permissions import IsSellerOrReadOnly


class ProductViewSet(ModelViewSet):
    permission_classes = [IsSellerOrReadOnly]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter
    ]
    filterset_fields = ["category"]
    search_fields = ["name", "description"]
    ordering_fields = ["price", "created_at"]

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)

        user = self.request.user
        if user.is_authenticated and user.role == "seller":
            if self.action in ["update", "partial_update", "destroy"]:
                return queryset.filter(seller=user)

        return queryset

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ProductCreateUpdateSerializer
        return ProductSerializer

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()
