from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UsuarioViewSet, SalaViewSet, ReservaViewSet

# Crear el router
router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet, basename='usuario')
router.register(r'salas', SalaViewSet, basename='sala')
router.register(r'reservas', ReservaViewSet, basename='reserva')

urlpatterns = [
    path('', include(router.urls)),
]