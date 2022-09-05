from api.views import IngredientViewSet, RecipeViewSet, TagViewSet, UserViewSet
# SubscribeViewSet
from django.urls import include, path
from rest_framework.authtoken import views
from rest_framework.routers import DefaultRouter

router_v1 = DefaultRouter()
router_v1.register('tags', TagViewSet, basename='tag')
router_v1.register('ingredients', IngredientViewSet, basename='ingredient')
router_v1.register('recipes', RecipeViewSet, basename='recipe')
router_v1.register('users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router_v1.urls)),
    # path('users/subscriptions/', SubscribeViewSet.as_view(
    #     {'get': 'list'}), name='subscriptions'
    # ),
    # path("users/<int:pk>/subscribe/", SubscribeViewSet.as_view(
    #     {'post': 'create', 'delete': 'destroy'}), name='subscribe'
    # ),
    # path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
