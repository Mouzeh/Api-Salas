
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

class Usuario(AbstractUser):
    """
    Usuario extendido con campos personalizados
    """
    ROLES = [
        ('usuario', 'Usuario Regular'),
        ('admin', 'Administrador'),
    ]
    
    telefono = models.CharField(max_length=15)
    carrera = models.CharField(max_length=100)
    rol = models.CharField(max_length=20, choices=ROLES, default='usuario')
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    # Campos requeridos por AbstractUser
    email = models.EmailField(unique=True)
    
    # Usar email como username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    @property
    def nombre_completo(self):
        return self.get_full_name()
    
    @property
    def es_admin(self):
        return self.rol == 'admin' or self.is_staff or self.is_superuser


class Sala(models.Model):
    ESTADOS = [
        ('disponible', 'Disponible'),
        ('mantenimiento', 'Mantenimiento'),
    ]
    
    nombre = models.CharField(max_length=50, unique=True)
    capacidad = models.IntegerField()
    ubicacion = models.CharField(max_length=100)
    equipamiento = models.TextField(help_text="Ej: Proyector, Pizarra, Computadores")
    estado = models.CharField(max_length=20, choices=ESTADOS, default='disponible')
    imagen = models.URLField(blank=True, null=True, help_text="URL de imagen de la sala")
    
    class Meta:
        db_table = 'salas'
        verbose_name = 'Sala'
        verbose_name_plural = 'Salas'
    
    def __str__(self):
        return f"{self.nombre} - Capacidad: {self.capacidad}"


class Reserva(models.Model):
    ESTADOS_RESERVA = [
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
    ]
    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='reservas')
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE, related_name='reservas')
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    estado = models.CharField(max_length=20, choices=ESTADOS_RESERVA, default='pendiente')
    motivo_uso = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'reservas'
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        ordering = ['-fecha', '-hora_inicio']
    
    def __str__(self):
        return f"{self.sala.nombre} - {self.usuario.get_full_name()} - {self.fecha}"
    
    def clean(self):
        if self.hora_fin <= self.hora_inicio:
            raise ValidationError('La hora de fin debe ser posterior a la hora de inicio')
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


