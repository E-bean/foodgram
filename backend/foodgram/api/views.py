from api.permissions import IsAdminOrSuperuserOrReadOnly
from api.serializers import (CustomUserSerializer, IngredientSerializer,
                             RecipeCreateSerializer, RecipeSerializer,
                             ShortRecipeSerialaizer, SubscribeSerialaizer,
                             TagSerializer)
from django.shortcuts import get_list_or_404, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from recipes.models import Favorite, Ingredient, Recipe, Shopping_cart, Tag
from rest_framework import filters, permissions, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import (LimitOffsetPagination,
                                       PageNumberPagination)
from rest_framework.response import Response
from users.models import Subscribe, User


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.order_by('id')
    serializer_class = TagSerializer
    permission_classes = [
        IsAdminOrSuperuserOrReadOnly,
    ]
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name', )
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.order_by('id')
    serializer_class = IngredientSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.order_by('id')
    serializer_class = RecipeSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.action == 'list' or 'retrieve':
            return RecipeSerializer
        if self.action == 'create' or 'update':
            return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            )

    def perfome_update(self, serializer):
        serializer.save(
            author=self.request.user,
            )

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        permission_classes=(permissions.IsAuthenticated,),
        url_path='favorite'
    )
    def favorite(self, request, *args, **kwargs):
        recipe_id = kwargs.get("pk")
        recipe = get_object_or_404(Recipe, id=recipe_id)
        user = get_object_or_404(User, id=self.request.user.id)
        if request.method == 'POST':
            if Favorite.objects.filter(user=user, favorite=recipe).exists():
                return Response(
                    'Нельзя подписаться на самого себя.',
                    status=status.HTTP_400_BAD_REQUEST
                )
            Favorite.objects.create(user=user, favorite=recipe)
            serializer = ShortRecipeSerialaizer(
                recipe,
                context={'request': request},
                many=False
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            favorite = get_object_or_404(
                Favorite, user=user, favorite=recipe
            )
            favorite.delete()
            return Response(
                status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        permission_classes=(permissions.IsAuthenticated,),
        url_path='shopping_cart'
    )
    def shopping_cart(self, request, *args, **kwargs):
        recipe_id = kwargs.get("pk")
        recipe = get_object_or_404(Recipe, id=recipe_id)
        user = get_object_or_404(User, id=self.request.user.id)
        if request.method == 'POST':
            if Shopping_cart.objects.filter(user=user, purchase=recipe).exists():
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
                recipe_in_cart = Shopping_cart.objects.get(user=user, purchase=recipe)
            # recipe_in_cart = get_object_or_404(
            #     Shopping_cart, user=user, purchase=recipe
            # )
            except Shopping_cart.DoesNotExist:
                return Response(
                    'Такого рецепта не было в корзине.',
                    status=status.HTTP_400_BAD_REQUEST
                )
            recipe_in_cart.delete()
            return Response(
                status=status.HTTP_204_NO_CONTENT)


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = PageNumberPagination

    @action(
        detail=False,
        methods=["GET", ],
        permission_classes=(permissions.IsAuthenticatedOrReadOnly,),
    )
    def subscriptions(self, request, *args, **kwargs):
        user = self.request.user
        queryset = get_list_or_404(User, content_author__subscriber=user)
        serializer = SubscribeSerialaizer(
            queryset,
            context={'request': request},
            many=True)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscribe(self, request, *args, **kwargs):
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
            except serializers.ValidationError:
                return Response(
                    'Вы уже подписаны на этого автора.',
                    status=status.HTTP_400_BAD_REQUEST
                )
            subscribes = User.objects.filter(username=author)
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
