from rest_framework import generics, permissions, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Avg
from django_filters.rest_framework import DjangoFilterBackend

from .models import Recipe, RecipeFavorite, RecipeRating, RecipeComment
from .serializers import (
    RecipeListSerializer, RecipeDetailSerializer, 
    RecipeCreateUpdateSerializer, RecipeRatingSerializer,
    RecipeCommentSerializer
)


class RecipeListView(generics.ListAPIView):
    """List recipes with filtering and search"""
    serializer_class = RecipeListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'difficulty', 'author']
    search_fields = ['title', 'description', 'ingredients']
    ordering_fields = ['created_at', 'prep_time', 'cook_time']

    def get_queryset(self):
        return Recipe.objects.filter(is_published=True).select_related('author', 'category')

class RecipeDetailView(generics.RetrieveAPIView):
    """Get recipe details"""
    queryset = Recipe.objects.filter(is_published=True)
    serializer_class = RecipeDetailSerializer
    lookup_field = 'slug'
    permission_classes = [permissions.AllowAny]

class RecipeCreateView(generics.CreateAPIView):
    """Create new recipe"""
    serializer_class = RecipeCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user,is_published=True)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response({
            'recipe': response.data,
            'message': 'Recipe created successfully! 🎉'
        }, status=status.HTTP_201_CREATED)

class RecipeUpdateView(generics.UpdateAPIView):
    """Update recipe (only by author)"""
    serializer_class = RecipeCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'slug'

    def get_queryset(self):
        return Recipe.objects.filter(author=self.request.user)

class MyRecipesView(generics.ListAPIView):
    """List current user's recipes"""
    serializer_class = RecipeListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Recipe.objects.filter(author=self.request.user).select_related('category')

class RecipeDeleteView(generics.DestroyAPIView):
    """Delete a recipe (only by author)"""
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'slug'
    
    def get_queryset(self):
        return Recipe.objects.filter(author=self.request.user)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        recipe_title = instance.title
        self.perform_destroy(instance)
        return Response({
            'message': f'Recipe "{recipe_title}" was deleted successfully!',
            'deleted_recipe': {
                'id': instance.id,
                'title': recipe_title
            }
        }, status=status.HTTP_200_OK)

@api_view(['POST', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def toggle_favorite(request, recipe_id):
    """Add/remove recipe from favorites"""
    try:
        recipe = Recipe.objects.get(id=recipe_id, is_published=True)
    except Recipe.DoesNotExist:
        return Response({'error': 'Recipe not found'}, status=status.HTTP_404_NOT_FOUND)

    favorite, created = RecipeFavorite.objects.get_or_create(
        user=request.user, recipe=recipe
    )

    if created:
        return Response({
            'message': f'Added "{recipe.title}" to favorites! ❤️',
            'favorited': True
        })
    else:
        favorite.delete()
        return Response({
            'message': f'Removed "{recipe.title}" from favorites',
            'favorited': False
        })

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def favorite_recipes(request):
    """Get user's favorite recipes"""
    favorites = Recipe.objects.filter(
        favorites=request.user, 
        is_published=True
    ).select_related('author', 'category')
    
    serializer = RecipeListSerializer(favorites, many=True, context={'request': request})
    return Response({
        'recipes': serializer.data,
        'count': favorites.count(),
        'message': 'Your favorite recipes! ❤️'
    })

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def rate_recipe(request, recipe_id):
    """Rate a recipe"""
    try:
        recipe = Recipe.objects.get(id=recipe_id, is_published=True)
    except Recipe.DoesNotExist:
        return Response({'error': 'Recipe not found'}, status=status.HTTP_404_NOT_FOUND)

    rating, created = RecipeRating.objects.update_or_create(
        user=request.user, 
        recipe=recipe,
        defaults={
            'rating': request.data.get('rating'),
            'review': request.data.get('review', '')
        }
    )

    serializer = RecipeRatingSerializer(rating)
    action = 'added' if created else 'updated'
    
    return Response({
        'rating': serializer.data,
        'message': f'Rating {action} successfully! ⭐'
    })

@api_view(['GET'])
def featured_recipes(request):
    """Get featured recipes"""
    recipes = Recipe.objects.filter(
        is_published=True, 
        is_featured=True
    ).select_related('author', 'category')[:6]
    
    serializer = RecipeListSerializer(recipes, many=True, context={'request': request})
    return Response({
        'recipes': serializer.data,
        'message': 'Check out these featured recipes! 🌟'
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def comment_on_recipe(request, recipe_id):
    """Add a comment to a recipe"""
    try:
        recipe = Recipe.objects.get(id=recipe_id, is_published=True)
    except Recipe.DoesNotExist:
        return Response({'error': 'Recipe not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = RecipeCommentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(author=request.user, recipe=recipe)
        return Response({
            'comment': serializer.data,
            'message': 'Comment added successfully! 💬'
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)