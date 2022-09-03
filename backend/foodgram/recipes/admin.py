from django.contrib import admin
from recipes.models import Ingredient, IngredientInRecipe, Recipe, Tag


class IngredientsInLine(admin.TabularInline):
    model = IngredientInRecipe
    extra = 1


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    empty_value_display = '-пусто-'
    search_fields = ('name',)
    list_editable = ('measurement_unit',)
    list_filter = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color')
    empty_value_display = '-пусто-'
    search_fields = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'author',
    )
    list_filter = ('name', 'author', 'tags')
    inlines = (IngredientsInLine, )
