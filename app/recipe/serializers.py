from rest_framework import serializers

from core.models import Tag


class TagSerializer(serializers.ModelSerializer):
    """Serializing for tag object."""
    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_Fields = ('id')
