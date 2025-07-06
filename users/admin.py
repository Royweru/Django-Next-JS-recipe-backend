from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'recipes_count', 
                    'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Profile Info', {
            'fields': ('bio', 'profile_picture', 'location', 'website')
        }),
        ('Stats', {
            'fields': ('recipes_count',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('recipes_count','date_joined', 'last_login')

    def recipes_count(self, obj):
        count = obj.recipes_count
        if count > 0:
            return format_html(
                '<span style="color: green; font-weight: bold;">{}</span>', 
                count
            )
        return count
    recipes_count.short_description = "Recipes"