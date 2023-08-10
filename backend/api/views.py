from django.db.models import Sum
from django.shortcuts import HttpResponse, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from foodgram.models import (Favorites, Ingredient, IngredientForRecipe,
                             Recipe, ShoppingCart, Subscriptions, Tag, User)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .pagination import PageNumberLimitPagination
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipeSerializer,
                          ShoppingCartSerializer, SubscriptionSerializer,
                          TagSerializer, UserSubscribeSerializer)


class UserViewSet(UserViewSet):
    """Страница подписок/отписок пользователя."""

    pagination_class = PageNumberLimitPagination

    @action(detail=False,
            methods=['get'],
            permission_classes=(IsAuthenticated,)
            )
    def subscriptions(self, request):
        """Список подписок."""
        queryset = User.objects.filter(subscribing__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            page,
            many=True,
            context={
                'request': request
            },
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,)
            )
    def subscribe(self, request, id=None):
        """Подписка/отписка."""
        if request.method == 'POST':
            serializer = UserSubscribeSerializer(
                data=request.data,
                context={'request': request, 'pk': id}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(pk=id)
            return Response(status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            subscription = get_object_or_404(
                Subscriptions, user=self.request.user,
                author=get_object_or_404(User, id=id)
            )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Список тэгов."""

    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = (AllowAny,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Страница рецептов."""

    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = PageNumberLimitPagination
    http_method_names = ('get', 'post', 'patch', 'delete',)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,),
            )
    def favorite(self, request, pk=None):
        """Добавление/удаление рецепта в избранные."""
        if request.method == 'POST':
            serializer = FavoriteSerializer(
                data=request.data,
                context={'request': request, 'recipe_id': pk}
            )
            serializer.is_valid(raise_exception=True)
            response_data = serializer.save(id=pk)
            return Response(response_data, status=status.HTTP_201_CREATED)
        recipe = Favorites.objects.filter(user=request.user, recipe__id=pk)
        recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,),
            )
    def shopping_cart(self, request, pk=None):
        """Добавление/удаление рецепта в корзину."""
        if request.method == 'POST':
            serializer = ShoppingCartSerializer(
                data=request.data,
                context={'request': request, 'recipe_id': pk}
            )
            serializer.is_valid(raise_exception=True)
            response_data = serializer.save(id=pk)
            return Response(response_data, status=status.HTTP_201_CREATED)
        recipe = ShoppingCart.objects.filter(
            user=request.user, recipe__id=pk)
        recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            methods=['get'],
            permission_classes=(IsAuthenticated,)
            )
    def download_shopping_cart(self, request):
        """Отправка файла со списком покупок."""
        user = request.user
        amount_list = IngredientForRecipe.objects.filter(
            recipe__shopping_cart__user=user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        shopping_list = ['Список покупок:\n']
        for i in amount_list:
            shopping_list.append(
                f"\n{i['ingredient__name']} "
                f"({i['ingredient__measurement_unit']}) - "
                f"{i['amount']}")
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = \
            'attachment; filename="shopping_cart.txt"'
        return response


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Список игредиентов."""

    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None
