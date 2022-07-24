from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Модель пользователя."""

    username = models.CharField(
        db_index=True,
        max_length=150,
        unique=True,
        verbose_name='Логин',
        help_text='Введите логин',
    )
    email = models.EmailField(
        db_index=True,
        unique=True,
        max_length=254,
        verbose_name='Электронная почта',
        help_text='Введите электронную почту',
    )
    first_name = models.CharField(
        max_length=150, verbose_name='Имя', help_text='Введите имя'
    )
    last_name = models.CharField(
        max_length=150, verbose_name='Фамилия', help_text='Введите фамилию'
    )
    is_subcribed = models.BooleanField(
        default=False,
        verbose_name='Подписка на данного автора',
        help_text='Отметьте для подписки на автора',
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self) -> str:
        return self.username
