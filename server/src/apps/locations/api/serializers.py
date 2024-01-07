from django.utils.translation import gettext_lazy as _
from django_enum_choices.serializers import EnumChoiceField
from rest_framework import serializers

from locations.models import City, Address, Shop, Worktime


class WorktimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Worktime
        fields = ["day_of_week", "start_time", "end_time"]


class ShopSerializer(serializers.ModelSerializer):
    worktime_list = serializers.SerializerMethodField()

    def get_worktime_list(self, obj: Shop) -> list:
        result = []
        for worktime in obj.work_times:
            serializer = WorktimeSerializer(worktime)
            result.append(serializer.data)
        return result

    class Meta:
        model = Shop
        fields = ["pk_id", "address", "email", "worktime_list"]


class AddressSerializer(serializers.ModelSerializer):
    shops = serializers.SerializerMethodField()

    def get_shops(self, obj: Address) -> list[int]:
        return [shop.pk_id for shop in obj.shops.all()]

    class Meta:
        model = Address
        fields = ["pk_id", "city", "street", "house", "apartment", "shops"]


class AddressDetailSerializer(serializers.ModelSerializer):
    shops = serializers.SerializerMethodField()

    def get_shops(self, obj: Address) -> list:
        return [ShopSerializer(shop).data for shop in obj.shops.all()]

    class Meta:
        model = Address
        fields = ["pk_id", "city", "street", "house", "apartment", "shops"]


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ["pk_id", "title"]


class CityDetailSerializer(serializers.ModelSerializer):
    addresses = serializers.SerializerMethodField()
    shops = serializers.SerializerMethodField()

    def get_addresses(self, obj: City) -> list:
        return [AddressSerializer(address).data for address in obj.addresses.all()]

    def get_shops(self, obj: City) -> list:
        return [ShopSerializer(shop).data for shop in obj.shops.all()]

    class Meta:
        model = City
        fields = ["pk_id", "title", "addresses", "shops"]
