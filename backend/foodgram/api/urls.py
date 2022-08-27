from api.views import TagViewSet
from django.urls import include, path
from rest_framework.authtoken import views
from rest_framework.routers import DefaultRouter

router_v1 = DefaultRouter()
router_v1.register('tags', TagViewSet, basename='tag')

urlpatterns = [
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
