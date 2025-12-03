from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)

        data["user"] = {
            "id": self.user.id,
            "email": self.user.email,
            "nombre_completo": self.user.get_full_name(),
            "rol": self.user.rol,
            "es_admin": self.user.es_admin,
        }

        return data
