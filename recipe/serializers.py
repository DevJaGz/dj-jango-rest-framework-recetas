from os import read
from rest_framework import serializers
from core.models import Tag, Ingredient, Recipe


class TagSerializer(serializers.ModelSerializer):
    """Serializador para el modelo del Tag"""

    class Meta:
        model = Tag
        fields = (
            "id",
            "name",
        )
        read_only_fields = ("id",)


class IngredientSerializer(serializers.ModelSerializer):
    """Serializador para el modelo del ingrediente"""

    class Meta:
        model = Ingredient
        fields = (
            "id",
            "name",
        )
        read_only_fields = ("id",)


class RecipeSerializer(serializers.ModelSerializer):
    """Serializador para el modelo del Recipe"""

    ingredients = serializers.PrimaryKeyRelatedField(many=True, queryset=Ingredient.objects.all())
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())

    class Meta:
        model = Recipe
        fields = ("id", "title", "ingredients", "tags", "time_minutes", "price", "link")
        read_only_fields = ("id",)


class RecipeDetailSerializer(RecipeSerializer):
    """Serializar detalles de la receta"""

    ingredients = IngredientSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)


class RecipeImageSerializer(serializers.ModelSerializer):
    """Serializar Imagenes"""

    class Meta:
        model = Recipe
        fields = ("id", "image")
        read_only_fields = ("id",)
