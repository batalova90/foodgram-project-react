from django_filters import rest_framework as r_f

from recipes.models import Recipe, Tag


class RecipeFilter(r_f.FilterSet):
    tags = r_f.filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )
    author = r_f.CharFilter(lookup_expr='exact')
    is_in_shopping_cart = r_f.BooleanFilter(
        field_name='is_in_shopping_cart',
        method='filter_shopping_cart'
    )
    is_favorited = r_f.BooleanFilter(
        field_name='is_favorited',
        method='filter_favorited'
    )

    def filter_shopping_cart(self, value):
        if value:
            queryset = Recipe.shopping_cart.filter(
                user__id=self.request.user.id
            )
            return queryset
        return Recipe.objects.all()

    def filter_favorited(self, value):
        if value:
            queryset = Recipe.favorites.filter(
                user__id=self.request.user.id
            )
            return queryset
        return Recipe.objects.all()

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_in_shopping_cart', 'is_favorited']
