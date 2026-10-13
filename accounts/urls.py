from django.urls import path
from .views import (
    SignupAPIView,
    VerifySignupAPIView,
    ResendSignupOTPAPIView,
    LoginAPIView,
    VerifyLoginAPIView,
    ResendLoginOTPAPIView,
    LogoutAPIView,
    MeAPIView,
    EditProfileAPIView,
    EditProfileImageAPIView,
    DeleteProfileImageAPIView,
    GoogleLoginAPIView,
    RefreshTokenView
)

urlpatterns = [
    path("signup/", SignupAPIView.as_view()),
    path("signup/verify/", VerifySignupAPIView.as_view()),
    path("signup/resend-otp/", ResendSignupOTPAPIView.as_view()),
    path("login/", LoginAPIView.as_view()),
    path("login/verify/", VerifyLoginAPIView.as_view()),
    path("login/resend-otp/", ResendLoginOTPAPIView.as_view()),

    path("logout/", LogoutAPIView.as_view()),

    path("me/", MeAPIView.as_view()),
    path("me/edit/", EditProfileAPIView.as_view()),
    path("me/profile-image/", EditProfileImageAPIView.as_view()),
    path("me/profile-image/delete/", DeleteProfileImageAPIView.as_view()),
    path("token/refresh/",RefreshTokenView.as_view(),name="token-refresh"),
    path("google/",GoogleLoginAPIView.as_view())
]