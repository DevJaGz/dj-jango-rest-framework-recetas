from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from user.serializers import UserSerializer, AuthTokenSerializer

from rest_framework.settings import api_settings


class CreateUserView(generics.CreateAPIView):
    """Crear nuevo usuario en el sistema."""

    serializer_class = UserSerializer


class CreateTokeView(ObtainAuthToken):
    """Crear nuevo auth token para el usuario"""

    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Maneja el usuario autenticado"""

    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """Obtener y retornar usuario autenticado"""
        return self.request.user
