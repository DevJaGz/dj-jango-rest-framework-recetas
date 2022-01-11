from django.contrib.auth import get_user, get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

import tempfile
import os
from PIL import Image

RECIPES_URL = reverse("recipe:recipe-list")


def image_upload_url(recipe_id):
    """URL de retorno para imagen subida."""
    return reverse(
        "recipe:recipe-upload-image",
        args=[
            recipe_id,
        ],
    )


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

    def test_create_basic_recipe(self):
        """Testea para crear receta"""
        payload = {"title": "Test Recipe", "time_minutes": 30, "price": 10.00}

        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data["id"])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """Testea para crear receta con Tags"""
        tag1 = create_tag_sample(user=self.user, name="Tag 1")
        tag2 = create_tag_sample(user=self.user, name="Tag 2")

        payload = {
            "title": "Test Recipe",
            "time_minutes": 30,
            "price": 10.00,
            "tags": [tag1.id, tag2.id],
        }

        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data["id"])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """Testea para crear receta con Ingredients"""
        ingredient1 = create_ingredient_sample(user=self.user, name="Ingredient 1")
        ingredient2 = create_ingredient_sample(user=self.user, name="Ingredient 2")

        payload = {
            "title": "Test Recipe",
            "time_minutes": 30,
            "price": 10.00,
            "ingredients": [ingredient1.id, ingredient2.id],
        }

        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data["id"])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)


# class PrivateRecipeApiTests(TestCase):
#     """Testea acceso no autenticado a la API"""

#     def setUp(self):
#         self.client = APIClient()
#         self.user = get_user_model().objects.create_user("test@email.com", "tesdasdk")
#         self.client.force_authenticate(self.user)

#     def test_retrieve_recipes(self):
#       """Testea el obtener lista de recetas"""
#       create_recipe_sample(user=self.user)
#       create_recipe_sample(user=self.user)
#       res =self.client.get(RECIPES_URL)
#       recipes = Recipe.objects.get(id=res.data["id"])


class RecipeImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user("test@email.com", "tesdasdk")
        self.client.force_authenticate(self.user)
        self.recipe = create_recipe_sample(user=self.user)

    def tearDown(self):
        """Eliminar imagen"""
        self.recipe.image.delete()

    def test_upload_image_to_recipe(self):
        """Testea subir imagen a receta"""
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """Testea el fallar al subir imagen"""
        url = image_upload_url(self.recipe.id)
        res = self.client.post(url, {"image": "notImage"}, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_recipes_by_tags(self):
        """Testea filtrar recetas por tags"""
        recipe1 = create_recipe_sample(user=self.user, title="Thai Vegetable curry")
        recipe2 = create_recipe_sample(user=self.user, title="Aubergine with tahini")

        tag1 = create_tag_sample(user=self.user, name="Vegan")
        tag2 = create_tag_sample(user=self.user, name="Vegetarian")

        recipe1.tags.add(tag1)
        recipe2.tags.add(tag2)
        recipe3 = create_recipe_sample(user=self.user, title="Fish and chips")

        res = self.client.get(RECIPES_URL, {"tags": "{},{}".format(tag1.id, tag2.id)})

        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_recipes_by_ingredient(self):
        """Testea filtrar recetas por Ingredientes"""
        recipe1 = create_recipe_sample(user=self.user, title="Thai Vegetable curry")
        recipe2 = create_recipe_sample(user=self.user, title="Aubergine with tahini")

        ingredient1 = create_ingredient_sample(user=self.user, name="Vegan")
        ingredient2 = create_ingredient_sample(user=self.user, name="Vegetarian")

        recipe1.ingredients.add(ingredient1)
        recipe2.ingredients.add(ingredient2)
        recipe3 = create_recipe_sample(user=self.user, title="Fish and chips")

        res = self.client.get(
            RECIPES_URL, {"ingredients": "{},{}".format(ingredient1.id, ingredient2.id)}
        )

        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)
