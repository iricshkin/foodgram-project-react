"""Модуль разрешений."""

from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Разрешение для редактирования объекта только для авторов."""

    message = 'Редактирование чужого контента запрещено!'

    def has_object_permission(self, request, view, obj):
        """Метод для разрешений редактировать объект."""
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    """Разрешение доступа только для чтения или только для администратора."""

    message = 'Редактировать контент может только администратор!'

    def has_object_permission(self, request, view, obj):
        """Метод для разрешений доступа к объекту."""
        return (
            request.method in permissions.SAFE_METHODS or request.user.is_staff
        )
