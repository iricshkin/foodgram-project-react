from django_filters import FilterSet, filters
from django_filters.widgets import BooleanWidget
from recipes.models import Recipe, Tag
from rest_framework.filters import SearchFilter


class IngredientSearchFilter(SearchFilter):
    """Фильтр поиска ингредиентов."""

    search_param = 'name'


class RecipeFilter(FilterSet):
    """Фильтр для рецептов."""

    author = filters.AllValuesFilter(field_name='author')
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slag',
        queryset=Tag.objects.all(),
        to_field_name='slug',
    )
    is_favorited = filters.BooleanFilter(
        widget=BooleanWidget(), method='filter_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        widget=BooleanWidget(), method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(in_favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset
