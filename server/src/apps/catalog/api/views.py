from rest_framework import generics, status
from rest_framework.request import Request
from rest_framework.response import Response

from catalog.api.serializers import (
    MakeSerializer,
    ModelSerializer,
    BrandSerializer,
)
from catalog.models import Make, Model, Brand


class MakeListAPIView(generics.ListAPIView):
    serializer_class = MakeSerializer
    queryset = Make.objects.all()

    def get_queryset(self) -> list[Make]:
        return self.queryset


# class MakeDetailAPIView(generics.GenericAPIView):
#     serializer_class = MakeSerializer
#
#     def get(self, request: Request, pk_id: str) -> Response:
#         make = Make.objects.filter(pk_id=pk_id).first()
#         if make is None:
#             return Response("Make not found", status=status.HTTP_404_NOT_FOUND)
#         serializer = MakeSerializer(make)
#         return Response(serializer.data, status=status.HTTP_200_OK)


class ModelListAPIView(generics.ListAPIView):
    serializer_class = ModelSerializer
    queryset = Model.objects.all()

    def get_queryset(self) -> list[Model]:
        return self.queryset


class ModelsByMakeAPIView(generics.GenericAPIView):
    serializer_class = ModelSerializer

    def get(self, request: Request, make_pk: int) -> Response:
        models = Model.objects.filter(make__pk_id=make_pk)
        serializer_list = ModelSerializer(models, many=True)
        return Response(serializer_list.data, status=status.HTTP_200_OK)


class BrandListAPIView(generics.ListAPIView):
    serializer_class = BrandSerializer
    queryset = Brand.objects.all()

    def get_queryset(self) -> list[Brand]:
        return self.queryset
