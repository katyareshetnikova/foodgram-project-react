from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models
from foodgram.validators import validator_username


class User(AbstractUser):
    """Модель создания пользователя."""

    email = models.EmailField(
        'Адрес электронной почты',
        max_length=254,
        unique=True,
    )

    username = models.CharField(
        'Уникальный юзернэйм',
        validators=(validator_username, ),
        max_length=150,
        unique=True,
    )

    first_name = models.CharField(
        'Имя',
        max_length=150,
        blank=True,
    )

    last_name = models.CharField(
        'Фамилия',
        max_length=150,
        blank=True,
    )

    password = models.CharField(
        'Пароль',
        max_length=150,
        blank=True,
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Tag(models.Model):
    """Модель тэга рецепта."""

    name = models.CharField(
        'Название',
        max_length=150,
        blank=True,
    )

    color = models.CharField(
        'Цвет',
        max_length=10,
        blank=True,
    )

    slug = models.SlugField(
        'Слаг тэга',
        max_length=100,
        unique=True,
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиентов для блюда."""

    name = models.CharField(
        'Название',
        max_length=200,
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=200,
    )

    class Meta:
        ordering = ('-name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель создания рецепта."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',

    )

    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        verbose_name='Ингредиенты',
    )

    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тэги',
    )

    image = models.ImageField(
        'Картинка',
        upload_to='recipes/',
        blank=True,
    )

    name = models.CharField(
        'Название',
        max_length=200,
    )

    text = models.TextField(
        'Описание',
    )

    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=[
            MinValueValidator(
                1, 'Минимальное время приготовления блюда - 1 минута'
            )
        ]
    )

    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        ordering = ('-pub_date', )
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientForRecipe(models.Model):
    """Модель для ингредиентов в рецепте."""

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredients',
        verbose_name='Ингредиент',
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Рецепт',
    )

    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        unique_together = ('recipe', 'ingredient')


class ShoppingCart(models.Model):
    """Модель списка покупок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь',
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Покупка',
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'


class Favorites(models.Model):
    """Модель избранных рецептов."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class Subscriptions(models.Model):
    """Модель подписок пользователя."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Пользователь',
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribing',
        verbose_name='Автор',
    )

    class Meta:
        unique_together = ('user', 'author')
        ordering = ('-id',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
