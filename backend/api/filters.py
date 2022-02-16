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
        method='filter'
    )
    is_favorited = r_f.BooleanFilter(
        field_name='is_favorited',
        method='filter'
    )

    def filter(self, queryset, name, value):
        if name == 'is_in_shopping_cart' and value:
            queryset = queryset.filter(
                shopping_cart__user=self.request.user
            )
        return queryset

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_in_shopping_cart', 'is_favorited']
