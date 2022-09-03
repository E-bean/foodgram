import base64

from django.core.files.base import ContentFile
from recipes.models import Ingredient, IngredientInRecipe, Recipe, Tag
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from users.models import User


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Ingredient


# class IngredientInRecipeSerializer(serializers.ModelSerializer):
#     name = serializers.StringRelatedField()
#     measurement_unit = serializers.StringRelatedField()
#     amount = serializers.StringRelatedField()

#     class Meta:
#         fields = ('id', 'name', 'measurement_unit', 'amount')
#         model = IngredientInRecipe
#         # fields = ('amount', )

#     # def get_amount(self, obj):
#     #     amount = IngredientInRecipe.objects.get(ingredient=obj, recipe=obj).amount
#     #     return amount


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())],
    )

    class Meta:
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
        )
        model = User


class UserForMeSerializer(UserSerializer):
    class Meta:
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
        )
        model = User


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(
        many=True
    )
    author = UserSerializer(
        read_only=True,
    )
    image = Base64ImageField()
    ingredients = IngredientSerializer(many=True,)

    class Meta:
        fields = '__all__'
        model = Recipe

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        ingredients = instance.ingredients.all()
        print(ingredients)
        print(instance)
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


class AmountSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    author = serializers.CurrentUserDefault()
    image = Base64ImageField()
    ingredients = AmountSerializer(many=True,)

    class Meta:
        fields = (
            'id', 'ingredients', 'tags', 'image', 'name', 'text', 'cooking_time'
        )
        model = Recipe

    def create(self, validate_data):
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

    def to_representation(self, instance):
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
