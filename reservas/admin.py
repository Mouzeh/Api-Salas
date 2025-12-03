from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Usuario, Sala, Reserva

@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'rol', 'carrera']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'carrera']
    list_filter = ['rol', 'is_staff', 'is_active', 'fecha_registro']
    ordering = ['-fecha_registro']
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
        ('Información Personal', {
            'fields': ('first_name', 'last_name', 'telefono', 'carrera'),
        }),
        ('Permisos', {
            'fields': ('rol', 'is_staff', 'is_active'),
        }),
    )
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información Personal', {
            'fields': ('first_name', 'last_name', 'email', 'telefono', 'carrera')
        }),
        ('Permisos', {
            'fields': ('rol', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Fechas', {
            'fields': ('last_login', 'date_joined'),
        }),
    )

@admin.register(Sala)
class SalaAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'capacidad', 'ubicacion', 'estado']
    search_fields = ['nombre', 'ubicacion']
    list_filter = ['estado', 'capacidad']
    ordering = ['nombre']

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ['id', 'usuario', 'sala', 'fecha', 'hora_inicio', 'hora_fin', 'estado']
    search_fields = ['usuario__username', 'sala__nombre']
    list_filter = ['estado', 'fecha']
    ordering = ['-fecha', '-hora_inicio']