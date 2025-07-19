from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.mixins import UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.views import APIView
from django.utils import timezone
from django.core.mail import send_mail
from smurfboost_backend.users.models import EmailOTP, User
from .serializers import (
    UserSerializer, SendOTPSerializer, VerifyOTPSerializer,
    GoogleSocialLoginSerializer, DiscordSocialLoginSerializer,
    RegisterSerializer
)
import random
import requests
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny

class UserViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = "pk"

    def get_queryset(self, *args, **kwargs):
        assert isinstance(self.request.user.id, int)
        return self.queryset.filter(id=self.request.user.id)

    @action(detail=False)
    def me(self, request):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class RegisterView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        if User.objects.filter(email=email).exists():
            return Response({'detail': 'User already registered.'}, status=400)
        user = User.objects.create_user(email=email, password=password, is_active=False, is_verified=False)
        code = f"{random.randint(100000, 999999)}"
        EmailOTP.objects.create(email=email, code=code)
        send_mail(
            'Your OTP Code',
            f'Your OTP code is {code}',
            'no-reply@smurfboost.com',
            [email],
            fail_silently=True,
        )
        return Response({'detail': 'Registration successful. Please verify your email with the OTP sent.'}, status=201)

class SendOTPView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        user = authenticate(request, username=email, password=password)
        if user is None:
            return Response({'detail': 'No credentials or invalid credentials.'}, status=400)
        if not user.is_verified:
            return Response({'detail': 'User is not verified. Please verify your email first.'}, status=403)
        code = f"{random.randint(100000, 999999)}"
        EmailOTP.objects.create(email=email, code=code)
        send_mail(
            'Your OTP Code',
            f'Your OTP code is {code}',
            'no-reply@smurfboost.com',
            [email],
            fail_silently=True,
        )
        return Response({'detail': 'OTP sent.'}, status=200)

class VerifyOTPView(APIView):

    permission_classes = [AllowAny]
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        code = serializer.validated_data['code']
        now = timezone.now()
        otp = EmailOTP.objects.filter(email=email, code=code, is_used=False).order_by('-created_at').first()
        if not otp or (now - otp.created_at).total_seconds() > 900:
            return Response({'detail': 'Invalid or expired OTP.'}, status=400)
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({'detail': 'User not found.'}, status=404)
        user.is_active = True
        user.is_verified = True
        user.save()
        otp.is_used = True
        otp.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })

class GoogleSocialLoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = GoogleSocialLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']
        # In production, use google.oauth2.id_token.verify_oauth2_token
        # For now, do a simple call to Google tokeninfo endpoint
        resp = requests.get(f'https://oauth2.googleapis.com/tokeninfo?id_token={token}')
        if resp.status_code != 200:
            return Response({'detail': 'Invalid Google token.'}, status=400)
        email = resp.json().get('email')
        if not email:
            return Response({'detail': 'No email found in Google token.'}, status=400)
        user, created = User.objects.get_or_create(email=email)
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })

class DiscordSocialLoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = DiscordSocialLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']
        # Exchange token for user info
        headers = {'Authorization': f'Bearer {token}'}
        resp = requests.get('https://discord.com/api/users/@me', headers=headers)
        if resp.status_code != 200:
            return Response({'detail': 'Invalid Discord token.'}, status=400)
        data = resp.json()
        email = data.get('email')
        if not email:
            return Response({'detail': 'No email found in Discord account.'}, status=400)
        user, created = User.objects.get_or_create(email=email)
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })

class RegisterWithOTPView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = RegisterWithOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        if User.objects.filter(email=email).exists():
            return Response({'detail': 'User already registered.'}, status=400)
        user = User.objects.create_user(email=email, password=password)
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
