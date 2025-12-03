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
# 🔹 LOGOUT VIEW AGREGADO
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
# 🔹 LOGIN VIEW
# ============================
def login_view(request):
    """Vista de login y registro"""
    # Si el usuario ya está autenticado, redirigir según su rol
    if request.user.is_authenticated:
        if hasattr(request.user, 'es_admin') and request.user.es_admin:
            return redirect('admin_dashboard')
        else:
            return redirect('cliente_dashboard')
    
    # Manejar login tradicional o JSON
    if request.method == 'POST':
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                email = data.get('email')
                password = data.get('password')
            except:
                return JsonResponse({'error': 'Datos inválidos'}, status=400)
        else:
            email = request.POST.get('email')
            password = request.POST.get('password')
        
        if email and password:
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                login(request, user)

                # Si es una solicitud JSON (React u otra API)
                if request.content_type == 'application/json':
                    return JsonResponse({
                        'success': True,
                        'redirect': 'admin_dashboard' if user.es_admin else 'cliente_dashboard'
                    })

                # Si es formulario normal
                if user.es_admin:
                    return redirect('admin_dashboard')
                else:
                    return redirect('cliente_dashboard')

            else:
                if request.content_type == 'application/json':
                    return JsonResponse({'error': 'Credenciales incorrectas'}, status=401)

                return render(request, 'admin/login.html', {
                    'error': 'Credenciales incorrectas'
                })
    
    return render(request, 'admin/login.html')


# ============================
# 🔹 JWT SESSION LOGIN VIEW
# ============================
@csrf_exempt
def set_session_view(request):
    """Vista para establecer sesión a partir de token JWT"""
    if request.method == 'POST':
        auth_header = request.headers.get('Authorization', '')
        
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            
            try:
                payload = jwt.decode(
                    token, 
                    settings.SECRET_KEY, 
                    algorithms=['HS256']
                )
                
                user_id = payload.get('user_id')
                if user_id:
                    user = Usuario.objects.get(id=user_id)

                    login(request, user)

                    return JsonResponse({
                        'success': True,
                        'message': 'Sesión establecida',
                        'user': {
                            'id': user.id,
                            'email': user.email,
                            'nombre_completo': user.get_full_name(),
                            'es_admin': user.es_admin
                        }
                    })
                    
            except jwt.ExpiredSignatureError:
                return JsonResponse({'success': False, 'error': 'Token expirado'}, status=401)
            except jwt.InvalidTokenError:
                return JsonResponse({'success': False, 'error': 'Token inválido'}, status=401)
            except Usuario.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Usuario no encontrado'}, status=404)
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return JsonResponse({
        'success': False,
        'error': 'Método no permitido o token no proporcionado'
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
# 🔹 DASHBOARD CLIENTE
# ============================
@login_required(login_url='/login/')
@user_passes_test(es_usuario_regular, login_url='/login/')
def cliente_dashboard_view(request):
    return render(request, 'cliente/dashboard.html')


# ============================
# 🔹 DASHBOARD ADMIN
# ============================
@login_required(login_url='/login/')
@user_passes_test(es_admin, login_url='/login/')
def admin_dashboard_view(request):
    return render(request, 'admin/dashboard.html')
