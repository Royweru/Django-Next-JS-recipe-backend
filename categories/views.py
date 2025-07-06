from rest_framework import generics, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Category
from .serializers import CategorySerializer, CategoryDetailSerializer

class CategoryListView(generics.ListAPIView):
    """List all active categories"""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

class CategoryDetailView(generics.RetrieveAPIView):
    """Get category details with recent recipes"""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategoryDetailSerializer
    lookup_field = 'slug'
    permission_classes = [permissions.AllowAny]

@api_view(['GET'])
def featured_categories(request):
    """Get categories with most recipes"""
    categories = Category.objects.filter(is_active=True)[:6]
    serializer = CategorySerializer(categories, many=True, context={'request': request})
    return Response({
        'categories': serializer.data,
        'message': 'Explore these popular categories! 🍳'
    })

