class JWTAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Verificar si hay token en los headers
        auth_header = request.headers.get('Authorization', '')
        
        if auth_header.startswith('Bearer '):
            # Si hay token JWT en los headers, marcar la sesión
            request.session['has_jwt_token'] = True
        
        response = self.get_response(request)
        return response