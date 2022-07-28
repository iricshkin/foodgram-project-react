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
        widget=BooleanWidget(),
        method='filter_is_favorited',
    )
    is_in_shopping_cart = filters.BooleanFilter(
        widget=BooleanWidget(),
        method='filteris_in_shopping_cart',
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def _is_favorited_is_in_shopping_cart(self, queryset, key):
        filter_dict = {
            'favorites': 'is_favorited',
            'cart': 'is_in_shopping_cart',
        }
        user = self.request.user
        if not user.is_authenticated:
            return queryset
        value = self.request.query_params.get(
            filter_dict[key],
        )
        if value:
            return queryset.filter(
                **{f'{key}__user': self.request.user}
            ).distinct()
        return queryset

    def filter_is_favorited(self, queryset, is_favorited, slug):
        return self._is_favorited_is_in_shopping_cart(queryset, 'favorites')

    def filter_is_in_shopping_cart(self, queryset, is_in_shopping_cart, slug):
        return self._is_favorited_is_in_shopping_cart(queryset, 'cart')
