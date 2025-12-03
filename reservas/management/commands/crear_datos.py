from django.core.management.base import BaseCommand
from reservas.models import Usuario, Sala, Reserva
from datetime import date, time, timedelta
from django.utils import timezone

class Command(BaseCommand):
    help = 'Crea datos de prueba para el sistema de reservas'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creando datos de prueba...')
        
        # Limpiar datos existentes (opcional)
        self.stdout.write('Limpiando datos antiguos...')
        Reserva.objects.all().delete()
        Usuario.objects.all().delete()
        Sala.objects.all().delete()
        
        # Crear Usuarios
        self.stdout.write('Creando usuarios...')
        usuarios = [
            Usuario.objects.create(
                nombre='Juan Pérez',
                email='juan.perez@mail.com',
                telefono='+56912345678',
                carrera='Ingeniería Informática'
            ),
            Usuario.objects.create(
                nombre='María González',
                email='maria.gonzalez@mail.com',
                telefono='+56987654321',
                carrera='Ingeniería Civil'
            ),
            Usuario.objects.create(
                nombre='Carlos Rodríguez',
                email='carlos.rodriguez@mail.com',
                telefono='+56923456789',
                carrera='Administración de Empresas'
            ),
            Usuario.objects.create(
                nombre='Ana Martínez',
                email='ana.martinez@mail.com',
                telefono='+56956781234',
                carrera='Psicología'
            ),
            Usuario.objects.create(
                nombre='Pedro Silva',
                email='pedro.silva@mail.com',
                telefono='+56934567890',
                carrera='Derecho'
            ),
        ]
        self.stdout.write(self.style.SUCCESS(f'✓ {len(usuarios)} usuarios creados'))
        
        # Crear Salas
        self.stdout.write('Creando salas...')
        salas = [
            Sala.objects.create(
                nombre='Sala A-101',
                capacidad=8,
                ubicacion='Edificio A, Piso 1',
                equipamiento='Proyector, Pizarra, 8 sillas, WiFi',
                estado='disponible'
            ),
            Sala.objects.create(
                nombre='Sala B-202',
                capacidad=12,
                ubicacion='Edificio B, Piso 2',
                equipamiento='Proyector, Pizarra Digital, 12 sillas, 2 Computadores, WiFi',
                estado='disponible'
            ),
            Sala.objects.create(
                nombre='Sala C-303',
                capacidad=6,
                ubicacion='Edificio C, Piso 3',
                equipamiento='TV, Pizarra, 6 sillas, WiFi',
                estado='disponible'
            ),
            Sala.objects.create(
                nombre='Sala D-104',
                capacidad=15,
                ubicacion='Edificio D, Piso 1',
                equipamiento='Proyector, Pizarra, 15 sillas, Mesa grande, WiFi',
                estado='disponible'
            ),
            Sala.objects.create(
                nombre='Sala E-205',
                capacidad=4,
                ubicacion='Edificio E, Piso 2',
                equipamiento='Pizarra, 4 sillas, Mesa pequeña, WiFi',
                estado='mantenimiento'
            ),
        ]
        self.stdout.write(self.style.SUCCESS(f'✓ {len(salas)} salas creadas'))
        
        # Crear Reservas
        self.stdout.write('Creando reservas...')
        hoy = timezone.now().date()
        manana = hoy + timedelta(days=1)
        pasado_manana = hoy + timedelta(days=2)
        
        reservas = [
            # Reservas para hoy
            Reserva.objects.create(
                usuario=usuarios[0],
                sala=salas[0],
                fecha=hoy,
                hora_inicio=time(9, 0),
                hora_fin=time(11, 0),
                estado='confirmada',
                motivo_uso='Estudio para examen de matemáticas'
            ),
            Reserva.objects.create(
                usuario=usuarios[1],
                sala=salas[1],
                fecha=hoy,
                hora_inicio=time(14, 0),
                hora_fin=time(16, 0),
                estado='confirmada',
                motivo_uso='Reunión de proyecto grupal'
            ),
            Reserva.objects.create(
                usuario=usuarios[2],
                sala=salas[2],
                fecha=hoy,
                hora_inicio=time(10, 0),
                hora_fin=time(12, 0),
                estado='pendiente',
                motivo_uso='Preparación de presentación'
            ),
            
            # Reservas para mañana
            Reserva.objects.create(
                usuario=usuarios[0],
                sala=salas[0],
                fecha=manana,
                hora_inicio=time(8, 0),
                hora_fin=time(10, 0),
                estado='confirmada',
                motivo_uso='Estudio individual'
            ),
            Reserva.objects.create(
                usuario=usuarios[3],
                sala=salas[1],
                fecha=manana,
                hora_inicio=time(15, 0),
                hora_fin=time(18, 0),
                estado='pendiente',
                motivo_uso='Taller de estudio'
            ),
            Reserva.objects.create(
                usuario=usuarios[4],
                sala=salas[3],
                fecha=manana,
                hora_inicio=time(11, 0),
                hora_fin=time(13, 0),
                estado='confirmada',
                motivo_uso='Reunión de equipo'
            ),
            
            # Reservas para pasado mañana
            Reserva.objects.create(
                usuario=usuarios[1],
                sala=salas[2],
                fecha=pasado_manana,
                hora_inicio=time(9, 0),
                hora_fin=time(12, 0),
                estado='pendiente',
                motivo_uso='Proyecto de investigación'
            ),
            Reserva.objects.create(
                usuario=usuarios[2],
                sala=salas[0],
                fecha=pasado_manana,
                hora_inicio=time(13, 0),
                hora_fin=time(15, 0),
                estado='confirmada',
                motivo_uso='Estudio para certamen'
            ),
            
            # Una reserva cancelada
            Reserva.objects.create(
                usuario=usuarios[3],
                sala=salas[1],
                fecha=hoy,
                hora_inicio=time(17, 0),
                hora_fin=time(19, 0),
                estado='cancelada',
                motivo_uso='Reunión cancelada'
            ),
        ]
        
        self.stdout.write(self.style.SUCCESS(f'✓ {len(reservas)} reservas creadas'))
        
        # Resumen
        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS('¡Datos de prueba creados exitosamente!'))
        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write(f'Total Usuarios: {Usuario.objects.count()}')
        self.stdout.write(f'Total Salas: {Sala.objects.count()}')
        self.stdout.write(f'Total Reservas: {Reserva.objects.count()}')
        self.stdout.write(f'  - Confirmadas: {Reserva.objects.filter(estado="confirmada").count()}')
        self.stdout.write(f'  - Pendientes: {Reserva.objects.filter(estado="pendiente").count()}')
        self.stdout.write(f'  - Canceladas: {Reserva.objects.filter(estado="cancelada").count()}')