from django.db import IntegrityError
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.filter import IngredientSearchFilter
from api.pagination import CustomPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (CustomUserSerializer, IngredientSerializer,
                             RecipeCreateSerializer, RecipeSerializer,
                             ShortRecipeSerialaizer, SubscribeSerialaizer,
                             TagSerializer)
from foodgram.settings import MEDIA_ROOT
from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            Shopping_cart, Tag)
from users.models import Subscribe, User


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для обработки тэгов"""
    queryset = Tag.objects.order_by('id').order_by('id')
    serializer_class = TagSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name', )
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для обработки ингредиентов"""
    queryset = Ingredient.objects.order_by('id')
    serializer_class = IngredientSerializer
    filter_backends = [IngredientSearchFilter]
    search_fields = ("^name",)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для обработки рецептов"""
    queryset = Recipe.objects.order_by('id')
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = CustomPagination

    def get_queryset(self):
        """Получение списка объектов"""
        queryset = Recipe.objects.all().order_by('id')
        user = self.request.user
        is_favorited = self.request.query_params.get('is_favorited')
        author_id = self.request.query_params.get('author')
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart'
        )
        tags = self.request.query_params.getlist('tags')
        if is_favorited is not None:
            queryset = Recipe.objects.filter(
                favorite__user=user
            ).order_by('id')
        if author_id is not None:
            queryset = queryset.filter(author=author_id).order_by('id')
        if is_in_shopping_cart is not None:
            queryset = queryset.filter(cart__user=user).order_by('id')
        if tags is not None:
            for tag in tags:
                tag_filter = Tag.objects.get(slug=tag)
                queryset = queryset.filter(tags=tag_filter).order_by('id')
        return queryset

    def get_serializer_class(self):
        """Выбор сериалайзера"""
        if self.action in ('create', 'partial_update'):
            return RecipeCreateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        """Обработка запроса создания рецепта"""
        serializer.save(
            author=self.request.user,
        )

    def perfome_update(self, serializer):
        """Обработка запроса обновления рецепта"""
        serializer.save(
            author=self.request.user,
        )

    @action(
        detail=False,
        methods=["GET", ],
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request, *args, **kwargs):
        """Скачивание файла покупок"""
        queryset = Recipe.objects.all()
        user = request.user
        queryset = queryset.filter(cart__user=user).order_by('id')
        shoppingcart = {}
        for recipe in queryset:
            ingredients = Ingredient.objects.all().filter(recipes=recipe)
            for ingredient in ingredients:
                amount = IngredientInRecipe.objects.get(
                    recipe=recipe,
                    ingredient=ingredient
                ).amount
                if shoppingcart.get(ingredient) is not None:
                    shoppingcart[ingredient] += amount
                else:
                    shoppingcart[ingredient] = amount
        username = user.username
        filename = f'{username}.txt'
        with open(f'{MEDIA_ROOT}/{filename}', 'w', encoding="utf-8") as file:
            for i in shoppingcart.keys():
                s = f'{i.name} ({i.measurement_unit}) - {shoppingcart[i]}'
                print(s, file=file)
        return FileResponse(
            open(f'{MEDIA_ROOT}/{filename}', 'rb')
        )

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        permission_classes=(IsAuthenticated,),
        url_path='favorite'
    )
    def favorite(self, request, *args, **kwargs):
        """Добавление/удаление избранного рецепта """
        recipe_id = kwargs.get("pk")
        recipe = get_object_or_404(Recipe, id=recipe_id)
        user = get_object_or_404(User, id=self.request.user.id)
        if request.method == 'POST':
            if Favorite.objects.filter(user=user, favorite=recipe).exists():
                return Response(
                    'Рецепт уже добавлен в избранное.',
                    status=status.HTTP_400_BAD_REQUEST
                )
            Favorite.objects.create(user=user, favorite=recipe)
            serializer = ShortRecipeSerialaizer(
                recipe,
                context={'request': request},
                many=False
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if not Favorite.objects.filter(
                user=user, favorite=recipe
            ).exists():
                return Response(
                    'Рецепта нет в избранном.',
                    status=status.HTTP_400_BAD_REQUEST
                )
            favorite = Favorite.objects.get(user=user, favorite=recipe)
            favorite.delete()
            return Response(
                status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        permission_classes=(IsAuthenticated,),
        url_path='shopping_cart'
    )
    def shopping_cart(self, request, *args, **kwargs):
        """Добавление/удаление в список покупок"""
        recipe_id = kwargs.get("pk")
        recipe = get_object_or_404(Recipe, id=recipe_id)
        user = get_object_or_404(User, id=self.request.user.id)
        if request.method == 'POST':
            if Shopping_cart.objects.filter(
                user=user, purchase=recipe
            ).exists():
                return Response(
                    'Рецепт уже добавлен в корзину.',
                    status=status.HTTP_400_BAD_REQUEST
                )
            Shopping_cart.objects.create(user=user, purchase=recipe)
            serializer = ShortRecipeSerialaizer(
                recipe,
                context={'request': request},
                many=False
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            try:
                recipe_in_cart = Shopping_cart.objects.get(
                    user=user, purchase=recipe
                )
            except Shopping_cart.DoesNotExist:
                return Response(
                    'Такого рецепта не было в корзине.',
                    status=status.HTTP_400_BAD_REQUEST
                )
            recipe_in_cart.delete()
            return Response(
                status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserViewSet(DjoserUserViewSet):
    """Вьюсет для обработки рецептов"""
    queryset = User.objects.all().order_by('id')
    serializer_class = CustomUserSerializer
    pagination_class = CustomPagination

    @action(
        detail=False,
        methods=["GET", ],
        permission_classes=(permissions.IsAuthenticated,),
    )
    def me(self, request):
        """Метод для адреса users/me """
        user = self.request.user
        serializer = CustomUserSerializer(
            user,
            context={'request': request},
        )
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["GET", ],
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request, *args, **kwargs):
        """Получение списка подписок"""
        user = self.request.user
        queryset = User.objects.filter(
            content_author__subscriber=user
        ).order_by('id')
        self.paginate_queryset(queryset)
        serializer = SubscribeSerialaizer(
            queryset,
            context={'request': request},
            many=True)
        data = serializer.data
        return self.get_paginated_response(data)

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, *args, **kwargs):
        """Подписка/отписка на автора """
        author_id = kwargs.get("id")
        author = get_object_or_404(User, id=author_id)
        subscriber = get_object_or_404(User, id=self.request.user.id)
        if request.method == 'POST':
            if author.id == subscriber.id:
                return Response(
                    'Нельзя подписаться на самого себя.',
                    status=status.HTTP_400_BAD_REQUEST
                )
            try:
                Subscribe.objects.create(author=author, subscriber=subscriber)
            except IntegrityError:
                return Response(
                    'Вы уже подписаны на этого автора.',
                    status=status.HTTP_400_BAD_REQUEST
                )
            subscribes = User.objects.filter(username=author.username)
            serializer = SubscribeSerialaizer(
                subscribes,
                context={'request': request},
                many=True
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            subscribe = get_object_or_404(
                Subscribe, author=author, subscriber=subscriber
            )
            subscribe.delete()
            return Response(
                status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
