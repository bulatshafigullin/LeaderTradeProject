from typing import Any

from django_enum_choices.serializers import EnumChoiceField
from rest_framework import serializers

from src.apps.actions.models import FormApplication, CallRequest, Portfolio, Review
from catalog.api.serializers import MakeSerializer
from src.other.enums import FormApplicationStatus, CallRequestStatus


class FormApplicationSerializer(serializers.ModelSerializer):
    status = EnumChoiceField(enum_class=FormApplicationStatus)

    class Meta:
        model = FormApplication
        fields = "__all__"


class CallRequestSerializer(serializers.ModelSerializer):
    status = EnumChoiceField(enum_class=CallRequestStatus)

    class Meta:
        model = CallRequest
        fields = "__all__"


class PortfolioSerializer(serializers.ModelSerializer):
    make = serializers.SerializerMethodField()

    def get_make(self, obj: Portfolio) -> Any:
        return MakeSerializer(obj.make).data

    class Meta:
        model = Portfolio
        fields = ["pk_id", "make", "slug", "image", "product"]


class PortfolioDetailSerializer(serializers.ModelSerializer):
    make = serializers.SerializerMethodField()

    def get_make(self, obj: Portfolio) -> Any:
        return MakeSerializer(obj.make).data

    def get_gallery(self, obj: Portfolio) -> list[str]:
        return [image for image in obj.gallery.all()]

    class Meta:
        model = Portfolio
        fields = ["pk_id", "make", "slug", "description", "image", "product", "gallery"]


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            "pk_id",
            "image",
            "text",
            "date",
        ]
