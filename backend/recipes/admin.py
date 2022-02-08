from django.contrib import admin
from .models import Tag, Ingredient, Recipe, Favorites, ShoppingCart


class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')
    search_fields = ('slug', )
    list_filter = ('slug', )
    empty_value_display = '-empty-'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    search_fields = ('name', )
    list_filter = ('name', )
    empty_value_display = '-empty-'


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'author', 'name', 'favorited_count')
    search_fields = ('name', )
    list_filter = ('author', 'name')
    empty_value_display = '-empty-'
    readonly_fields = ['favorited_count']

    def favorited_count(self, obj):
        return obj.favorites.count()


class FavoritesAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    search_fields = ('user', )
    list_filter = ('user', )
    empty_value_display = '-empty-'


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    search_fields = ('user', )
    list_filter = ('user', )
    empty_value_display = '-empty-'


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favorites, FavoritesAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
