from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status, permissions
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from users.api.serializers import (
    LoginSerializer,
    UserSerializer,
    VerifyCodeSerializer,
    LogoutSerializer,
)
from users.tasks import broadcast_sms_task

User = get_user_model()


class GetUserAPIView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get(self, request: Request) -> Response:
        user = request.user
        serializer = self.serializer_class(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class VerifyCodeAPIView(generics.GenericAPIView):
    serializer_class = VerifyCodeSerializer

    @swagger_auto_schema(request_body=VerifyCodeSerializer)
    def post(self, request: Request) -> Response:
        data = request.data
        phone_number = data["phone_number"]
        is_exists: User | None = User.objects.filter(phone_number=phone_number).first()
        if not is_exists:
            user = User.objects.create(phone_number=phone_number)
        else:
            user = is_exists
        verification = user.verification
        try:
            verification.generate_token()
            task_data = {
                "phone_number": phone_number,
                "verify_code": verification.token,
            }
            broadcast_sms_task.delay(task_data)
            return Response(True, status=status.HTTP_200_OK)
        except Exception:
            return Response(
                "Token generation limit exception", status=status.HTTP_400_BAD_REQUEST
            )


class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request: Request) -> Response:
        data = request.data
        phone_number = data["phone_number"]
        verify_code = data["verify_code"]
        user = get_object_or_404(User, phone_number=phone_number)
        if verify_code == user.verification.token:
            tokens = RefreshToken.for_user(user)
            data = {"refresh": f"{tokens}", "access": f"{tokens.access_token}"}
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response(
                "Wrong verification code", status=status.HTTP_400_BAD_REQUEST
            )


class LogoutAPIView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LogoutSerializer

    def get(self, request: Request) -> Response:
        return Response("Logout success", status=status.HTTP_200_OK)


class DeleteAPIView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request: Request) -> Response:
        user = request.user
        user.delete()
        return Response("User deleted", status=status.HTTP_200_OK)
