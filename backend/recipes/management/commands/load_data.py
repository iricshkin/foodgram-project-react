"""Скрипт для заполнения базы данных ингредиетов."""

import json
from typing import Any, Optional

from django.core.management.base import BaseCommand
from recipes.models import Ingredient

JSON_PATH = '../data/ingredients.json'


class Command(BaseCommand):
    """Работа с базой данных."""

    help = 'Загрузка данных из файла ingredients.json'

    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        if Ingredient.objects.exists():
            print('Данные уже загружены!')
            return

        with open(JSON_PATH, encoding='utf-8') as json_file:
            ingredients = json.load(json_file)
            for ingredient in ingredients:
                name = ingredient['name']
                measurement_unit = ingredient['measurement_unit']
                Ingredient.objects.create(
                    name=name, measurement_unit=measurement_unit
                )
        print('Ингредиенты загружены в базу!')
