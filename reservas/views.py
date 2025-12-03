from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Sala, Reserva
from .serializers import (
    UsuarioSerializer, RegistroSerializer,
    SalaSerializer, ReservaSerializer, ReservaListSerializer
)
from .permissions import IsAdminUser, IsOwnerOrAdmin, ReadOnlyOrAdmin

Usuario = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Serializer personalizado para incluir info del usuario en el token"""
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Agregar información adicional del usuario
        data['user'] = {
            'id': self.user.id,
            'email': self.user.email,
            'nombre_completo': self.user.nombre_completo,
            'rol': self.user.rol,
            'es_admin': self.user.es_admin,
        }
        
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class RegistroViewSet(viewsets.GenericViewSet):
    """Vista para registro de nuevos usuarios"""
    permission_classes = [AllowAny]
    serializer_class = RegistroSerializer
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            usuario = serializer.save()
            return Response({
                'message': 'Usuario registrado exitosamente',
                'user': UsuarioSerializer(usuario).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsuarioViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar usuarios"""
    queryset = Usuario.objects.all().order_by('-fecha_registro')
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Obtener información del usuario autenticado"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def reservas(self, request, pk=None):
        """Obtener todas las reservas de un usuario"""
        usuario = self.get_object()
        reservas = usuario.reservas.all()
        serializer = ReservaListSerializer(reservas, many=True)
        return Response(serializer.data)


class SalaViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar salas"""
    queryset = Sala.objects.all().order_by('nombre')
    serializer_class = SalaSerializer
    permission_classes = [IsAuthenticated, ReadOnlyOrAdmin]
    
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


class ReservaViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar reservas"""
    queryset = Reserva.objects.all().select_related('usuario', 'sala').order_by('-fecha', '-hora_inicio')
    serializer_class = ReservaSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtrar reservas según el rol del usuario"""
        user = self.request.user
        if user.es_admin:
            return self.queryset
        return self.queryset.filter(usuario=user)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ReservaListSerializer
        return ReservaSerializer
    
    def perform_create(self, serializer):
        """Asignar el usuario autenticado al crear una reserva"""
        serializer.save(usuario=self.request.user)
    
    @action(detail=False, methods=['get'])
    def mis_reservas(self, request):
        """Obtener reservas del usuario autenticado"""
        reservas = Reserva.objects.filter(usuario=request.user).select_related('sala')
        serializer = ReservaListSerializer(reservas, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsOwnerOrAdmin])
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
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsOwnerOrAdmin])
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
        queryset = self.get_queryset().filter(fecha=hoy)
        serializer = ReservaListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pendientes(self, request):
        """Obtener todas las reservas pendientes"""
        queryset = self.get_queryset().filter(estado='pendiente')
        serializer = ReservaListSerializer(queryset, many=True)
        return Response(serializer.data)

