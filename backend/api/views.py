from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    ShoppingCart,
    Subscription,
    Tag,
)
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .filters import IngredientSearchFilter, RecipeFilter
from .pagination import LimitPageNumberPagination
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (
    IngredientSerializer,
    PasswordSerializer,
    RecipeMinifiedSerializer,
    RecipeSerializer,
    SubscriptionsSerializer,
    TagSerializer,
    UserSerializer,
)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для пользователя."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitPageNumberPagination

    @action(
        detail=False,
        url_path='set_password',
        methods=['POST'],
        permission_classes=(IsAuthenticated,),
    )
    def set_password(self, request, pk=None):
        user = self.request.user
        context = {'request': request}
        serializer = PasswordSerializer(data=request.data, context=context)
        if serializer.is_valid():
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'status': 'Пароль установлен!'})
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        methods=['GET'], detail=False, permission_classes=(IsAuthenticated,)
    )
    def me(self, request, pk=None):
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        serializer = UserSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        queryset = User.objects.filter(following__user=request.user)
        obj = self.paginate_queryset(queryset)
        serializer = SubscriptionsSerializer(
            obj, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def subcribe(self, request, pk=None):
        user = request.user
        author_id = pk
        author = get_object_or_404(User, pk=author_id)
        if request.method == 'POST':
            if user == author:
                return Response(
                    data={'detail': 'Нельзя подписываться на себя!'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if Subscription.objects.filter(user=user, author=author).exists():
                return Response(
                    data={'detail': 'Вы уже подписаны на этого автора!'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            Subscription.objects.create(user=user, author=author)
            serializer = self.get_serializer(author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if not Subscription.objects.filter(
                user=user, author=author
            ).exists():
                return Response(
                    data={'detai': 'Вы не подписаны на этого автора!'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            subscribe = Subscription.objects.filter(user=user, author=author)
            subscribe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_class = (IsAuthorOrReadOnly,)
    pagination_classes = LimitPageNumberPagination
    filterset_class = RecipeFilter

    @action(
        url_path='download_shopping_cart',
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        """Получение списка покупок в формате txt."""
        ingredients = (
            ShoppingCart.objects.filter(user=request.user)
            .values(
                'recipe__ingredients__name',
                'recipe__ingredients__measurement_unit',
            )
            .annotate(amount=Sum('recipe__ingredient_in_recipe__amout'))
        )
        if not ingredients:
            return Response(
                {'errors': 'Список покупок пуст!'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        shopping_cart = 'Ваш список покупок: \n'
        for ingredient in ingredients:
            shopping_cart += (
                f'{ingredient["recipe__ingredients__name"]} '
                f'({ingredient["recipe__ingredients__measurement_unit"]}) - '
                f'{ingredient["amount"]} \n\n'
            )
        shopping_cart += '@Продуктовый помощник'
        filename = 'my_shopping_cart.txt'
        response = HttpResponse(
            shopping_cart, status=status.HTTP_200_OK, content_type='text/plain'
        )
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class FavoriteViewSet(
    mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    """Вьюсет для избранных рецептов."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeMinifiedSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        if Favorite.objects.filter(user=request.user, recipe=recipe).exists():
            return Response(
                data={'detail': 'Этот рецепт уже есть в избранном!'},
                status=status.HTTP_400_Bad_REQUEST,
            )
        Favorite.objects.create(user=request.user, recipe=recipe)
        serializer = self.get_serializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        if not Favorite.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                data={'detail': 'Вы не подписаны на этот рецепт!'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        favorite = Favorite.objects.filter(user=user, recipe=recipe)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(viewsets.ModelViewSet):
    """Вьюсет для списка покупок."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeMinifiedSerializer
    permission_classes = (
        IsAdminOrReadOnly,
        IsAuthorOrReadOnly,
        IsAuthenticated,
    )

    def create(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        if ShoppingCart.objects.filter(
            user=request.user, recipe=recipe
        ).exists():
            return Response(
                data={'detail': 'Рецепт уже есть в списке покупок!'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        ShoppingCart.objects.create(user=request.user, recipe=recipe)
        serializer = self.get_serializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


def delete(self, request, recipe_id):
    user = request.user
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    if not ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
        return Response(
            data={'detail': 'Рецепта еще нет в списке покупок!'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    cart = ShoppingCart.objects.filter(user=user, recipe=recipe)
    cart.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
