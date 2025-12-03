from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model, login

Usuario = get_user_model()

@api_view(["POST"])
@permission_classes([AllowAny])
def set_session(request):
    auth = request.headers.get("Authorization", "")

    if not auth.startswith("Bearer "):
        return JsonResponse({"error": "Token faltante"}, status=400)

    token = auth.split()[1]

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user = Usuario.objects.get(id=payload["user_id"])
        login(request, user)
        return JsonResponse({"success": True})
    except Exception:
        return JsonResponse({"error": "Token inválido"}, status=400)
