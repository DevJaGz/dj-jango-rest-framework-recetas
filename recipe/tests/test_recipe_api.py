from django.contrib.auth import get_user, get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPES_URL = reverse("recipe:recipe-list")


def create_tag_sample(user, name="Main Course"):
    """Crear y retornar tag"""
    return Tag.objects.create(user=user, name=name)


def create_ingredient_sample(user, name="Cinnamon"):
    """Crear y retornar ingrediente"""
    return Ingredient.objects.create(user=user, name=name)


def detail_url(recipe_id):
    """Retorna Receta Detail URL"""
    return reverse(
        "recipe:recipe-detail",
        args=[
            recipe_id,
        ],
    )


def create_recipe_sample(user, **params):
    """Crear y retornar receta"""
    defaults = {"title": "Sample recipe", "time_minutes": 10, "price": 5.00}
    defaults.update(params)
    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTests(TestCase):
    """Testea acceso no autenticado a la API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user("test@email.com", "tesdasdk")
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Testea obtener lista de recetas"""
        create_recipe_sample(user=self.user)
        create_recipe_sample(user=self.user)

        res = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.all().order_by("id")
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """Testea obtener receta para usuario"""
        user2 = get_user_model().objects.create_user("test2@email.com", "t22esdasdk")
        create_recipe_sample(user=user2)
        create_recipe_sample(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_detail(self):
        """Testea el ver los detalles de una receta"""
        recipe = create_recipe_sample(user=self.user)
        recipe.tags.add(create_tag_sample(user=self.user))
        recipe.ingredients.add(create_ingredient_sample(user=self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)


# class PrivateRecipeApiTests(TestCase):
#     """Testea acceso no autenticado a la API"""

#     def setUp(self):
#         self.client = APIClient()
#         self.user = get_user_model().objects.create_user("test@email.com", "tesdasdk")
#         self.client.force_authenticate(self.user)