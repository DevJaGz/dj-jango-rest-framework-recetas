from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core.models import Tag, Ingredient
from recipe import serializers


class TagViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    """Manejar Tags en base de datos"""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer

    def get_queryset(self):
        """Retornan objetos para el usuario autenticado"""
        return self.queryset.filter(user=self.request.user).order_by("-name")


class IngredientViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    """Manejar Ingredientes en base de datos"""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer

    def get_queryset(self):
        """Retornan objetos para el usuario autenticado"""
        return self.queryset.filter(user=self.request.user).order_by("-name")