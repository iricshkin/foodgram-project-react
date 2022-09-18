"""Модуль для фильтров."""

from django.db.models import Case, IntegerField, Q, When
from django_filters.rest_framework import CharFilter, FilterSet, filters
from recipes.models import Ingredient, Recipe, Tag


class IngredientSearchFilter(FilterSet):
    """Фильтр поиска ингредиентов."""

    class Meta:
        """Метакласс для фильтации ингредиентов."""

        model = Ingredient
        fields = ['name']

    name = CharFilter(field_name='name', method='name_filter')

    @staticmethod
    def name_filter(queryset, name, value):
        """Метод для фильтрации по наименованию ингредиентов."""
        return (
            queryset.filter(**{f'{name}__icontains': value})
            .annotate(
                order=Case(
                    When(
                        Q(**{f'{name}__istartswith': value}),
                        then=1,
                    ),
                    When(
                        Q(**{f'{name}__icontains': value})
                        & ~Q(**{f'{name}__istartswith': value}),
                        then=2,
                    ),
                    output_field=IntegerField(),
                ),
            )
            .order_by('order')
        )


class RecipeFilter(FilterSet):
    """Фильтр для рецептов."""

    class Meta:
        """Метакласс для фильтрации рецептов."""

        model = Recipe
        fields = (
            'author',
            'tags',
            'is_favorited',
            'is_in_shopping_cart',
        )

    author = filters.AllValuesFilter(field_name='author')
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug',
    )
    is_favorited = filters.BooleanFilter(
        field_name='favorites',
        method='_choice_filter',
    )
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='shoppingcart',
        method='_choice_filter',
    )

    def _choice_filter(self, queryset, key, value):
        """Метод для выбора фильтра."""
        if value:
            return queryset.filter(**{f'{key}__user': self.request.user})
        return queryset
