from django.contrib import admin

from .models import (Favorites, Ingredient, IngredientForRecipe, Recipe,
                     ShoppingCart, Subscriptions, Tag, User)


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
    )
    search_fields = ('username', 'email', 'first_name', 'last_name',)
    list_filter = ('username', 'email',)
    empty_value_display = '-пусто-'


class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug',)
    empty_value_display = '<пусто>'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit',)
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'favorites_amount',)
    search_fields = ('name', 'author',)
    list_filter = ('name', 'author', 'tags',)
    empty_value_display = '-пусто-'

    """Количество добавления рецепта в избранное."""

    def favorites_amount(self, obj):
        return obj.favorites.count()


class RecipeIngredientInline(admin.TabularInline):
    model = IngredientForRecipe


admin.site.register(User, UserAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Subscriptions)
admin.site.register(ShoppingCart)
admin.site.register(Favorites)
