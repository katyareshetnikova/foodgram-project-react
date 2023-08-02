from django.db.models import Sum
from django.shortcuts import HttpResponse, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from foodgram.models import (Favorites, Ingredient, IngredientForRecipe,
                             Recipe, ShoppingCart, Subscriptions, Tag, User)

from .filters import RecipeFilter
from .pagination import PageNumberLimitPagination
from .serializers import (IngredientSerializer, RecipeCreateSerializer,
                          RecipeSerializer,
                          SubscriptionSerializer, TagSerializer,
                          UserSubscribeSerializer)


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
        elif request.method == 'DELETE':
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
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = PageNumberLimitPagination
    http_method_names = ('get', 'post', 'patch', 'delete',)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeCreateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,)
            )
    def favorite(self, request, pk=None):
        """Добавление/удаление из избранного."""
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            serializer = self.get_serializer(
                data=request.data,
                context={'request': request, 'id': pk}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(id=pk)
            return Response(status=status.HTTP_201_CREATED)
        if not Favorites.objects.filter(user=request.user,
                                        recipe=recipe).exists():
            return Response('Рецепт уже добавлен в избранное.',
                            status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'DELETE':
            get_object_or_404(
                Favorites, user=request.user,
                recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,),
            )
    def shopping_cart(self, request, pk=None):
        """Добавление/удаление из списка покупок."""
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            serializer = self.get_serializer(
                data=request.data,
                context={'request': request, 'id': pk}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(id=pk)
            return Response(status=status.HTTP_201_CREATED)
        if not ShoppingCart.objects.filter(user=request.user,
                                           recipe=recipe).exists():
            return Response('Рецепт уже добавлен в список покупок.',
                            status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'DELETE':
            get_object_or_404(
                ShoppingCart, user=request.user,
                recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            methods=['get'],
            permission_classes=(IsAuthenticated,)
            )
    def download_shopping_cart(self, request):
        """Отправка файла со списком покупок."""
        user = request.user
        shopping_cart = ShoppingCart.objects.filter(user=user)
        recipe_id = [i.recipe for i in shopping_cart]
        amount_list = IngredientForRecipe.objects.filter(
            recipe__in=recipe_id
        ).values('ingredient').annotate(amount=Sum('amount'))
        shopping_list = ['Список покупок:\n']
        for i in amount_list:
            ingredients = Ingredient.objects.get(pk=i['ingredient'])
            amount = i['amount']
            shopping_list.append(
                f'\n{ingredients.name} - {amount}',
                f'{ingredients.measurement_unit}'
                )
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = \
            'attachment; filename="shopping_cart.txt"'
        return response


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Список игредиентов."""

    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name', )
