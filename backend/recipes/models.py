from django.db import models
from django.contrib.auth import get_user_model
from colorfield.fields import ColorField

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        unique=True,
        max_length=50
    )
    color = ColorField(
        null=True,
        default='#FF0000',
        format='hexa'
    )
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True
    )
    measurement_unit = models.CharField(max_length=50)

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
            verbose_name='Время приготовления'
    )

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        null=True,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE
    )


class TagRecipe(models.Model):
    tag = models.ForeignKey(
        Tag,
        null=True,
        on_delete=models.CASCADE)
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )


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
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shoping_cart'
            )
        ]


class Number_of_Ingredients(models.Model):
    ingredient = models.ForeignKey(
            Ingredient,
            on_delete=models.CASCADE,
            related_name='amount',
    )
    amount = models.PositiveIntegerField()
    recipe = models.ForeignKey(
            Recipe,
            on_delete=models.CASCADE,
            related_name='amount'
    )
