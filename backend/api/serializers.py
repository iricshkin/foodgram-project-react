from django.forms import ValidationError
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (
    Favorite, Ingredient, IngredientInRecipe, Recipe, ShoppingCart, Tag,
    TagRecipe,
)
from rest_framework import serializers
from users.models import Subscription, User


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор данных пользователя."""
    password = serializers.CharField(required=True, write_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'id', 'first_name', 'last_name', 'username', 'email', 'password',
            'is_subscribed'
        )
        model = User

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save
        return user

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=request.user, author=obj.author
        ).exists()

    def validate_email(self, data):
        if User.objects.filter(email=data).exists():
            raise ValidationError(
                'Пользователь с данной почтой существует!'
            )
        return data


class PasswordSerializer(serializers.Serializer):
    """Сериализатор для пароля."""
    new_password = serializers.CharField(max_length=150)
    current_password = serializers.CharField(max_length=150)

    def validate_current_password(self, data):
        user = self.context['request'].user
        current_password = data
        if not user.check_password(current_password):
            raise ValidationError('Неверный пароль, попробуйте еще раз!')
        return current_password

    def validate(self, data):
        if data['current_password'] == data['new_password']:
            raise ValidationError('Пароли не должны совпадать!')
        return data


class TokenCreateSerializer(serializers.Serializer):
    """Сериализатор для создания токена."""
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""
    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    """Сериализатор для упрощенного отображения модели рецептов."""
    image = Base64ImageField()

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipe


class SubscriptionsSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок."""
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
        'is_subscribed', 'recipes', 'recipes_count')
        model = Subscription

    def validate(self, data):
        user = self.context['request'].user
        if data['author'] == user:
            raise ValidationError('Нельзя подписываться на самого себя!')
        return data

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return request.user.is_authenticated and Subscription.objects.filter(
            user= request.user, author=obj.author
        ).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        queryset = Recipe.objects.filter(author=obj.author)
        if recipes_limit:
            queryset = queryset[:int(recipes_limit)]
        return RecipeMinifiedSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()
