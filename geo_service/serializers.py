from rest_framework import serializers
from geo_service.models import Place


class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = ("name", "description", "geom")
