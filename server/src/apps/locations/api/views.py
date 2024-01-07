from rest_framework import generics, status
from rest_framework.request import Request
from rest_framework.response import Response

from locations.api.pagination import LocationPagination
from locations.api.serializers import (
    CitySerializer,
    AddressSerializer,
    ShopSerializer,
    CityDetailSerializer,
    AddressDetailSerializer,
)
from locations.models import City, Address, Shop


class CityListAPIView(generics.ListAPIView):
    pagination_class = LocationPagination
    queryset = City.objects.all()
    serializer_class = CitySerializer

    def get_queryset(self) -> list[City]:
        return self.queryset


class CityDetailAPIView(generics.GenericAPIView):
    serializer_class = CityDetailSerializer

    def get(self, request: Request, title: str) -> Response:
        city = City.objects.filter(title=title).first()
        if city is None:
            return Response("City not found", status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(city)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AddressListAPIView(generics.ListAPIView):
    pagination_class = LocationPagination
    queryset = Address.objects.all()
    serializer_class = AddressSerializer

    def get_queryset(self) -> list[Address]:
        return self.queryset


class AddressDetailAPIView(generics.GenericAPIView):
    serializer_class = AddressDetailSerializer

    def get(self, request: Request, pk_id: int) -> Response:
        address = Address.objects.filter(pk_id=pk_id).first()
        if address is None:
            return Response("Address not found", status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(address)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ShopListAPIView(generics.ListAPIView):
    pagination_class = LocationPagination
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer

    def get_queryset(self) -> list[Shop]:
        return self.queryset
