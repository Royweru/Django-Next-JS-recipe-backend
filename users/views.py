
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from .serializers import (
    UserRegistrationSerializer, 
    UserProfileSerializer, 
    UserUpdateSerializer
)

User = get_user_model()

class UserRegistrationView(generics.CreateAPIView):
    """Register new users"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            'user': UserProfileSerializer(user).data,
            'message': 'Registration successful! Welcome to RecipeApp!🎉'
        }, status=status.HTTP_201_CREATED)


class CustomTokenObtainPairView(TokenObtainPairView):
    pass

class CustomTokenRefreshView(TokenRefreshView):
    pass


class UserProfileView(generics.RetrieveUpdateAPIView):
    "Get user profile and update user details"
    queryset   = User.objects.all()
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserProfileSerializer
        return UserUpdateSerializer
    
    def get_object(self):
        return self.request.user
    
class UserDetailView(generics.RetrieveAPIView):
    "Get public user profile"
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    lookup_field = 'username'
    permission_classes = [permissions.AllowAny]
