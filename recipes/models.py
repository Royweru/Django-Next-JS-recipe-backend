from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from PIL import Image
import os

User = get_user_model()

class Recipe(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

 
    # Basic Information
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True)
    description = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes')
    category = models.ForeignKey(
        'categories.Category', 
        on_delete=models.CASCADE, 
        related_name='recipes'
    )
    
    # Recipe Details
    prep_time = models.PositiveIntegerField(help_text="Preparation time in minutes")
    cook_time = models.PositiveIntegerField(help_text="Cooking time in minutes")
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
   
   
    
    # Images
    featured_image = models.ImageField(upload_to='recipes/featured/', blank=True)
    
    # Content
    ingredients = models.TextField()
    instructions = models.TextField()
    tips = models.TextField(blank=True,null=True)
    
    # Engagement
    favorites = models.ManyToManyField(
        User, 
        through='RecipeFavorite', 
        related_name='favorite_recipes'
    )
    
    # Status and Metadata
    is_published = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
        
        # Resize featured image
        if self.featured_image:
            img = Image.open(self.featured_image.path)
            if img.height > 800 or img.width > 800:
                output_size = (800, 800)
                img.thumbnail(output_size)
                img.save(self.featured_image.path)

    def __str__(self):
        return self.title

    @property
    def total_time(self):
        return self.prep_time + self.cook_time

    @property
    def average_rating(self):
        ratings = self.ratings.all()
        if ratings:
            return sum(rating.rating for rating in ratings) / len(ratings)
        return 0

    @property
    def rating_count(self):
        return self.ratings.count()

    @property
    def favorite_count(self):
        return self.favorites.count()

class RecipeFavorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'recipe')

    def __str__(self):
        return f"{self.user.username} ♥ {self.recipe.title}"

class RecipeRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,      related_name='ratings')
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    review = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'recipe')

    def __str__(self):
        return f"{self.user.username} rated {self.recipe.title}: {self.rating}/5"

class RecipeComment(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True, 
        related_name='replies'
    )
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author.username} on {self.recipe.title}"

