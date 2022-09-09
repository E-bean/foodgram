import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            Shopping_cart, Tag)
from users.models import Subscribe, User


class TagSerializer(serializers.ModelSerializer):
    """Сериалайзер для тегов"""
    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер для ингредиентов"""
    class Meta:
        fields = '__all__'
        model = Ingredient


class Base64ImageField(serializers.ImageField):
    """Сериалайзер для изображений"""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class CustomUserSerializer(UserSerializer):
    """Сериалайзер для пользователей"""
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())],
    )
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed"
        )
        model = User

    def get_is_subscribed(self, obj):
        auth = self.context.get('request').auth
        user = self.context.get('request').user
        if not auth:
            return False
        else:
            return Subscribe.objects.filter(
                subscriber=user, author=obj
            ).exists()


class RecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер для рецептов"""
    tags = TagSerializer(
        many=True
    )
    author = CustomUserSerializer(
        read_only=True,
    )
    image = Base64ImageField()
    ingredients = IngredientSerializer(many=True,)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = ('is_favorited', 'is_in_shopping_cart',
                  'id', 'tags', 'author', 'ingredients', 'image',
                  'name', 'text', 'cooking_time',)
        model = Recipe

    def to_representation(self, instance):
        """Изменение ответа при получении рецепта"""
        representation = super().to_representation(instance)
        ingredients = instance.ingredients.all()
        amount = instance.amounts.all()
        amount_list = []
        for i in range(len(amount)):
            i = {
                'id': ingredients[i].id,
                'name': ingredients[i].name,
                'measurement_unit': ingredients[i].measurement_unit,
                'amount': amount[i].amount
            }
            amount_list.append(i)
        representation['ingredients'] = amount_list
        return representation

    def get_is_favorited(self, obj):
        """Добавление рецепта в избранное"""
        auth = self.context.get('request').auth
        user = self.context.get('request').user
        if not auth:
            return False
        else:
            return Favorite.objects.filter(user=user, favorite=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        """Добавление рецепта в список покупок"""
        auth = self.context.get('request').auth
        user = self.context.get('request').user
        if not auth:
            return False
        else:
            return Shopping_cart.objects.filter(
                user=user, purchase=obj
            ).exists()


class AmountSerializer(serializers.ModelSerializer):
    """Сериалайзер для количества ингредиента"""
    id = serializers.IntegerField()
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериалайзер для создание рецепта"""
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = AmountSerializer(many=True,)

    class Meta:
        fields = (
            'id', 'tags', 'author', 'ingredients', 'image', 'name',
            'text', 'cooking_time'
        )
        model = Recipe

    def create(self, validate_data):
        """Создание рецепта"""
        tags = validate_data.pop('tags')
        ingredients = validate_data.pop('ingredients')
        recipe = Recipe.objects.create(
            **validate_data
        )
        for tag in tags:
            recipe.tags.add(tag)
        for value in ingredients:
            ingredient_id = value.get('id')
            ingredient = Ingredient.objects.get(pk=ingredient_id)
            amount = value.get('amount')
            IngredientInRecipe.objects.create(
                ingredient=ingredient, recipe=recipe, amount=amount
            )
        return recipe

    def update(self, instance, validate_data):
        """Обновление рецепта"""
        IngredientInRecipe.objects.filter(recipe=instance).delete()
        ingredients = validate_data.pop('ingredients')
        for value in ingredients:
            ingredient_id = value.get('id')
            ingredient = Ingredient.objects.get(pk=ingredient_id)
            amount = value.get('amount')
            IngredientInRecipe.objects.create(
                ingredient=ingredient, recipe=instance, amount=amount
            )
        return super().update(instance, validate_data)

    def to_representation(self, instance):
        """Изменение ответа при создании и обновлении рецепта"""
        data = super().to_representation(instance)
        data['tags'] = []
        data['ingredients'] = []
        tags_list = instance.tags.all()
        ingredient_recipe_qs = instance.ingredients.all()
        for tag in tags_list:
            tag_dict = {
                "id": tag.pk,
                "name": tag.name,
                "color": tag.color,
                "slug": tag.slug,
            }
            data['tags'].append(tag_dict)
        for ingredient in ingredient_recipe_qs:
            ingredient_dict = {
                "id": ingredient.pk,
                "name": ingredient.name,
                "measurement_unit": ingredient.measurement_unit,
                "amount": instance.amounts.get(ingredient=ingredient).amount
            }
            data['ingredients'].append(ingredient_dict)
        return data


class RecipeSubscribeSerialaizer(serializers.ModelSerializer):
    """Сериалайзер для представления рецепта в подписках"""
    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipe


class SubscribeSerialaizer(CustomUserSerializer):
    """Сериалайзер для подписок"""
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            'recipes',
            'recipes_count'
        )
        model = User

    def get_recipes(self, obj):
        """Получение поля рецепты"""
        queryset = Recipe.objects.filter(author_id=obj.id).order_by('id')
        return RecipeSubscribeSerialaizer(queryset, many=True).data

    def get_recipes_count(self, obj):
        """Получение поля количество рецептов"""
        return Recipe.objects.filter(author_id=obj.id).count()

    def get_is_subscribed(self, obj):
        """Получение поля наличия подписки"""
        auth = self.context.get('request').auth
        user = self.context.get('request').user
        if not auth:
            return False
        else:
            return Subscribe.objects.filter(
                subscriber=user, author=obj
            ).exists()


class ShortRecipeSerialaizer(serializers.ModelSerializer):
    """Сериалайзер рецепта с малым количеством полей"""
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
