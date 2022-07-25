from rest_framework.pagination import PageNumberPagination


class LimitPageNumberPagination(PageNumberPagination):
    """Общий пагинатор для большинства endpoints."""

    page_size = 6
    page_size_query_param = 'limit'
    page_query_param = 'page'
