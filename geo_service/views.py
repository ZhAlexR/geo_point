from rest_framework import generics

from geo_service.models import Place
from geo_service.serializers import PlaceSerializer


class PlaceListAPIView(generics.ListCreateAPIView):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer


