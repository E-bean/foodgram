# Generated by Django 3.2.15 on 2022-08-30 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='ingredient',
            field=models.ManyToManyField(related_name='recipes', through='recipes.IngredientInRecipe', to='recipes.Ingredient'),
        ),
    ]
