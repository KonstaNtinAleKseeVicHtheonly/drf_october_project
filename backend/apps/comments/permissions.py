from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Разрешение, позволяющее редактировать комментарий только автору
    """
    
    def has_object_permission(self, request, view, obj):
        # Разрешения на чтение для всех
        if request.method in permissions.SAFE_METHODS: # если у нас get запрос на чтение
            return True
        # Разрешения на запись только для автора
        return obj.author == request.user # если запрос на изменение или удаление то только автор коммнета может изменить его