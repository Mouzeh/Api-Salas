from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """
    Permiso personalizado para administradores
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.es_admin


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permiso para que el usuario solo pueda ver/editar sus propias reservas
    o si es administrador puede ver/editar todas
    """
    def has_object_permission(self, request, view, obj):
        # Los admins pueden hacer todo
        if request.user.es_admin:
            return True
        
        # Los usuarios solo pueden acceder a sus propias reservas
        if hasattr(obj, 'usuario'):
            return obj.usuario == request.user
        
        return False


class ReadOnlyOrAdmin(permissions.BasePermission):
    """
    Solo lectura para usuarios normales, escritura para admins
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        return request.user and request.user.is_authenticated and request.user.es_admin
