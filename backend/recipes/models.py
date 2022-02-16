from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinValueValidator

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        unique=True,
        max_length=50,
        verbose_name='Наименование'
    )
    color = ColorField(
        verbose_name='Цвет'
    )
    slug = models.SlugField(unique=True,
                            verbose_name='Slug')

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Наименование'
    )
    measurement_unit = models.CharField(max_length=50,
                                        verbose_name='Единицы измерения')

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipes'
    )
    name = models.CharField(max_length=200,
                            verbose_name='Название')
    image = models.ImageField(
        upload_to='recipes/images/',
        blank=True,
        null=True,
        verbose_name='Изображение'
    )
    text = models.TextField(verbose_name='Рецепт')
    ingredients = models.ManyToManyField(
            Ingredient,
            through='IngredientRecipe',
            verbose_name='Ингредиенты',
            related_name='recipes'
    )
    tags = models.ManyToManyField(
        Tag,
        through='TagRecipe',
        verbose_name='Тэги',
        related_name='recipes')
    cooking_time = models.PositiveIntegerField(
            validators=[MinValueValidator(1), ],
            verbose_name='Время приготовления'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        null=True,
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'


class TagRecipe(models.Model):
    tag = models.ForeignKey(
        Tag,
        null=True,
        on_delete=models.CASCADE,
        verbose_name='Тэг')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Тэг в рецепте'
        verbose_name_plural = 'Тэги в рецепте'


class Favorites(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorites'
            )
        ]

    def __str__(self):
        return f'Favorite recipe {self.user} {self.recipe}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт'
    )

    def __str__(self):
        return f'Shopping cart: {self.user} {self.recipe}'

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shoping_cart'
            )
        ]


class NumberOfIngredients(models.Model):
    ingredient = models.ForeignKey(
            Ingredient,
            on_delete=models.CASCADE,
            related_name='amount',
            verbose_name='Ингредиент'
    )
    amount = models.PositiveIntegerField(
            verbose_name='Количество')
    recipe = models.ForeignKey(
            Recipe,
            on_delete=models.CASCADE,
            related_name='amount',
            verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Количество ингредиентов'
