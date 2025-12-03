from django.shortcuts import render

def home_view(request):
    """Vista para la página principal"""
    return render(request, 'index.html')

def login_view(request):
    """Vista de login y registro"""
    return render(request, 'auth/login.html')

def cliente_dashboard_view(request):
    """Vista del dashboard para usuarios regulares"""
    return render(request, 'cliente/dashboard.html')

def admin_dashboard_view(request):
    """Vista del dashboard para administradores"""
    return render(request, 'admin/dashboard.html')