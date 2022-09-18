"""Модуль конфигурации приложения."""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Класс конфигурации управления пользователями."""

    name = 'users'
    verbose_name = 'Управление пользователями'
