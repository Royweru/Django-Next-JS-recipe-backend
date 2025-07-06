from django.urls import path
from . import views

urlpatterns = [
    path('', views.CategoryListView.as_view(), name='category-list'),
    path('featured/', views.featured_categories, name='featured-categories'),
    path('<slug:slug>/', views.CategoryDetailView.as_view(), name='category-detail'),
]
