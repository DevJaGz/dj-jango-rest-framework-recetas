from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Ingredient
from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse("recipe:ingredient-list")


class PublicIngredientsApiTest(TestCase):
    """Probar API Ingredientes accesibles publicamente"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Testea que login es necesario para acceder al este endpoint"""
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PublicIngredientsApiTest(TestCase):
    """Probar API Ingredientes accesibles de forma privada"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user("test@email.com", "testpass123")
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients_list(self):
        """Testea obtener lista de ingredientes"""
        Ingredient.objects.create(user=self.user, name="Milk")
        Ingredient.objects.create(user=self.user, name="Cheese")
        res = self.client.get(INGREDIENTS_URL)
        ingredients = Ingredient.objects.all().order_by("-name")
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Testea retornar ingrediente solamente autenticados por el usuario"""

        user2 = get_user_model().objects.create_user("other@email.com", "password123434")
        Ingredient.objects.create(user=user2, name="Vinegar")
        ingredient = Ingredient.objects.create(user=self.user, name="tumeric")

        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], ingredient.name)
