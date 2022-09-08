from django.contrib import admin
from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            Shopping_cart, Tag)


class IngredientsInLine(admin.TabularInline):
    model = IngredientInRecipe
    extra = 1


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    empty_value_display = '-пусто-'
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color')
    empty_value_display = '-пусто-'
    search_fields = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'author', 'favorite_count'
    )
    list_filter = ('name', 'author', 'tags')
    inlines = (IngredientsInLine, )

    @admin.display(
        description='Количество добавлений в избранное',
    )
    def favorite_count(self, obj):
        return Favorite.objects.filter(favorite=obj).count()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'favorite'
    )


@admin.register(Shopping_cart)
class Shopping_cartAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'purchase'
    )
