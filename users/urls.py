
from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('register/', views.UserRegistrationView.as_view(), name='user-register'),
    path('login/', views.CustomTokenObtainPairView.as_view(), name='user-login'),
    path('refresh/token/', views.CustomTokenRefreshView.as_view(), name='refresh-token'),
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('users/<str:username>/', views.UserDetailView.as_view(), name='user-detail'),
]
