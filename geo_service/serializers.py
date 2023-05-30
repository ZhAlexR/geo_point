from django.contrib.gis import gdal
from rest_framework import serializers
from django.contrib.gis.geos import Point
from django.conf import settings

from geo_service.models import Place


class PlaceSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(source="geom.y")
    longitude = serializers.FloatField(source="geom.x")
    srid = serializers.IntegerField(source="geom.srid", write_only=True)

    class Meta:
        model = Place
        fields = ("id", "name", "description", "latitude", "longitude", "srid")

    def validate_srid(self, srid):
        try:
            gdal.SpatialReference(srid)
        except Exception:
            raise serializers.ValidationError("Invalid SRID.")

        return srid

    def validate(self, attrs):
        latitude = attrs.get("geom").get("y")
        longitude = attrs.get("geom").get("x")
        srid = attrs.get("geom").get("srid")

        point = self._create_point(
            longitude=longitude, latitude=latitude, srid=srid
        )
        if point.y < -180 or point.y > 180:
            raise serializers.ValidationError("Latitude is incorrect.")
        if point.x < -180 or point.y > 180:
            raise serializers.ValidationError("Longitude is incorrect.")
        return attrs

    @staticmethod
    def _create_point(longitude: float, latitude: float, srid: int) -> Point:
        point = Point(x=longitude, y=latitude, srid=srid)
        if srid != settings.DEFAULT_SRID:
            point.transform(settings.DEFAULT_SRID)
        return point


class PlaceCreateSerializer(PlaceSerializer):
    def create(self, validated_data):
        name = validated_data.get("name")
        description = validated_data.get("description")
        latitude = validated_data.get("geom").get("y")
        longitude = validated_data.get("geom").get("x")
        srid = validated_data.get("geom").get("srid")
        place = Place.objects.create(
            name=name,
            description=description,
            geom=self._create_point(
                longitude=longitude, latitude=latitude, srid=srid
            ),
        )
        return place


class PlaceListSerializer(PlaceSerializer):
    description = serializers.SerializerMethodField()

    @staticmethod
    def get_description(obj):
        words = obj.description.split()
        return " ".join(words[:10])


class PlaceDetailSerializer(PlaceSerializer):
    def update(self, instance, validated_data):
        geom = validated_data.pop("geom")
        latitude = geom.get("y")
        longitude = geom.get("x")
        srid = geom.get("srid")
        if all([latitude, longitude, srid]):
            instance.geom = self._create_point(
                longitude=longitude, latitude=latitude, srid=srid
            )
        return super().update(instance, validated_data)


class NearestPointSerializer(PlaceSerializer):
    distance = serializers.SerializerMethodField()

    class Meta(PlaceSerializer.Meta):
        fields = PlaceSerializer.Meta.fields + ("distance",)

    @staticmethod
    def get_distance(obj):
        if hasattr(obj, "distance"):
            return obj.distance.m
        return None
