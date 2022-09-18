"""Модуль конфигурации приложения."""

from django.apps import AppConfig


class RecipesConfig(AppConfig):
    """Класс конфигурации управления рецептами."""

    name = 'recipes'
    verbose_name = 'Управление рецептами'
