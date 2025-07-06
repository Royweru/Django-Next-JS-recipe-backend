from django.urls import path
from . import views

urlpatterns = [
    path('', views.RecipeListView.as_view(), name='recipe-list'),
    path('create/', views.RecipeCreateView.as_view(), name='recipe-create'),
    path('my-recipes/', views.MyRecipesView.as_view(), name='my-recipes'),
    path('favorites/', views.favorite_recipes, name='favorite-recipes'),
    path('featured/', views.featured_recipes, name='featured-recipes'),
    
    path('<slug:slug>/', views.RecipeDetailView.as_view(), name='recipe-detail'),
    path('<slug:slug>/update/', views.RecipeUpdateView.as_view(), name='recipe-update'),
    path('<slug:slug>/delete/', views.RecipeDeleteView.as_view(), name='recipe-delete'),
    path('<int:recipe_id>/comment/', views.comment_on_recipe, name='comment-on-recipe'),
    path('<int:recipe_id>/favorite/', views.toggle_favorite, name='toggle-favorite'),
    path('<int:recipe_id>/rate/', views.rate_recipe, name='rate-recipe'),
]
