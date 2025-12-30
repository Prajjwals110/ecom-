from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import User
from .serializers import UserSerializer
from .permissions import IsAdmin


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.filter(is_active=True)

    def get_permissions(self):
        # Admin can list all users
        if self.action == "list":
            return [IsAdmin()]

        # Authenticated users only
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user

        # Admin → all users
        if user.is_staff or user.role == "admin":
            return User.objects.filter(is_active=True)

        # Normal user → only self
        return User.objects.filter(id=user.id, is_active=True)

    @action(detail=False, methods=["get"])
    def me(self, request):
        """Return logged-in user profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=["delete"])
    def delete_me(self, request):
        """Soft delete own account"""
        request.user.is_active = True
        request.user.save()
        return Response(
            {"detail": "Account deleted"},
            status=status.HTTP_204_NO_CONTENT,
        )
