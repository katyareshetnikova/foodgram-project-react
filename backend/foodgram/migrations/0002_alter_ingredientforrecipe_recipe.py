# Generated by Django 3.2.3 on 2023-08-02 03:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodgram', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredientforrecipe',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredient_recipes', to='foodgram.recipe', verbose_name='Рецепт'),
        ),
    ]
