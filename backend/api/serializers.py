"""Модуль сериализаторов."""

from django.db import transaction
from django.forms import ValidationError
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Subscription, Tag, TagRecipe)
from rest_framework import serializers
from users.models import User


class SubscriptionsSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок."""

    class Meta:
        """Метакласс сериализатора подписок."""

        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        model = User

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    def validate(self, data):
        """Метод проверки попытки подписки на себя."""
        user = self.context['request'].user
        if data['author'] == user:
            raise ValidationError(
                'Нельзя подписываться на самого себя!',
            )
        return data

    def get_is_subscribed(self, obj):
        """Метод для получения сведений о наличии подписки на автора."""
        request = self.context.get('request')
        return (
            request.user.is_authenticated
            and Subscription.objects.filter(
                user=request.user,
                author=obj,
            ).exists()
        )

    def get_recipes(self, obj):
        """Метод для получения всех рецептов автора."""
        queryset = Recipe.objects.filter(
            author=obj,
        )
        return RecipeMinifieldSerializer(
            queryset,
            many=True,
        ).data

    def get_recipes_count(self, obj):
        """Метод для получения количества рецептов автора."""
        return Recipe.objects.filter(author=obj).count()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор данных пользователя."""

    class Meta:
        """Метакласс сериализатора пользователя."""

        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
            'is_subscribed',
        )
        model = User

    password = serializers.CharField(required=True, write_only=True)
    is_subscribed = serializers.SerializerMethodField()

    def create(self, validated_data):
        """Метод для создания пользователя."""
        user = User(**validated_data)
        user.set_password(
            validated_data['password'],
        )
        user.save
        return user

    def get_is_subscribed(self, obj):
        """Метод для получения подписок пользователя."""
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=request.user,
            author=obj,
        ).exists()

    def validate_email(self, data):
        """Метод для проверки наличия пользователя с указанной почтой."""
        if User.objects.filter(email=data).exists():
            raise ValidationError('Пользователь с данной почтой существует!')
        return data


class PasswordSerializer(serializers.Serializer):
    """Сериализатор для пароля."""

    new_password = serializers.CharField(max_length=150)
    current_password = serializers.CharField(max_length=150)

    def validate_current_password(self, data):
        """Метод для проверки корректности введенного пароля."""
        user = self.context['request'].user
        current_password = data
        if not user.check_password(current_password):
            raise ValidationError('Неверный пароль, попробуйте еще раз!')
        return current_password

    def validate(self, data):
        """Метод для проверки старого и нового пароля на совпадение."""
        if data['current_password'] == data['new_password']:
            raise ValidationError('Пароли не должны совпадать!')
        return data


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""

    class Meta:
        """Метакласс сериализатора тегов."""

        fields = (
            'id',
            'name',
            'color',
            'slug',
        )
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        """Метакласс сериализатора ингредиентов."""

        fields = (
            'id',
            'name',
            'measurement_unit',
        )
        model = Ingredient


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов в рецепте."""

    id = serializers.ReadOnlyField(
        source='ingredient.id',
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name',
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
    )

    class Meta:
        """Метакласс сериализатора ингредиетов в рецепте."""

        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )
        model = IngredientInRecipe


class AddToIngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления количества ингредиентов."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        """Метакласс сериализатора добавления ингредиентов в рецепт."""

        fields = (
            'id',
            'amount',
        )
        model = IngredientInRecipe


class RecipeMinifieldSerializer(serializers.ModelSerializer):
    """Сериализатор для упрощенного отображения модели рецептов."""

    class Meta:
        """Метакласс сериализатора упрощенного отображений рецептов."""

        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )
        read_only_fields = ('author',)
        model = Recipe

    image = Base64ImageField()


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов."""

    class Meta:
        """Метакласс сериализатора рецептов."""

        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        model = Recipe

    author = UserSerializer(default=serializers.CurrentUserDefault())
    tags = TagSerializer(read_only=True, many=True)
    ingredients = IngredientInRecipeSerializer(
        source='recipesingredients',
        many=True,
    )
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    def get_is_favorited(self, obj):
        """Метод для получения избранных рецептов."""
        request = self.context['request']
        if request is None or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        """Метод для получения списка покупок."""
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user,
            recipe=obj,
        ).exists()


class RecipePostSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецептов."""

    class Meta:
        """Метакласс создания рецептов."""

        fields = (
            'id',
            'author',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )
        model = Recipe

    author = UserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    ingredients = AddToIngredientInRecipeSerializer(
        source='recipesingredients',
        many=True,
    )
    image = Base64ImageField(
        max_length=None,
        use_url=True,
    )

    def validate_ingredients(self, ingredients):
        """Метод для проверки корректности добавления ингредиентов в рецепт."""
        if not ingredients:
            raise serializers.ValidationError(
                'Необходимо выбрать ингредиенты!',
            )

        for ingredient in ingredients:
            if ingredient['amount'] < 1:
                raise serializers.ValidationError(
                    'Количество не может быть меньше 1!',
                )
        ids = [ingredient['id'] for ingredient in ingredients]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError(
                'Данный ингредиент уже есть в рецепте!',
            )
        return ingredients

    def add_ingredients_and_tags(self, tags, ingredients, recipe):
        """Метод для добавления ингредиентов и тегов в создаваемый рецепт."""
        for tag in tags:
            recipe.tags.add(tag)
            recipe.save()
        instances = [
            IngredientInRecipe(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount'],
            )
            for ingredient in ingredients
        ]
        IngredientInRecipe.objects.bulk_create(instances)
        return recipe

    @transaction.atomic
    def create(self, validated_data):
        """Метод для создания рецепта."""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipesingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe = self.add_ingredients_and_tags(
            tags=tags,
            ingredients=ingredients,
            recipe=recipe,
        )
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        """Метод для редактирования рецепта."""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipesingredients')
        TagRecipe.objects.filter(recipe=instance).delete()
        IngredientInRecipe.objects.filter(recipe=instance).delete()
        instance = self.add_ingredients_and_tags(tags, ingredients, instance)
        super().update(instance, validated_data)
        instance.save()
        return instance
