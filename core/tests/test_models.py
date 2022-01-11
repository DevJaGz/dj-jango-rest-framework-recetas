from core import models
from django.test import TestCase
from django.contrib.auth import get_user_model

from unittest.mock import patch


def sample_user(email="test@email.com", password="testpass"):
    """Crea un usuario de ejemplo"""
    return get_user_model().objects.create_user(email, password)


class ModelTest(TestCase):
    def test_create_user_with_email_successful(self):
        """Testea la creación de nuevo usuario con email"""
        email = "test@email.co"
        password = "TestPassword123"
        user = get_user_model().objects.create_user(email, password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Testea email normalizado para nuevo usuario"""
        email = "TesT@EMAIL.co"
        user = get_user_model().objects.create_user(email, "TestPass123")
        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Testea Nuevo usuario Email Invalido"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, "TestPass123")

    def test_create_new_super_user(self):
        """Testea la creación de Nuevo Super usuario"""
        email = "test@email.co"
        password = "TestPassword123"
        user = get_user_model().objects.create_superuser(email=email, password=password)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Testea la representación de string del tag"""
        tag = models.Tag.objects.create(user=sample_user(), name="Meat")
        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """Testea la representación de string del ingrediente"""
        ingredient = models.Ingredient.objects.create(user=sample_user(), name="Banana")
        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        """Testea la representación de string del ingrediente"""
        recipe = models.Recipe.objects.create(
            user=sample_user(), title="Steal and mushrrom sauce", time_minutes=5, price=5.00
        )
        self.assertEqual(str(recipe), recipe.title)

    @patch("uuid.uuid4")
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Testea que la imagen ha sido guardad en el lugar correcto"""
        uuid = "test-uuid"
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, "myimage.jpg")

        exp_path = f"uploads/recipe/{uuid}.jpg"
        self.assertEqual(file_path, exp_path)
