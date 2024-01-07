from typing import Any

from django.utils.translation import gettext_lazy as _
from django_enum_choices.serializers import EnumChoiceField
from rest_framework import serializers

from catalog.models import Make, Brand, Model


class MakeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Make
        fields = ["pk_id", "title"]


class ModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Model
        fields = ["pk_id", "make", "title", "year"]


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ["pk_id", "title", "description"]
