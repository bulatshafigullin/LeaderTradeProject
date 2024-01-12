from django.urls import path, include
from users.api.views import (
    LoginAPIView,
    LogoutAPIView,
    VerifyCodeAPIView,
    GetUserAPIView,
    DeleteAPIView,
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("me/", GetUserAPIView.as_view(), name="get-user"),
    path("verify-code/", VerifyCodeAPIView.as_view(), name="verify"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    # path("delete/", DeleteAPIView.as_view(), name="delete"),
]
