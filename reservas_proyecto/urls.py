# Archivo: reservas_proyecto/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('admin/', admin.site.urls),
    path('api/', include('reservas.urls')),
    path('cliente/', views.cliente_view, name='cliente'),
]

# ¡ESTA LÍNEA ES CRÍTICA PARA SERVIR ARCHIVOS ESTÁTICOS EN DESARROLLO!
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)