from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):
    def setUp(self):
        """Función que corre antes de ejecutarse los tests"""
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            "admin@email.com", "password123"
        )
        # hacer que el usuario administrador haga login
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            "user@email.com", "userpassword123", name="Test User Nombre completo"
        )

    def test_users_listed(self):
        """Testear que los usuarios han sido enlistados en la página de usuario"""
        # reverse Genera la url para la lista de usuarios que tengamos
        # https://www.argpar.se/posts/programming/testing-django-admin
        # each admin url consits of the following three things
        # the app name, the name of the model and the name of the view
        url = reverse("admin:core_user_changelist")
        res = self.client.get(url)
        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_user_change_page(self):
        """ "Testea que la página editada por el usuario funciona"""
        url = reverse("admin:core_user_change", args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """Testear que la página de crear usuario se renderiza"""
        url = reverse("admin:core_user_add")
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
