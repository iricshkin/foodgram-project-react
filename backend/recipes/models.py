from tabnanny import verbose
from django.db import models
from django.core.validators import MinValueValidator, RegexValidator

from users.models import User

MIN_INGR_AMOUNT = 1
MIN_COOK_TIME = 1


class Tag(models.Model):
    """Модель тэгов."""
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название',
        help_text='Введите название тега'
    )
    color = models.CharField(
        max_length=7,
        unique=True,
        null=True,
        verbose_name='Цвет в НЕХ',
        help_text='Введите цвет тега в НЕХ',
        validators=[
            RegexValidator(
                r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                'Неверный цветовой код'
            )
        ]  
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        null=True, 
        verbose_name='Уникальный слаг',
        help_text='Введите уникальный слаг',
        validators=[
            RegexValidator(
                r'^[-a-zA-Z0-9_]+$',
                'Неверный уникальный слаг'
            )
        ]
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    """Модель ингредиента."""
    name = models.CharField(
        max_length=200,
        verbose_name='Название ингредиента',
        help_text='Введите название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения',
        help_text='Введите единицу измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self) -> str:
        return f'{self.name}, {self.measurement_unit}'

    
