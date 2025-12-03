from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Usuario, Sala, Reserva
from .serializers import (
    UsuarioSerializer, 
    SalaSerializer, 
    ReservaSerializer,
    ReservaListSerializer
)

class UsuarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar usuarios
    Operaciones: list, create, retrieve, update, partial_update, destroy
    """
    queryset = Usuario.objects.all().order_by('-fecha_registro')
    serializer_class = UsuarioSerializer
    
    @action(detail=True, methods=['get'])
    def reservas(self, request, pk=None):
        """Obtener todas las reservas de un usuario"""
        usuario = self.get_object()
        reservas = usuario.reservas.all()
        serializer = ReservaListSerializer(reservas, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def buscar_email(self, request):
        """Buscar usuario por email"""
        email = request.query_params.get('email', None)
        if not email:
            return Response(
                {'error': 'Debe proporcionar un email'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            usuario = Usuario.objects.get(email=email)
            serializer = self.get_serializer(usuario)
            return Response(serializer.data)
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Usuario no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )


class SalaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar salas
    Operaciones: list, create, retrieve, update, partial_update, destroy
    """
    queryset = Sala.objects.all().order_by('nombre')
    serializer_class = SalaSerializer
    
    @action(detail=False, methods=['get'])
    def disponibles(self, request):
        """Listar solo las salas disponibles"""
        salas = Sala.objects.filter(estado='disponible')
        serializer = self.get_serializer(salas, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def reservas(self, request, pk=None):
        """Obtener todas las reservas de una sala"""
        sala = self.get_object()
        reservas = sala.reservas.all()
        serializer = ReservaListSerializer(reservas, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def buscar_capacidad(self, request):
        """Buscar salas por capacidad mínima"""
        capacidad_min = request.query_params.get('min', None)
        
        if not capacidad_min:
            return Response(
                {'error': 'Debe proporcionar una capacidad mínima'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            capacidad_min = int(capacidad_min)
            salas = Sala.objects.filter(
                capacidad__gte=capacidad_min,
                estado='disponible'
            )
            serializer = self.get_serializer(salas, many=True)
            return Response(serializer.data)
        except ValueError:
            return Response(
                {'error': 'La capacidad debe ser un número'},
                status=status.HTTP_400_BAD_REQUEST
            )


class ReservaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar reservas
    Operaciones: list, create, retrieve, update, partial_update, destroy
    """
    queryset = Reserva.objects.all().select_related('usuario', 'sala').order_by('-fecha', '-hora_inicio')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ReservaListSerializer
        return ReservaSerializer
    
    @action(detail=True, methods=['post'])
    def confirmar(self, request, pk=None):
        """Confirmar una reserva pendiente"""
        reserva = self.get_object()
        
        if reserva.estado == 'confirmada':
            return Response(
                {'error': 'La reserva ya está confirmada'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if reserva.estado == 'cancelada':
            return Response(
                {'error': 'No se puede confirmar una reserva cancelada'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reserva.estado = 'confirmada'
        reserva.save()
        
        serializer = self.get_serializer(reserva)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        """Cancelar una reserva"""
        reserva = self.get_object()
        
        if reserva.estado == 'cancelada':
            return Response(
                {'error': 'La reserva ya está cancelada'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reserva.estado = 'cancelada'
        reserva.save()
        
        serializer = self.get_serializer(reserva)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def hoy(self, request):
        """Obtener reservas del día de hoy"""
        hoy = timezone.now().date()
        reservas = Reserva.objects.filter(fecha=hoy).select_related('usuario', 'sala')
        serializer = ReservaListSerializer(reservas, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pendientes(self, request):
        """Obtener todas las reservas pendientes"""
        reservas = Reserva.objects.filter(estado='pendiente').select_related('usuario', 'sala')
        serializer = ReservaListSerializer(reservas, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def por_fecha(self, request):
        """Buscar reservas por fecha específica"""
        fecha = request.query_params.get('fecha', None)
        
        if not fecha:
            return Response(
                {'error': 'Debe proporcionar una fecha (formato: YYYY-MM-DD)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            reservas = Reserva.objects.filter(fecha=fecha).select_related('usuario', 'sala')
            serializer = ReservaListSerializer(reservas, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': f'Formato de fecha inválido: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )