from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token")
ME_URL = reverse("user:me")

print("CREATE_USER_URL ******: ", CREATE_USER_URL)
print("TOKEN_URL ******: ", TOKEN_URL)
print("ME_URL ******: ", ME_URL)


def create_user(**param):
    return get_user_model().objects.create_user(**param)


class PublicUserApiTests(TestCase):
    """Testear el API Pública del usuario"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Testea el crea usuario con un payload exitoso"""
        payload = {"email": "test@email.com", "password": "testPassword", "name": "Test Name"}
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload["password"]))
        self.assertNotIn("password", res.data)

    def test_user_exists(self):
        """Testea crear un usuario que ya exista (Debe fallar si existe)"""
        payload = {"email": "test@email.com", "password": "testPassword", "name": "Test Name"}
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Testea que La contraseña debe sea mayor a 5 caracteres"""
        payload = {"email": "test@email.com", "password": "pw", "name": "Test Name"}
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(email=payload["email"]).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """ "Testea que el token seea creado apra el usuario"""
        payload = {"email": "test@email.com", "password": "testPassword", "name": "Test Name"}
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)
        self.assertIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Testea que el token no es creado con credenciales inválidas"""
        create_user(email="test@email.com", password="testPassword")
        payload = {"email": "test@email.com", "password": "asdasd", "name": "Test Name"}
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Testea que el token no sea crea creado si no existe el usuario"""
        payload = {"email": "test@email.com", "password": "asdasd", "name": "Test Name"}
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Testea que el email y contraseña sea requerido"""
        payload = {"email": "badEmail", "password": "", "name": "Test Name"}
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorize(self):
        """Testea que la autenticación sea requerida"""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Testear el API Privado del usuario"""

    def setUp(self):
        self.user = create_user(email="test@email.com", password="testPassword", name="Name test")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Testear obtener perfil para usuario con login"""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {"name": self.user.name, "email": self.user.email})

    def test_post_me_not_allowed(self):
        """testea que el post no sea permitido"""
        res = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """testea que el usuario esta siendo actualizado si esta autenticado"""
        payload = {"name": "new name", "password": "password12334"}

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload["name"])
        self.assertTrue(self.user.check_password(payload["password"]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
