from django.db import transaction
from django.forms import ValidationError
from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Subscription, Tag, TagRecipe)
from rest_framework import serializers
from users.models import User


class SubscribeSerializer(metaclass=serializers.SerializerMetaclass):
    """Сериализатор подписки пользователя на автора."""

    is_subscribed = serializers.SerializerMethodField()

    # def get_is_subscribed(self, obj):
    #    request = self.context.get('request')
    #    if request.user.is_anonymous:
    #        return False
    #    if Subscription.objects.filter(
    #        user=request.user, following__id=obj.id
    #        ).exists():
    #        return True
    #    else:
    #        return False

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=request.user, author=obj
        ).exists()


class UserSerializer(UserCreateSerializer, SubscribeSerializer):
    """Сериализатор данных пользователя."""

    class Meta:
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
        write_only_fields = ('password',)
        read_only_fields = ('id',)
        extra_kwargs = {'is_subscribed': {'required': False}}

    def to_representations(self, obj):
        result = super(UserSerializer, self).to_representation(obj)
        result.pop('password', None)
        return result

    def validate_email(self, data):
        if User.objects.filter(email=data).exists():
            raise ValidationError('Пользователь с данной почтой существует!')
        return data


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""

    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount')
        read_only_fields = ('id', 'name', 'measurement_unit')
        model = Ingredient


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    """Сериализатор для упрощенного отображения модели рецептов."""

    image = Base64ImageField()

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipe


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для количества ингредиентов в рецепте."""

    id = serializers.ReadOnlyField(
        default=Ingredient.objects.all(), source='ingredient_id'
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount')
        model = IngredientInRecipe


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов."""

    author = UserSerializer(default=serializers.CurrentUserDefault())
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    ingredients = IngredientInRecipeSerializer(
        source='ingredient_in_recipes', many=True
    )
    image = Base64ImageField(max_length=None, use_url=False)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
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

    def validate_ingredients(self, value):
        ingredients_list = []
        ingredients = value
        for ingredient in ingredients:
            if ingredient['amount'] < 1:
                raise serializers.ValidationError(
                    'Количество не может быть меньше 1!'
                )
            id_to_check = ingredient['ingredient']['id']
            ingredient_to_check = Ingredient.objects.filter(id=id_to_check)
            if not ingredient_to_check.exists():
                raise serializers.ValidationError(
                    'Данного ингредиента нет в базе!'
                )
            if ingredient_to_check in ingredients_list:
                raise serializers.ValidationError(
                    'Данный ингредиент уже есть в рецепте!'
                )
            ingredients_list.append(ingredient_to_check)
        return value

    def to_representation(self, instance):
        repres = super().to_representation(instance)
        repres['tags'] = TagSerializer(instance.tags.all(), many=True).data
        repres['ingredients'] = IngredientInRecipeSerializer(
            instance.ingredient_in_recipes.all(), many=True
        ).data
        return repres

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return user.is_authenticated and Favorite.objects.filter(
            user=user, recipe=obj
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return user.is_authenticated and ShoppingCart.objects.filter(
            user=user, recipe__id=obj.id
        )

    def add_ingredients_and_tags(self, tags, ingredients, recipe):
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

        # for ingredient in ingredients:
        #    if not IngredientInRecipe.objects.filter(
        #        ingredient_id=ingredient['ingredient']['id'],
        #        recipe=recipe,
        #    ).exists():
        #        ingredientinrecipe = IngredientInRecipe.objects.create(
        #            ingredient_id=ingredient['ingredient']['id'],
        #            recipe=recipe,
        #        )
        #        ingredientinrecipe.amount = ingredient['amount']
        #        ingredientinrecipe.save()
        #    else:
        #        IngredientInRecipe.objects.filter(recipe=recipe).delete()
        #        recipe.delete()
        #        raise serializers.ValidationError(
        #            'Данный ингредиент уже есть в рецепте!'
        #        )
        #    return recipe

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredientinrecipes')
        recipe = Recipe.objects.create(**validated_data)
        recipe = self.add_ingredients_and_tags(tags, ingredients, recipe)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredientinrecipes')
        TagRecipe.objects.filter(recipe=instance).delete()
        IngredientInRecipe.objects.filter(recipe=instance).delete()
        instance = self.add_ingredients_and_tags(tags, ingredients, instance)
        super().update(instance, validated_data)
        instance.save()
        return instance


class ShoppingCartSerializer(serializers.Serializer):
    """Сериализатор для списка покупок."""

    id = serializers.IntegerField()
    name = serializers.CharField()
    cooking_time = serializers.IntegerField()
    image = Base64ImageField(
        max_length=None,
        use_url=False,
    )


class SubscriptionsSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок."""

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
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

    def validate(self, data):
        user = self.context['request'].user
        if data['author'] == user:
            raise ValidationError('Нельзя подписываться на самого себя!')
        return data

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (
            request.user.is_authenticated
            and Subscription.objects.filter(
                user=request.user, author=obj
            ).exists()
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')

        queryset = Recipe.objects.filter(author=obj)
        if recipes_limit:
            queryset = queryset[: int(recipes_limit)]
        return RecipeMinifiedSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()
