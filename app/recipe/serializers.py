from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from core import models


class TagSerializer(ModelSerializer):
    """Serializer for Tag object"""

    class Meta:
        model = models.Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)


class IngredientSerializer(ModelSerializer):
    """Serializer for Ingredient object"""

    class Meta:
        model = models.Ingredient
        fields = ('id', 'name')
        read_only_fields = ('id',)


class RecipeSerializer(ModelSerializer):
    """Serializer for Recipe object"""
    ingredients = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=models.Ingredient.objects.all()
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=models.Tag.objects.all()
    )

    class Meta:
        model = models.Recipe
        fields = ('id', 'title', 'price', 'time_minutes', 'tags',
                  'ingredients', 'link')
        read_only_fields = ('id',)


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for detail data of recipe"""
    ingredients = IngredientSerializer(
        many=True,
        read_only=True
    )
    tags = TagSerializer(
        many=True,
        read_only=True
    )


class RecipeImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to recipe"""

    class Meta:
        model = models.Recipe
        fields = ('id', 'image')
        read_only_fields = ('id',)
