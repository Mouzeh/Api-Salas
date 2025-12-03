from rest_framework import serializers
from .models import Usuario, Sala, Reserva
from django.utils import timezone
from datetime import datetime, time

class UsuarioSerializer(serializers.ModelSerializer):
    total_reservas = serializers.SerializerMethodField()
    
    class Meta:
        model = Usuario
        fields = ['id', 'nombre', 'email', 'telefono', 'carrera', 'fecha_registro', 'total_reservas']
        read_only_fields = ['fecha_registro']
    
    def get_total_reservas(self, obj):
        return obj.reservas.count()
    
    def validate_email(self, value):
        # Validar formato de email
        if Usuario.objects.filter(email=value).exists():
            if self.instance and self.instance.email == value:
                return value
            raise serializers.ValidationError("Este email ya está registrado")
        return value


class SalaSerializer(serializers.ModelSerializer):
    disponible = serializers.SerializerMethodField()
    
    class Meta:
        model = Sala
        fields = ['id', 'nombre', 'capacidad', 'ubicacion', 'equipamiento', 'estado', 'disponible']
    
    def get_disponible(self, obj):
        return obj.estado == 'disponible'
    
    def validate_capacidad(self, value):
        if value <= 0:
            raise serializers.ValidationError("La capacidad debe ser mayor a 0")
        if value > 100:
            raise serializers.ValidationError("La capacidad no puede exceder 100 personas")
        return value


class ReservaSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='usuario.nombre', read_only=True)
    sala_nombre = serializers.CharField(source='sala.nombre', read_only=True)
    duracion_horas = serializers.SerializerMethodField()
    
    class Meta:
        model = Reserva
        fields = [
            'id', 'usuario', 'usuario_nombre', 'sala', 'sala_nombre', 
            'fecha', 'hora_inicio', 'hora_fin', 'duracion_horas',
            'estado', 'motivo_uso', 'fecha_creacion'
        ]
        read_only_fields = ['fecha_creacion']
    
    def get_duracion_horas(self, obj):
        # Calcular duración en horas
        inicio = datetime.combine(obj.fecha, obj.hora_inicio)
        fin = datetime.combine(obj.fecha, obj.hora_fin)
        duracion = (fin - inicio).total_seconds() / 3600
        return round(duracion, 2)
    
    def validate(self, data):
        # Validar que la hora de fin sea posterior a la hora de inicio
        if data['hora_fin'] <= data['hora_inicio']:
            raise serializers.ValidationError({
                'hora_fin': 'La hora de fin debe ser posterior a la hora de inicio'
            })
        
        # Validar que la fecha no sea en el pasado
        if data['fecha'] < timezone.now().date():
            raise serializers.ValidationError({
                'fecha': 'No se pueden hacer reservas en fechas pasadas'
            })
        
        # Validar que la sala esté disponible
        sala = data.get('sala')
        if sala and sala.estado != 'disponible':
            raise serializers.ValidationError({
                'sala': f'La sala {sala.nombre} no está disponible (estado: {sala.estado})'
            })
        
        # Validar horario de operación (ejemplo: 8:00 - 22:00)
        hora_apertura = time(8, 0)
        hora_cierre = time(22, 0)
        
        if data['hora_inicio'] < hora_apertura or data['hora_fin'] > hora_cierre:
            raise serializers.ValidationError({
                'horario': f'El horario de reservas es de {hora_apertura.strftime("%H:%M")} a {hora_cierre.strftime("%H:%M")}'
            })
        
        # Validar duración máxima (ejemplo: 4 horas)
        inicio = datetime.combine(data['fecha'], data['hora_inicio'])
        fin = datetime.combine(data['fecha'], data['hora_fin'])
        duracion = (fin - inicio).total_seconds() / 3600
        
        if duracion > 4:
            raise serializers.ValidationError({
                'duracion': 'La duración máxima de una reserva es de 4 horas'
            })
        
        # Validar conflictos de horario
        reserva_id = self.instance.id if self.instance else None
        conflictos = Reserva.objects.filter(
            sala=data['sala'],
            fecha=data['fecha'],
            estado__in=['pendiente', 'confirmada']
        ).exclude(id=reserva_id)
        
        for reserva in conflictos:
            if not (data['hora_fin'] <= reserva.hora_inicio or data['hora_inicio'] >= reserva.hora_fin):
                raise serializers.ValidationError({
                    'horario': f'Ya existe una reserva en este horario. Reserva conflictiva: {reserva.hora_inicio} - {reserva.hora_fin}'
                })
        
        return data


class ReservaListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados"""
    usuario_nombre = serializers.CharField(source='usuario.nombre', read_only=True)
    sala_nombre = serializers.CharField(source='sala.nombre', read_only=True)
    sala_ubicacion = serializers.CharField(source='sala.ubicacion', read_only=True)
    
    class Meta:
        model = Reserva
        fields = [
            'id', 'usuario_nombre', 'sala_nombre', 'sala_ubicacion',
            'fecha', 'hora_inicio', 'hora_fin', 'estado'
        ]