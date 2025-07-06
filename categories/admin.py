from django.contrib import admin
from django.utils.html import format_html
from .models import Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'recipes_count', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}  # Fixed: Added comma after 'name'
    list_editable = ('is_active',)
    ordering = ('name',)
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Appearance', {
            'fields': ('image',)  # Fixed: Proper single-item tuple
        }),
        ('Settings', {
            'fields': ('is_active',)  # Fixed: Proper single-item tuple
        }),
        ('Stats', {
            'fields': ('recipes_count',),  # Fixed: Proper single-item tuple
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('recipes_count',)

    def recipes_count(self, obj):
        count = obj.recipes_count
        if count > 10:
            color = "green"
        elif count > 5:
            color = "orange"
        else:
            color = "red"
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} recipes</span>',
            color,
            count
        )
    recipes_count.short_description = "Recipe Count"  # Fixed: Removed trailing comma