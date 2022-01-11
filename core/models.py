from django.db import models

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

from django.conf import settings

import uuid
import os


def recipe_image_file_path(intance, filename):
    """Genera Path para imagenes"""
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"

    return os.path.join("uploads/recipe/", filename)


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


class Tag(models.Model):
    """Modelo del Tag para la receta"""

    name = models.CharField(max_length=255)
    # on_delete=models.CASCADE = Si se borra el usuario todos los tags van a borrarse
    # Automáticamente se crea como user_id
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Modelo del Ingrediente para la receta"""

    name = models.CharField(max_length=255)
    # on_delete=models.CASCADE = Si se borra el usuario todos los tags van a borrarse
    # Automáticamente se crea como user_id
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Modelo para receta"""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)
    ingredients = models.ManyToManyField("Ingredient")
    tags = models.ManyToManyField("Tag")
    image = models.ImageField(null=True, upload_to=recipe_image_file_path)

    def __str__(self):
        return self.title
