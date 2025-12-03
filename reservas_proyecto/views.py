# Archivo: reservas_proyecto/views.py
from django.shortcuts import render
from django.http import HttpResponse
import os

def home_view(request):
    """Vista para la página principal"""
    return render(request, 'index.html')

def cliente_view(request):
    """Vista para la aplicación cliente - versión simple que funciona"""
    # Renderizar una versión simple que no tenga conflictos
    return render(request, 'cliente/simple.html')  # Crearemos este archivo