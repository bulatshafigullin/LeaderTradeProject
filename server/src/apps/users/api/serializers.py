from django.utils.translation import gettext_lazy as _
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    # phone_number = PhoneNumberField(region="RU")

    class Meta:
        model = User
        fields = ["phone_number", "created_at"]


class RegistrationSerializer(serializers.ModelSerializer):
    # phone_number = PhoneNumberField(region="RU")
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)

    class Meta:
        model = User
        fields = ["phone_number", "password"]

    def validate(self, attrs):
        return attrs

    def create(self, validated_data):
        print(validated_data)
        return User.objects.create_user(**validated_data)


class VerifyCodeSerializer(serializers.ModelSerializer):
    # phone_number = PhoneNumberField(region="RU")

    class Meta:
        model = User
        fields = ["phone_number"]


class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    verify_code = serializers.IntegerField()

    class Meta:
        fields = ["phone_number", "verify_code"]


class LogoutSerializer(serializers.Serializer):
    class Meta:
        fields = ["message"]
