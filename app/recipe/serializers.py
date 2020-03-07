from rest_framework.serializers import ModelSerializer
from core import models


class TagSerializer(ModelSerializer):
    """Serializer for Tag object"""

    class Meta:
        model = models.Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)
