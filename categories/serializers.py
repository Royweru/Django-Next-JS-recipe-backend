from rest_framework import serializers
from .models import Category

class CategorySerializer(serializers.ModelSerializer):
    """Basic category serializer"""
    recipes_count = serializers.ReadOnlyField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'description', 'image', 
                  'recipes_count', 'created_at')
        read_only_fields = ('id', 'slug', 'created_at')

class CategoryDetailSerializer(serializers.ModelSerializer):
    """Detailed category serializer with recent recipes"""
    recent_recipes = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'description', 'image', 
                  'recipes_count', 'recent_recipes', 'created_at')
        read_only_fields = ('id', 'slug', 'created_at')

    def get_recent_recipes(self, obj):
        request = self.context.get('request')
        recent_recipes = obj.recipes.filter(is_published=True).order_by('-created_at')[:5]
        from recipes.serializers import RecipeListSerializer
        return RecipeListSerializer(recent_recipes, many=True, context={'request': request}).data