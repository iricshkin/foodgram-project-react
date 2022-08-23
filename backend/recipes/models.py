from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from users.models import User

MIN_INGR_AMOUNT = 1
MIN_COOK_TIME = 1


class Tag(models.Model):
    """Модель тэгов."""

    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название',
        help_text='Введите название тега',
    )
    color = models.CharField(
        max_length=7,
        unique=True,
        null=True,
        verbose_name='Цвет в НЕХ',
        help_text='Введите цвет тега в НЕХ',
        validators=[
            RegexValidator(
                r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', 'Неверный цветовой код'
            )
        ],
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        null=True,
        verbose_name='Уникальный слаг',
        help_text='Введите уникальный слаг',
        validators=[
            RegexValidator(r'^[-a-zA-Z0-9_]+$', 'Неверный уникальный слаг')
        ],
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
        help_text='Введите название ингредиента',
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения',
        help_text='Введите единицу измерения',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self) -> str:
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    """Модель рецептов."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
        help_text='Введите автора рецепта',
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта',
        help_text='Введите название рецепта',
    )
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Изображение рецепта',
        help_text='Выберите изображение рецепта',
    )
    text = models.TextField(
        verbose_name='Описание рецепта', help_text='Введите описание рецепта'
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления (в минутах)',
        help_text='Введите время приготовления (в минутах)',
        validators=[
            MinValueValidator(
                MIN_COOK_TIME,
                f'минимальное время приготовления {MIN_COOK_TIME} мин.',
            )
        ],
    )
    tags = models.ManyToManyField(
        Tag,
        through='TagRecipe',
        verbose_name='Тег рецепта',
        help_text='Выберите тег рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        related_name='recipes',
        verbose_name='Необходимые ингредиенты',
        help_text='Выберете необходимые ингредиенты',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания рецепта',
        help_text='Введите дату создания рецепта',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self) -> str:
        return f'{self.name} - {self.author}'


class TagRecipe(models.Model):
    """Модель списка тегов рецепта."""

    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Тег рецепта',
        help_text='Выберите тег рецепта',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        help_text='Выберите рецепт',
    )

    class Meta:
        verbose_name = 'Список тегов рецепта'
        verbose_name_plural = 'Список тегов рецепта'
        constraints = [
            models.UniqueConstraint(
                fields=['tag', 'recipe'], name='unique_tag_recipe'
            )
        ]

    def __str__(self) -> str:
        return f'{self.tag} - {self.recipe}'


class IngredientInRecipe(models.Model):
    """Модель количества ингредиентов в рецепте."""

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
        related_name='ingredientinrecipes',
        verbose_name='Ингредиенты рецепта',
        help_text='Выберите ингредиенты рецепта',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipesingredients',
        verbose_name='Рецепт',
        help_text='Выберите рецепт',
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        help_text='Укажите количество ингредиента',
        validators=[
            MinValueValidator(
                MIN_INGR_AMOUNT,
                f'укажите количество не менее {MIN_INGR_AMOUNT}',
            )
        ],
    )

    class Meta:
        verbose_name = 'Ингредиенты в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient_in_recipe',
            )
        ]

    def __str__(self) -> str:
        return f'{self.recipe} -{self.ingredient}, {self.amount}'


class Favorite(models.Model):
    """Модель списка избранного."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Избранный пользователь',
        help_text='Выберите избранного пользователя',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Избранный рецепт',
        help_text='Выберите избранный рецепт',
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        ordering = ('-id',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_recipe_in_favorite'
            )
        ]

    def __str__(self) -> str:
        return f'{self.user} - {self.recipe}'


class Subscription(models.Model):
    """Модель подписок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Избранный автор',
    )
    created = models.DateTimeField(
        db_index=True, verbose_name='Дата создания', auto_now_add=True
    )

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_relationships'
            ),
            models.CheckConstraint(
                name='prevent_self_follow',
                check=~models.Q(user=models.F('author')),
            ),
        ]

    def __str__(self) -> str:
        return f'{self.user} подписан(а) на {self.author}'


class ShoppingCart(models.Model):
    """Модель списка покупок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        help_text='Выберите пользователя',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shoppingcart',
        verbose_name='Рецепт в списке покупок',
        help_text='Выберите рецепт для списка покупок',
    )
    add_date = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата добавления'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        ordering = ('-add_date',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_shopping_cart'
            )
        ]
