from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter
from django.urls import path

from smurfboost_backend.users.api.views import UserViewSet, SendOTPView, VerifyOTPView, GoogleSocialLoginView, DiscordSocialLoginView, RegisterView

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("users", UserViewSet)


app_name = "api"
urlpatterns = router.urls

urlpatterns += [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/send-otp/', SendOTPView.as_view(), name='send-otp'),
    path('auth/verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('auth/social/google/', GoogleSocialLoginView.as_view(), name='google-social-login'),
    path('auth/social/discord/', DiscordSocialLoginView.as_view(), name='discord-social-login'),
]
