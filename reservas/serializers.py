from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Sala, Reserva
from django.utils import timezone
from datetime import datetime, time

Usuario = get_user_model()

class UsuarioSerializer(serializers.ModelSerializer):
    total_reservas = serializers.SerializerMethodField()
    nombre_completo = serializers.CharField(read_only=True)
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'nombre_completo', 'telefono', 'carrera', 'rol', 
            'fecha_registro', 'total_reservas', 'password'
        ]
        read_only_fields = ['fecha_registro', 'total_reservas']
    
    def get_total_reservas(self, obj):
        return obj.reservas.count()
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        usuario = Usuario(**validated_data)
        if password:
            usuario.set_password(password)
        usuario.save()
        return usuario
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class RegistroSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = Usuario
        fields = [
            'username', 'email', 'password', 'password2',
            'first_name', 'last_name', 'telefono', 'carrera'
        ]
    
    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden"})
        
        if Usuario.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({"email": "Este email ya está registrado"})
        
        return data
    
    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        
        usuario = Usuario(**validated_data)
        usuario.set_password(password)
        usuario.rol = 'usuario'  # Por defecto es usuario regular
        usuario.save()
        return usuario


class SalaSerializer(serializers.ModelSerializer):
    disponible = serializers.SerializerMethodField()
    total_reservas = serializers.SerializerMethodField()
    
    class Meta:
        model = Sala
        fields = [
            'id', 'nombre', 'capacidad', 'ubicacion', 'equipamiento', 
            'estado', 'imagen', 'disponible', 'total_reservas'
        ]
    
    def get_disponible(self, obj):
        return obj.estado == 'disponible'
    
    def get_total_reservas(self, obj):
        return obj.reservas.filter(estado__in=['pendiente', 'confirmada']).count()


class ReservaSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='usuario.nombre_completo', read_only=True)
    sala_nombre = serializers.CharField(source='sala.nombre', read_only=True)
    duracion_horas = serializers.SerializerMethodField()
    puede_editar = serializers.SerializerMethodField()
    
    class Meta:
        model = Reserva
        fields = [
            'id', 'usuario', 'usuario_nombre', 'sala', 'sala_nombre', 
            'fecha', 'hora_inicio', 'hora_fin', 'duracion_horas',
            'estado', 'motivo_uso', 'fecha_creacion', 'puede_editar'
        ]
        read_only_fields = ['fecha_creacion', 'usuario']
    
    def get_duracion_horas(self, obj):
        inicio = datetime.combine(obj.fecha, obj.hora_inicio)
        fin = datetime.combine(obj.fecha, obj.hora_fin)
        duracion = (fin - inicio).total_seconds() / 3600
        return round(duracion, 2)
    
    def get_puede_editar(self, obj):
        request = self.context.get('request')
        if not request or not request.user:
            return False
        return obj.usuario == request.user or request.user.es_admin
    
    def validate(self, data):
        # Validaciones existentes...
        if data['hora_fin'] <= data['hora_inicio']:
            raise serializers.ValidationError({
                'hora_fin': 'La hora de fin debe ser posterior a la hora de inicio'
            })
        
        if data['fecha'] < timezone.now().date():
            raise serializers.ValidationError({
                'fecha': 'No se pueden hacer reservas en fechas pasadas'
            })
        
        sala = data.get('sala')
        if sala and sala.estado != 'disponible':
            raise serializers.ValidationError({
                'sala': f'La sala {sala.nombre} no está disponible'
            })
        
        hora_apertura = time(8, 0)
        hora_cierre = time(22, 0)
        
        if data['hora_inicio'] < hora_apertura or data['hora_fin'] > hora_cierre:
            raise serializers.ValidationError({
                'horario': f'El horario de reservas es de 08:00 a 22:00'
            })
        
        inicio = datetime.combine(data['fecha'], data['hora_inicio'])
        fin = datetime.combine(data['fecha'], data['hora_fin'])
        duracion = (fin - inicio).total_seconds() / 3600
        
        if duracion > 4:
            raise serializers.ValidationError({
                'duracion': 'La duración máxima de una reserva es de 4 horas'
            })
        
        # Validar conflictos
        reserva_id = self.instance.id if self.instance else None
        conflictos = Reserva.objects.filter(
            sala=data['sala'],
            fecha=data['fecha'],
            estado__in=['pendiente', 'confirmada']
        ).exclude(id=reserva_id)
        
        for reserva in conflictos:
            if not (data['hora_fin'] <= reserva.hora_inicio or data['hora_inicio'] >= reserva.hora_fin):
                raise serializers.ValidationError({
                    'horario': f'Ya existe una reserva en este horario: {reserva.hora_inicio} - {reserva.hora_fin}'
                })
        
        return data
    
    def create(self, validated_data):
        # Asignar el usuario autenticado
        request = self.context.get('request')
        if request and request.user:
            validated_data['usuario'] = request.user
        return super().create(validated_data)


class ReservaListSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='usuario.nombre_completo', read_only=True)
    sala_nombre = serializers.CharField(source='sala.nombre', read_only=True)
    sala_ubicacion = serializers.CharField(source='sala.ubicacion', read_only=True)
    
    class Meta:
        model = Reserva
        fields = [
            'id', 'usuario_nombre', 'sala_nombre', 'sala_ubicacion',
            'fecha', 'hora_inicio', 'hora_fin', 'estado'
        ]

