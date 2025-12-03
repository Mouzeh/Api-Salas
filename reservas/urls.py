from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    CustomTokenObtainPairView,
    RegistroViewSet,
    UsuarioViewSet,
    SalaViewSet,
    ReservaViewSet,
    CheckAuthView  # Ahora sí está definido
)

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet, basename='usuario')
router.register(r'salas', SalaViewSet, basename='sala')
router.register(r'reservas', ReservaViewSet, basename='reserva')

urlpatterns = [
    # Autenticación
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/registro/', RegistroViewSet.as_view({'post': 'create'}), name='registro'),
    path('auth/check/', CheckAuthView.as_view(), name='check_auth'),  # Descomentado
    path("auth/login/", LoginView.as_view(), name="auth_login"),
    path("set-session/", set_session, name="set_session"),
    
    # API REST
    path('', include(router.urls)),
]