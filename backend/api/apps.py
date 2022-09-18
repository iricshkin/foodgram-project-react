"""Модуль конфигурации приложения."""

from django.apps import AppConfig


class ApiConfig(AppConfig):
    """Класс конфигурации управления API."""

    name = 'api'
    verbose_name = 'Управление API'
