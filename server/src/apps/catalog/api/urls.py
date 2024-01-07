from django.urls import path

from catalog.api.views import (
    BrandListAPIView,
    MakeListAPIView,
    ModelListAPIView,
    ModelsByMakeAPIView,
)

urlpatterns = [
    path("models/", ModelListAPIView.as_view(), name="models"),
    path("makes/", MakeListAPIView.as_view(), name="makes"),
    path("brands/", BrandListAPIView.as_view(), name="brands"),
    path("models/<make_pk>", ModelsByMakeAPIView.as_view(), name="models-by-make"),
]
