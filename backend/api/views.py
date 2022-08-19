from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_list_or_404, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingCart,
    Subscription,
    Tag,
)
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from users.models import User

from .filters import IngredientSearchFilter, RecipeFilter
from .pagination import LimitPageNumberPagination
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (
    IngredientSerializer,
    RecipeMinifiedSerializer,
    RecipeSerializer,
    SubscriptionsSerializer,
    TagSerializer,
    UserSerializer,
)


class CreateUserViewSet(UserViewSet):
    """Вьюсет для пользователя."""

    serializer_class = UserSerializer
    pagination_class = LimitPageNumberPagination

    def get_queryset(self):
        return User.objects.all()


class SubscriptionsViewSet(viewsets.ModelViewSet):
    """Вьюсет для подписок."""

    serializer_class = SubscriptionsSerializer
    permission_class = (IsAuthenticated,)

    def get_queriser(self):
        return get_list_or_404(User, author=self.request.user)

    def create(self, request, *args, **kwargs):
        user = request.user
        author_id = self.kwargs.get('author_id')
        author = get_object_or_404(User, id=author_id)
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

    def delete(self, request, *args, **kwargs):
        user = request.user
        author_id = self.kwargs.get('author_id')
        author = get_object_or_404(User, id=author_id)
        subscribe = Subscription.objects.filter(user=user, author=author)
        if not subscribe.exists():
            return Response(
                data={'detail': 'Вы не подписаны на этого автора!'},
                status=status.HTTP_400_BAD_REQUEST,
            )
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
    filter_backends = (DjangoFilterBackend,)

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
            .annotate(amount=Sum('recipe__ingredient_in_recipes__amout'))
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
    filterset_class = IngredientSearchFilter
    # filter_backend = (
    #    DjangoFilterBackend,
    #    IngredientSearchFilter,
    # )
    # search_fields = ('^name',)


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
        favorite = Favorite.objects.filter(user=user, recipe=recipe)
        if not favorite.exists():
            return Response(
                data={'detail': 'Вы не подписаны на этот рецепт!'},
                status=status.HTTP_400_BAD_REQUEST,
            )
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
    cart = ShoppingCart.objects.filter(user=user, recipe=recipe)
    if not cart.exists():
        return Response(
            data={'detail': 'Рецепта еще нет в списке покупок!'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    cart.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


class DownloadShoppingCart(viewsets.ModelViewSet):
    """
    Сохранение файла списка покупок.
    """

    permission_classes = (IsAuthenticated,)

    @staticmethod
    def canvas_method(dictionary):
        response = HttpResponse(content_type='application/pdf')
        response[
            'Content-Disposition'
        ] = 'attachment; \
        filename = "shopping_cart.pdf"'
        begin_position_x, begin_position_y = 40, 650
        sheet = canvas.Canvas(response, pagesize=A4)
        pdfmetrics.registerFont(TTFont('FreeSans', 'data/FreeSans.ttf'))
        sheet.setFont('FreeSans', 50)
        sheet.setTitle('Список покупок')
        sheet.drawString(
            begin_position_x, begin_position_y + 40, 'Список покупок: '
        )
        sheet.setFont('FreeSans', 24)
        for number, item in enumerate(dictionary, start=1):
            if begin_position_y < 100:
                begin_position_y = 700
                sheet.showPage()
                sheet.setFont('FreeSans', 24)
            sheet.drawString(
                begin_position_x,
                begin_position_y,
                f'{number}.  {item["ingredient__name"]} - '
                f'{item["ingredient_total"]}'
                f' {item["ingredient__measurement_unit"]}',
            )
            begin_position_y -= 30
        sheet.showPage()
        sheet.save()
        return response

    def download(self, request):
        result = (
            IngredientInRecipe.objects.filter(recipe__carts__user=request.user)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .order_by('ingredient__name')
            .annotate(ingredient_total=Sum('amount'))
        )
        return self.canvas_method(result)
