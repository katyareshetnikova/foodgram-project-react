from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_base64.fields import Base64ImageField
from foodgram.models import (Favorites, Ingredient, IngredientForRecipe,
                             Recipe, ShoppingCart, Subscriptions, Tag)
from rest_framework import serializers

User = get_user_model()


class UserSerializer(UserSerializer):
    """Сериализатор для получения инфо о пользователях."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscriptions.objects.filter(user=user, author=obj).exists()


class UserCreateSerializer(UserCreateSerializer):
    """Сериализатор для регистрации нового пользователя."""

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'password')


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор для краткой информации о рецепте."""

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра списка подписок пользователя."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        user = self.context['request'].user
        if not request or not user.is_authenticated:
            return False
        return obj.subscribing.filter(user=user).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = None
        if request:
            recipes_limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.all()
        if recipes_limit:
            recipes = obj.recipes.all()[:int(recipes_limit)]
        return RecipeShortSerializer(recipes, many=True,
                                     context={'request': request}).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class UserSubscribeSerializer(serializers.Serializer):
    """Сериализатор для подписки/отписки от пользователей."""

    def validate(self, data):
        user = self.context.get('request').user
        author = get_object_or_404(User, pk=self.context['pk'])
        if user == author:
            raise serializers.ValidationError(
                'Невозможно подписаться на самого себя.'
            )
        if Subscriptions.objects.filter(user=user, author=author).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого пользователя.'
            )
        return data

    def create(self, validated_data):
        user = self.context.get('request').user
        author = get_object_or_404(User, pk=validated_data['pk'])
        Subscriptions.objects.create(user=user, author=author)
        serializer = SubscriptionSerializer(
            author, context={'request': self.context.get('request')}
        )
        return serializer.data


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для получения тэга."""

    class Meta:
        model = Tag
        fields = ('id', 'name',
                  'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализотор для получения списка ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name',
                  'measurement_unit')


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор количества ингредиентов для рецепта."""

    id = serializers.PrimaryKeyRelatedField(source='ingredient.id',
                                            read_only=True
                                            )
    name = serializers.StringRelatedField(source='ingredient.name')
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientForRecipe
        fields = ('id', 'name',
                  'measurement_unit',
                  'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для получения информации о рецепте."""

    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(many=True, source='recipes')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image',
                  'text', 'cooking_time')

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and Favorites.objects.filter(
                    user=request.user, recipe=obj
                ).exists())

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and ShoppingCart.objects.filter(
                    user=request.user, recipe=obj
                ).exists())


class IngredientAddSerializer(serializers.ModelSerializer):
    """Сериализатор добавления ингредиента в рецепт."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientForRecipe
        fields = ('id', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания/удаления рецепта."""

    ingredients = IngredientAddSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all())
    author = UserSerializer(read_only=True)
    image = Base64ImageField(required=True, allow_null=False)

    class Meta:
        model = Recipe
        fields = ('id', 'ingredients',
                  'tags', 'image',
                  'name', 'text',
                  'cooking_time', 'author')

    def add_ingredients_and_tags(self, tags, ingredients, recipe):
        recipe.tags.set(tags)
        ingredients_list = []
        for ingredient in ingredients:
            new_ingredient = IngredientForRecipe(
                recipe=recipe,
                ingredient_id=ingredient['id'],
                amount=ingredient['amount'],
            )
            ingredients_list.append(new_ingredient)
        IngredientForRecipe.objects.bulk_create(ingredients_list)
        return recipe

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        return self.add_ingredients_and_tags(tags, ingredients, recipe)

    def update(self, instance, validated_data):
        instance.ingredients.clear()
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance = super().update(instance, validated_data)
        return self.add_ingredients_and_tags(
            tags, ingredients, instance
        )

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeSerializer(
            instance,
            context={'request': request}
        ).data


class FavoriteSerializer(serializers.Serializer):

    def validate(self, data):
        user = self.context['request'].user
        pk = self.context['recipe_id']

        if Favorites.objects.filter(user=user,
                                    recipe__id=pk).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в избранное.'
            )
        return data

    def create(self, validated_data):
        recipe = get_object_or_404(Recipe, pk=validated_data['id'])
        user = self.context['request'].user
        Favorites.objects.create(user=user, recipe=recipe)
        serializer = RecipeShortSerializer(recipe)
        return serializer.data


class ShoppingCartSerializer(serializers.Serializer):

    def validate(self, data):
        user = self.context['request'].user
        pk = self.context['recipe_id']

        if ShoppingCart.objects.filter(user=user,
                                       recipe__id=pk).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в список покупок.'
            )
        return data

    def create(self, validated_data):
        recipe = get_object_or_404(Recipe, pk=validated_data['id'])
        user = self.context['request'].user
        ShoppingCart.objects.create(user=user, recipe=recipe)
        serializer = RecipeShortSerializer(recipe)
        return serializer.data
