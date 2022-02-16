from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import MethodNotAllowed

from recipes.models import (Favorites, Ingredient, NumberOfIngredients,
                            Recipe, ShoppingCart, Tag)
from users.serializers import UserSerializer

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class GetRecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'cooking_time',
        )

    def get_ingredients(self, obj):
        ingredients = NumberOfIngredients.objects.filter(recipe=obj)
        return NumberOfIngredientSerializer(ingredients,
                                            many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Favorites.objects.filter(user=request.user,
                                        recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=request.user,
                                           recipe=obj).exists()


class NumberOfIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
            source='ingredient.measurement_unit'
    )

    class Meta:
        model = NumberOfIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount')


class CreateIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
            queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField()

    class Meta:
        model = NumberOfIngredients
        fields = ('id', 'amount')


class CreateRecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    ingredients = CreateIngredientSerializer(many=True)
    author = UserSerializer(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'ingredients', 'tags',
            'image', 'name', 'text', 'cooking_time'
        )

    def validate(self, data):
        image = data.get('image')
        MAX_IMAGE_SIZE = 12000000
        if image is not None and image.size > MAX_IMAGE_SIZE:
            raise serializers.ValidationError({
                'image': 'Слишком большой размер файла!',
            })
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                'Выберите как минимум один ингредиент!',
            )
        ingredient_list = []
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            if ingredient_id in ingredient_list:
                raise serializers.ValidationError(
                    'Ингредиент уже был добавлен!',
                )
            ingredient_list.append(ingredient_id)
            amount = ingredient['amount']
            if int(amount) <= 0:
                raise serializers.ValidationError({
                    'amount': 'Введите необходимое кол-во ингредиента!',
                })
        tags = self.initial_data.get('tags')
        if not tags:
            raise serializers.ValidationError({
                'tags': 'Добавьте как минимум один тэг',
            })
        tags_list = []
        for tag_temp in tags:
            if tag_temp in tags_list:
                raise serializers.ValidationError({
                    'tags': 'Тэг уже был добавлен!'
                })
            tags_list.append(tag_temp)
        cooking_time = self.initial_data.get('cooking_time')
        if int(cooking_time) <= 0:
            raise serializers.ValidationError({
                'cooking_time': 'Введите время приготовление отличное от нуля!'
            })
        return data

    def create_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            amount = ingredient['amount']
            ingredient = Ingredient.objects.get(name=ingredient_id)
            NumberOfIngredients.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=amount
            )

    def create_tags(self, tags_id, recipe):
        for tag_id in tags_id:
            recipe.tags.add(tag_id)

    def create(self, validated_data):
        author = self.context.get('request').user
        tags_id = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author,
                                       **validated_data)
        self.create_tags(tags_id, recipe)
        self.create_ingredients(ingredients, recipe)
        print(recipe)
        return recipe

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request, }
        return GetRecipeSerializer(instance, context=context).data

    def update(self, instance, validated_data):
        if self.context['request'].method == 'PUT':
            raise MethodNotAllowed('PUT')
        instance.image = validated_data.get('image')
        instance.name = validated_data.get('name')
        instance.text = validated_data.get('text')
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.tags.clear()
        tags = validated_data.get('tags')
        self.create_tags(tags, instance)
        NumberOfIngredients.objects.filter(recipe=instance).all().delete()
        ingredients = validated_data.get('ingredients')
        self.create_ingredients(ingredients, instance)
        instance.save()
        return instance


class FavoritesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorites
        fields = ('user', 'recipe')

    def validate(self, data):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        recipe = data['recipe']
        if Favorites.objects.filter(user=request.user,
                                    recipe=recipe.id).exists():
            raise serializers.ValidationError({
                    'recipe': 'Рецепт уже был добавлен в избранное!'
            })
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeShoppingCartSerializer(instance.recipe,
                                            context=context).data


class RecipeShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def validate(self, data):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        recipe = data['recipe']
        if ShoppingCart.objects.filter(user=request.user,
                                       recipe__id=recipe.id).exists():
            raise serializers.ValidationError({
                'status': 'Рецепт уже добавлен!'
            })
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeShoppingCartSerializer(
            instance.recipe,
            context=context).data
