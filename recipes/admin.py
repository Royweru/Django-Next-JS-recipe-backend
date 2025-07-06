from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Avg
from .models import Recipe, RecipeFavorite, RecipeRating, RecipeComment

class RecipeRatingInline(admin.TabularInline):
    model = RecipeRating
    extra = 0
    readonly_fields = ('user', 'rating', 'created_at')

class RecipeCommentInline(admin.TabularInline):
    model = RecipeComment
    extra = 0
    readonly_fields = ('author', 'created_at')
    fields = ('author', 'content', 'is_approved', 'created_at')

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'difficulty', 
                   'total_time_display', 'rating_display', 'favorite_count',
                   'is_published', 'is_featured', 'created_at')
    list_filter = ('difficulty', 'category', 'is_published', 'is_featured', 
                  'created_at', 'author')
    search_fields = ('title', 'description', 'ingredients', 'instructions')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_published', 'is_featured')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    inlines = [RecipeRatingInline, RecipeCommentInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'author', 'category')
        }),
        ('Recipe Details', {
            'fields': ('prep_time', 'cook_time', 'difficulty', 'featured_image')
        }),
        ('Content', {
            'fields': ('ingredients', 'instructions', 'tips'),
            'classes': ('wide',)
        }),
        ('Status', {
            'fields': ('is_published', 'is_featured')
        }),
        ('Statistics', {
            'fields': ('favorite_count', 'average_rating', 'rating_count'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ('favorite_count', 'average_rating', 'rating_count')

    def total_time_display(self, obj):
        total = obj.total_time
        if total > 120:  # More than 2 hours
            return format_html(
                '<span style="color: red;">{} min</span>', total
            )
        elif total > 60:  # More than 1 hour
            return format_html(
                '<span style="color: orange;">{} min</span>', total
            )
        return format_html(
            '<span style="color: green;">{} min</span>', total
        )
    total_time_display.short_description = "Total Time"

    def rating_display(self, obj):
        rating = obj.average_rating
        if rating >= 4:
            color = "green"
            stars = "⭐⭐⭐⭐⭐"
        elif rating >= 3:
            color = "orange" 
            stars = "⭐⭐⭐⭐"
        elif rating >= 2:
            color = "red"
            stars = "⭐⭐⭐"
        elif rating >= 1:
            color = "gray"
            stars = "⭐⭐"
        else:
            color = "red"
            stars = "⭐"
        
        return format_html(
            '<span style="color: {};">{} {}</span>',
            color, rating, stars
        )
    rating_display.short_description = "Rating"

@admin.register(RecipeRating)
class RecipeRatingAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('recipe__title', 'user__username', 'review')
    ordering = ('-created_at',)

@admin.register(RecipeComment)
class RecipeCommentAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'author', 'content_preview', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('recipe__title', 'author__username', 'content')
    list_editable = ('is_approved',)
    ordering = ('-created_at',)

    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = "Content Preview"

@admin.register(RecipeFavorite)
class RecipeFavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'recipe__title')
    ordering = ('-created_at',)
