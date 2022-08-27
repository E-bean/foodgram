from api.permissions import IsAdminOrSuperuserOrReadOnly
from api.serializers import TagSerializer
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import Tag


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.order_by("id")
    serializer_class = TagSerializer
    permission_classes = [
        IsAdminOrSuperuserOrReadOnly,
    ]
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name', )
