from django.contrib import admin
from .models import User, Subscription


class UserAdmin(admin.ModelAdmin):
    """Админка пользователя."""
    list_display = ('id', 'username', 'email')
    search_fields = ('username', 'email')
    empty_value_display = '-пусто-'
    list_filter = ('username', 'email')


class SubscriptionAdmin(admin.ModelAdmin):
    """Админка подписок."""
    list_display = ('id', 'user', 'author', 'created')
    list_filter = ('user',)
    search_fields = ('user',)


admin.site.register(User, UserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
