from rest_framework import serializers

from core.models import Tag, Ingredient, Recipe


class TagSerializer(serializers.ModelSerializer):
    """Serializing for tag object."""
    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_Fields = ('id')


class IngredientSerializer(serializers.ModelSerializer):
    """Serializing for ingredient object."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name',)
        read_only_Fields = ('id',)


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipe objects."""
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )

    ingredients = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'title', 'time_minutes', 'description', 'ingredients',
            'tags', 'price', 'link',
        )
        read_only_Fields = ('id',)


class RecipeDetailSerializer(RecipeSerializer):
    """Serialize a specific recipe."""
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientSerializer(many=True, read_only=True)


class RecipeImageSerializer(serializers.ModelSerializer):
    """Serilaizer for uploading images to recipe."""
    class Meta:
        model = Recipe
        fields = ('id', 'image')
        read_only_fields = ('id',)
