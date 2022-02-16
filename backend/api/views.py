import io

from django.db.models import Sum, Exists, OuterRef
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.models import User
from recipes.models import Favorites, Ingredient, Recipe, ShoppingCart, Tag
from .filters import RecipeFilter
from .permissions import IsAuthorOrReadOnly
from .paginations import CustomPageNumberPaginator
from .serializers import (CreateRecipeSerializer, FavoritesSerializer,
                          GetRecipeSerializer, IngredientSerializer,
                          NumberOfIngredients, ShoppingCartSerializer,
                          TagSerializer)


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
    pagination_class = CustomPageNumberPaginator

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return GetRecipeSerializer
        return CreateRecipeSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:
            return Recipe.objects.all()
        queryset = Recipe.objects.annotate(
            is_favorited=Exists(Favorites.objects.filter(
                user=user, recipe_id=OuterRef('pk'))),
            is_in_shopping_cart=Exists(ShoppingCart.objects.filter(
                user=user, recipe_id=OuterRef('pk'))))
        if self.request.GET.get('is_favorited'):
            return queryset.filter(is_favorited=True)
        elif self.request.GET.get('is_in_shopping_cart'):
            return queryset.filter(is_in_shopping_cart=True)
        return queryset

    @action(methods=['post', 'get'],
            detail=True,
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        user = get_object_or_404(User, pk=request.user.id)
        recipe = get_object_or_404(Recipe, pk=pk)
        data = {'user': user.id, 'recipe': recipe.id}
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
        ingredients = NumberOfIngredients.objects.filter(
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

    @action(methods=['get', 'post'],
            detail=True,
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        user = get_object_or_404(User, id=request.user.id)
        recipe = get_object_or_404(Recipe, id=pk)
        data = {'user': user.id,
                'recipe': recipe.id}
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
