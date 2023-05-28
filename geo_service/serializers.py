from rest_framework import serializers
from django.contrib.gis.geos import Point
from geo_service.models import Place


class PlaceSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(source="geom.y")
    longitude = serializers.FloatField(source="geom.x")

    class Meta:
        model = Place
        fields = ("id", "name", "description", "latitude", "longitude")

    def create(self, validated_data):
        name = validated_data.get("name")
        description = validated_data.get("description")
        latitude = validated_data.get("geom").get("y")
        longitude = validated_data.get("geom").get("x")
        place = Place.objects.create(
            name=name, description=description, geom=Point(longitude, latitude)
        )
        return place

    def update(self, instance, validated_data):
        geom = validated_data.pop("geom", None)
        latitude = geom.get("y")
        longitude = geom.get("x")
        if latitude is not None and longitude is not None:
            instance.geom = Point(longitude, latitude)
        return super().update(instance, validated_data)
