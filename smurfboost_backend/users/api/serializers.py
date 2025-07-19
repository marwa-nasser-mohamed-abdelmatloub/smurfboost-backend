from rest_framework import serializers

from smurfboost_backend.users.models import User, EmailOTP


class UserSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = ["name", "url"]

        extra_kwargs = {
            "url": {"view_name": "api:user-detail", "lookup_field": "pk"},
        }


class SendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)

class GoogleSocialLoginSerializer(serializers.Serializer):
    token = serializers.CharField()

class DiscordSocialLoginSerializer(serializers.Serializer):
    token = serializers.CharField()
