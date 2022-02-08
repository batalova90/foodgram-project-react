from rest_framework import serializers
from .models import User, Follow
from djoser.serializers import (
        UserCreateSerializer as DjoserUserCreateSerializer,
        UserSerializer as DjoserUserSerializer
)
from recipes.models import Recipe


class UserSerializer(DjoserUserSerializer):

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, user):
        author = self.context['request'].user
        if author.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=author).exists()


class UserCreateSerializer(DjoserUserCreateSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'username',
            'email',
            'password'

        )


class SubscriptionsSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')

    def get_recipes(self, following):
        from api.serializers import RecipeShoppingCartSerializer
        request = self.context['request']
        limit = request.query_params.get('recipes_limit')
        qs = (following.recipes.all()[:int(limit)]
              if limit is not None
              else following.recipes.all())
        context = {'request': request}
        return RecipeShoppingCartSerializer(qs,
                                            many=True,
                                            context=context).data

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj.id).exists()

    def get_recipes_count(self, obj):
        counter = Recipe.objects.filter(author__username=obj).count()
        return counter


class CreateFollowSerializer(serializers.ModelSerializer):
    queryset = User.objects.all()
    user = serializers.PrimaryKeyRelatedField(queryset=queryset)
    author = serializers.PrimaryKeyRelatedField(queryset=queryset)

    class Meta:
        model = Follow
        fields = ('user', 'author')

    def validate(self, data):
        user = data['user']
        following = data['author']
        if user == following:
            raise serializers.ValidationError(
                    'На самого себя нельзя подписываться!')
        if Follow.objects.filter(
                author=following,
                user=user).exists():
            raise serializers.ValidationError(
                    'Вы уже подписаны на этого автора!')
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        instance_user = User.objects.get(username=instance)
        print(request.user)
        return ShowFollowSerializer(instance_user,
                                    context={'request': request}).data


class ShowFollowSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    recipe_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = UserSerializer.Meta.fields + ('recipes', 'recipe_count')

    def get_recipes(self, obj):
        from api.serializers import RecipeShoppingCartSerializer
        recipes = Recipe.objects.filter(author=obj)
        return RecipeShoppingCartSerializer(recipes, many=True).data

    def get_recipe_count(self, obj):
        queryset = Recipe.objects.filter(author=obj)
        return queryset.count()

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return Follow.objects.filter(author=obj,
                                     user=user).exists()
