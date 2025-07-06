from rest_framework import serializers
from .models import Recipe, RecipeFavorite, RecipeRating, RecipeComment
from users.serializers import UserProfileSerializer
from categories.serializers import CategorySerializer

class RecipeListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for recipe lists"""
    author = serializers.StringRelatedField()
    category = serializers.SerializerMethodField() #Changed this from a string related field to a serializer method field
    average_rating = serializers.ReadOnlyField()
    favorite_count = serializers.ReadOnlyField()
    comment_count = serializers.SerializerMethodField()  
    comments = serializers.SerializerMethodField()
    class Meta:
        model = Recipe
        fields = ('id', 'title', 'slug', 'description', 'author', 'category',
                 'prep_time', 'cook_time', 'total_time', 'difficulty','comments',
                 'featured_image', 'ingredients', 'instructions', 'tips',
                 'average_rating', 'rating_count', 'favorite_count','comment_count',
                  'is_published', 'is_featured','favorites',
                 'created_at', 'updated_at')

   
    def get_category(self,obj):
        return{
            'id': obj.category.id,
            'name': obj.category.name,
            'slug': obj.category.slug 
        }
    def get_comments(self, obj):
        # Get top-level comments (comments with no parent)
        comments = obj.comments.filter(parent__isnull=True)
        return RecipeCommentSerializer(
            comments, 
            many=True, 
            context=self.context
        ).data
    def get_comment_count(self, obj):
        return obj.comments.count()

class RecipeDetailSerializer(serializers.ModelSerializer):
    """Complete recipe details"""
    author = UserProfileSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    average_rating = serializers.ReadOnlyField()
    rating_count = serializers.ReadOnlyField()
    favorite_count = serializers.ReadOnlyField()
    total_time = serializers.ReadOnlyField()
    is_favorited = serializers.SerializerMethodField()
    user_rating = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'title', 'slug', 'description', 'author', 'category',
                 'prep_time', 'cook_time', 'total_time', 'difficulty',
                 'featured_image', 'ingredients', 'instructions', 'tips',
                 'average_rating', 'rating_count', 'favorite_count',
                 'is_favorited', 'user_rating', 'is_published', 'is_featured',
                 'created_at', 'updated_at')

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorites.filter(id=request.user.id).exists()
        return False

    def get_user_rating(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            rating = obj.ratings.filter(user=request.user).first()
            return rating.rating if rating else None
        return None

class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """For creating and updating recipes"""
    class Meta:
        model = Recipe
        fields = ('title', 'description', 'category', 'prep_time', 'cook_time',
                 'difficulty', 'featured_image', 'ingredients', 'instructions', 
                 'tips', 'is_published')

    def validate_prep_time(self, value):
        if value <= 0:
            raise serializers.ValidationError("Prep time must be positive!")
        return value

    def validate_cook_time(self, value):
        if value <= 0:
            raise serializers.ValidationError("Cook time must be positive!")
        return value

class RecipeDeleteSerializer(serializers.ModelSerializer):
    """Simple serializer for recipe deletion confirmation"""
    class Meta:
        model = Recipe
        fields = ('id', 'title')  # Only need basic info for deletion confirmation
        
class RecipeRatingSerializer(serializers.ModelSerializer):
    """For rating recipes"""
    user = UserProfileSerializer(read_only=True)

    class Meta:
        model = RecipeRating
        fields = ('id', 'user', 'rating', 'review', 'created_at', 'updated_at')
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')

class RecipeCommentSerializer(serializers.ModelSerializer):
    """For recipe comments"""
    author = UserProfileSerializer(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = RecipeComment
        fields = ('id', 'author', 'content', 'parent', 'replies', 
                 'created_at', 'updated_at')
        read_only_fields = ('id', 'author', 'created_at', 'updated_at')

    def get_replies(self, obj):
        if obj.replies.exists():
            return RecipeCommentSerializer(obj.replies.all(), many=True).data
        return []
