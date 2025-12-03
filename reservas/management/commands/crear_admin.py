from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

Usuario = get_user_model()

class Command(BaseCommand):
    help = "Crea un usuario administrador con email y contraseña"

    def add_arguments(self, parser):
        parser.add_argument("email", type=str, help="Correo del administrador")
        parser.add_argument("password", type=str, help="Contraseña del administrador")

    def handle(self, *args, **kwargs):
        email = kwargs["email"]
        password = kwargs["password"]

        if Usuario.objects.filter(email=email).exists():
            self.stdout.write(self.style.ERROR("❌ Ya existe un usuario con ese email"))
            return

        user = Usuario(
            username=email,             # requerido por AbstractUser
            email=email,
            first_name="Admin",         # requerido
            last_name="System",         # requerido
            rol="admin",                # tu campo para admins
            is_staff=True,              # permite entrar al admin panel
            is_superuser=True           # permisos totales
        )

        user.set_password(password)
        user.save()

        self.stdout.write(self.style.SUCCESS("✅ Administrador creado correctamente"))
        self.stdout.write(self.style.SUCCESS(f"Email: {email}"))
        self.stdout.write(self.style.SUCCESS(f"Password: {password}"))
