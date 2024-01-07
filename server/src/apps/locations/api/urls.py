from django.urls import path

from locations.api.serializers import CitySerializer
from locations.api.views import (
    CityListAPIView,
    AddressListAPIView,
    CityDetailAPIView,
    AddressDetailAPIView,
    ShopListAPIView,
)

# from apps.news.api.views import NewsDetailAPIView

urlpatterns = [
    path("cities/", CityListAPIView.as_view(), name="city-list"),
    path("shops/", ShopListAPIView.as_view(), name="shop-list"),
    path("addresses/", AddressListAPIView.as_view(), name="address-list"),
    path("cities/detail/<title>/", CityDetailAPIView.as_view(), name="city-detail"),
    path(
        "addresses/detail/<pk_id>", AddressDetailAPIView.as_view(), name="address-list"
    ),
]
