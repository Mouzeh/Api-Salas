from django.contrib import admin
from .models import Usuario, Sala, Reserva

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'email', 'carrera', 'telefono', 'fecha_registro']
    search_fields = ['nombre', 'email', 'carrera']
    list_filter = ['carrera', 'fecha_registro']
    ordering = ['-fecha_registro']

@admin.register(Sala)
class SalaAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'capacidad', 'ubicacion', 'estado']
    search_fields = ['nombre', 'ubicacion']
    list_filter = ['estado', 'capacidad']
    ordering = ['nombre']

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ['id', 'usuario', 'sala', 'fecha', 'hora_inicio', 'hora_fin', 'estado']
    search_fields = ['usuario__nombre', 'sala__nombre', 'motivo_uso']
    list_filter = ['estado', 'fecha']
    ordering = ['-fecha', '-hora_inicio']
    date_hierarchy = 'fecha'