from django.shortcuts import get_object_or_404
from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import LimitOffsetPagination
from recipes.models import Tag, Ingredient, Recipe, ShoppingCart, Favorites
from .serializers import (TagSerializer, IngredientSerializer,
                          GetRecipeSerializer, CreateRecipeSerializer,
                          ShoppingCartSerializer, FavoritesSerializer,
                          Number_of_Ingredients)
from .filters import RecipeFilter
from rest_framework import viewsets
from .permissions import IsAuthorOrReadOnly
from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from django.db.models import Sum


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (filters.SearchFilter, )
    search_fields = ('^name', )


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filter_class = RecipeFilter
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return GetRecipeSerializer
        return CreateRecipeSerializer

    @action(methods=['post', ],
            detail=True,
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        data = {'user': request.user.id, 'recipe': pk}
        serializer = ShoppingCartSerializer(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def delete_shoping_cart(self, request, pk):
        user = request.user
        try:
            recipe = get_object_or_404(Recipe, id=pk)
            shopping_cart = get_object_or_404(ShoppingCart,
                                              user=user,
                                              recipe=recipe)
            shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Http404:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        ingredients = Number_of_Ingredients.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(Sum('amount'))
        buf = io.BytesIO()
        c = canvas.Canvas(buf, bottomup=0)
        textob = c.beginText()
        textob.setTextOrigin(inch, inch)
        pdfmetrics.registerFont(TTFont('DejaVuSans',
                                       'DejaVuSans.ttf',
                                       'utf-8'))
        textob.setFont("DejaVuSans", 14)
        line_buf = ''
        for line in ingredients:
            line_buf = (line['ingredient__name'] +
                        ', ' + line['ingredient__measurement_unit'] +
                        ': ' + str(line['amount__sum']))
            textob.textLine(line_buf)
        c.drawText(textob)
        c.showPage()
        c.save()
        buf.seek(0)
        filename = f'shopping_cart {request.user}.pdf'
        return FileResponse(buf, as_attachment=True, filename=filename)

    @action(methods=['post', ],
            detail=True,
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        data = {'user': request.user.id,
                'recipe': pk}
        serializer = FavoritesSerializer(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        user = request.user
        try:
            recipe = get_object_or_404(Recipe, id=pk)
            favorite = get_object_or_404(Favorites,
                                         user=user,
                                         recipe=recipe)
            favorite.delete()
        except Http404:
            data = {"errors": "BAD_REQUEST"}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)
