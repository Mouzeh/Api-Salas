from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.contrib.auth import logout as auth_logout
import jwt
from django.conf import settings
import json

Usuario = get_user_model()


# ============================
# 🔹 LOGOUT VIEW
# ============================
def logout_view(request):
    """Vista para cerrar sesión"""
    # Cerrar sesión en Django
    auth_logout(request)
    
    # Limpiar datos de la sesión
    request.session.flush()
    
    # Si es una solicitud AJAX/JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'message': 'Sesión cerrada'})
    
    # Redirigir al login
    return redirect('login')


# ============================
# 🔹 VISTA HOME / INDEX
# ============================
def home_view(request):
    """Vista para la página principal"""
    return render(request, 'index.html')


# ============================
# 🔹 LOGIN VIEW - CORREGIDA
# ============================
def login_view(request):
    """Vista de login y registro - Versión corregida"""
    # Si ya está autenticado, redirigir según su rol
    if request.user.is_authenticated:
        if hasattr(request.user, 'es_admin') and request.user.es_admin:
            return redirect('admin_dashboard')
        else:
            return redirect('cliente_dashboard')
    
    # Manejar login desde React (JSON)
    if request.method == 'POST' and request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
            email = data.get('email', '').strip()
            password = data.get('password', '')
            
            if not email or not password:
                return JsonResponse({
                    'error': 'Email y contraseña son requeridos'
                }, status=400)
            
            # Autenticar usuario
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                login(request, user)
                
                return JsonResponse({
                    'success': True,
                    'message': 'Login exitoso',
                    'redirect': 'admin_dashboard' if (user.is_staff or user.is_superuser or (hasattr(user, 'es_admin') and user.es_admin)) else 'cliente_dashboard'
                })
            else:
                return JsonResponse({
                    'error': 'Credenciales incorrectas'
                }, status=401)
                
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Datos inválidos'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    # Si es GET, mostrar la página de login
    return render(request, 'admin/login.html')


# ============================
# 🔹 JWT SESSION LOGIN VIEW - CORREGIDA
# ============================
@csrf_exempt
def set_session_view(request):
    """Vista para establecer sesión a partir de token JWT - Corregida"""
    if request.method == 'POST':
        try:
            auth_header = request.headers.get('Authorization', '')
            
            if not auth_header.startswith('Bearer '):
                return JsonResponse({
                    'success': False,
                    'error': 'Token no proporcionado o formato inválido'
                }, status=401)
            
            token = auth_header.split(' ')[1]
            
            try:
                # Decodificar token JWT
                payload = jwt.decode(
                    token, 
                    settings.SECRET_KEY, 
                    algorithms=['HS256'],
                    options={'verify_exp': True}
                )
                
                user_id = payload.get('user_id')
                if not user_id:
                    return JsonResponse({
                        'success': False,
                        'error': 'Token inválido: no contiene user_id'
                    }, status=401)
                
                # Buscar usuario
                try:
                    user = Usuario.objects.get(id=user_id)
                except Usuario.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'error': 'Usuario no encontrado'
                    }, status=404)
                
                # Iniciar sesión en Django
                login(request, user)
                
                return JsonResponse({
                    'success': True,
                    'message': 'Sesión establecida correctamente',
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'nombre_completo': user.get_full_name(),
                        'es_admin': user.es_admin if hasattr(user, 'es_admin') else user.is_staff
                    }
                })
                    
            except jwt.ExpiredSignatureError:
                return JsonResponse({
                    'success': False, 
                    'error': 'Token expirado'
                }, status=401)
            except jwt.InvalidTokenError as e:
                return JsonResponse({
                    'success': False, 
                    'error': f'Token inválido: {str(e)}'
                }, status=401)
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error interno: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'error': 'Método no permitido'
    }, status=405)


# ============================
# 🔹 DECORADORES DE ROLES
# ============================
def es_admin(user):
    return user.is_authenticated and (
        (hasattr(user, 'rol') and user.rol == 'admin') 
        or user.is_staff 
        or user.is_superuser
    )

def es_usuario_regular(user):
    return user.is_authenticated and hasattr(user, 'rol') and user.rol == 'usuario'


# ============================
# 🔹 DASHBOARD CLIENTE - PERMANENTE
# ============================
@login_required(login_url='/login/')
def cliente_dashboard_view(request):
    """Vista permanente para dashboard del cliente"""
    # Verificar si el usuario tiene sesión activa
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Verificar si el usuario tiene rol de usuario regular
    # Si es admin, redirigir al admin dashboard
    if hasattr(request.user, 'es_admin') and request.user.es_admin:
        return redirect('admin_dashboard')
    
    # Pasar datos del usuario al template
    context = {
        'user': request.user,
        'is_authenticated': True,
    }
    
    return render(request, 'cliente/dashboard.html', context)


# ============================
# 🔹 DASHBOARD ADMIN - PERMANENTE
# ============================
@login_required(login_url='/login/')
@user_passes_test(lambda u: u.is_staff or u.is_superuser or (hasattr(u, 'es_admin') and u.es_admin))
def admin_dashboard_view(request):
    """Vista permanente para dashboard del administrador"""
    # Pasar datos del usuario al template
    context = {
        'user': request.user,
        'is_authenticated': True,
        'is_admin': True,
    }
    
    return render(request, 'admin/dashboard.html', context)


# ============================
# 🔹 VISTA PARA ERRORES DE AUTENTICACIÓN
# ============================
def auth_error_view(request):
    """Vista para mostrar errores de autenticación"""
    error_message = request.GET.get('message', 'Error de autenticación')
    return render(request, 'auth_error.html', {'error_message': error_message})