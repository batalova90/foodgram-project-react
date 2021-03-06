# Generated by Django 2.2.19 on 2022-02-08 13:24

import colorfield.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0009_auto_20220208_1246'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='numberofingredients',
            options={'verbose_name': 'Количество ингредиентов'},
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='measurement_unit',
            field=models.CharField(max_length=50,
                                   verbose_name='Единицы измерения'),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='name',
            field=models.CharField(max_length=50,
                                   unique=True,
                                   verbose_name='Наименование'),
        ),
        migrations.AlterField(
            model_name='ingredientrecipe',
            name='ingredient',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='recipes.Ingredient',
                verbose_name='Ингредиент'),
        ),
        migrations.AlterField(
            model_name='ingredientrecipe',
            name='recipe',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='recipes.Recipe',
                verbose_name='Рецепт'),
        ),
        migrations.AlterField(
            model_name='numberofingredients',
            name='amount',
            field=models.PositiveIntegerField(verbose_name='Количество'),
        ),
        migrations.AlterField(
            model_name='numberofingredients',
            name='ingredient',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='amount',
                to='recipes.Ingredient',
                verbose_name='Ингредиент'),
        ),
        migrations.AlterField(
            model_name='numberofingredients',
            name='recipe',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='amount',
                to='recipes.Recipe',
                verbose_name='Рецепт'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=colorfield.fields.ColorField(
                blank=True,
                default='#FF0000',
                image_field=None,
                max_length=18,
                null=True,
                samples=None,
                verbose_name='Цвет'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(
                max_length=50,
                unique=True,
                verbose_name='Наименование'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='slug',
            field=models.SlugField(unique=True,
                                   verbose_name='Slug'),
        ),
        migrations.AlterField(
            model_name='tagrecipe',
            name='recipe',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='recipes.Recipe',
                verbose_name='Рецепт'),
        ),
        migrations.AlterField(
            model_name='tagrecipe',
            name='tag',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='recipes.Tag',
                verbose_name='Тэг'),
        ),
    ]
