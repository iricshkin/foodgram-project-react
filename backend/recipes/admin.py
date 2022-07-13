from django.contrib import admin
from.models import Ingredient, Tag


class IngredientAdmin(admin.ModelAdmin):
    """Админка ингредиента."""
    list_display = ('id', 'name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)


class TagAdmin(admin.ModelAdmin):
    """Админка тегов."""
    list_display = ('id', 'name', 'color', 'slug')
    list_filter = ('name',)
    search_fields = ('name',)


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
