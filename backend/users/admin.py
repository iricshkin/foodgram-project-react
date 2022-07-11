from django.contrib import admin
from .models import User, Subscribe

class UserAdmin(admin.ModelAdmin):
    """Админка пользователя."""
    list_display = ('id', 'username', 'email')
    search_fields = ('username', 'email')
    empty_value_display = '-пусто-'
    list_filter = ('username', 'email')


class SubscribeAdmin(admin.ModelAdmin):
    """Админка подписок."""
    list_display = ('user', 'author')
    list_filter = ('user',)
    search_fields = ('user',)


admin.site.register(User, UserAdmin)
admin.site.register(Subscribe, SubscribeAdmin)
