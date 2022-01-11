from django.db import models

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    """Se encarga de proveer las funciones de ayuda para nuestra función de usuario principal"""

    def create_user(self, email, password=None, **extra_fields):
        """Crea y guarda nuevo usuario"""
        if not email:
            raise ValueError("Usuario debe tener un correo")
        user = self.model(email=email.lower(), password=password, **extra_fields)
        # Se utiliza con set_password para que la contraseña ingrese hasheada.
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Crea y guarda nuevo super usuario"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Modelo personalizado que soporta hacer Login con Email en vez de Usuario"""

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()
    USERNAME_FIELD = "email"
