from django.test import TestCase
from django.contrib.auth import get_user_model


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
