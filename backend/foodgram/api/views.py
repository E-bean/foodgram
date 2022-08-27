from api.serializers import TagSerializer
from api.permissions import IsAdminOrSuperuserOrReadOnly
from recipes.models import Tag
from django_filters.rest_framework import DjangoFilterBackend


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.order_by("id")
    serializer_class = TagSerializer
    permission_classes = [
        IsAdminOrSuperuserOrReadOnly,
    ]
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name', )
