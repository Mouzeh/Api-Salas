from django.shortcuts import render

def home_view(request):
    """Vista para la página principal"""
    return render(request, 'index.html')

def cliente_view(request):
    """Vista para la aplicación cliente React"""
    # Usa el index.html del cliente React
    return render(request, 'cliente/index.html')