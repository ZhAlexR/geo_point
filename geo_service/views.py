from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance as DistanceMeasure
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from geo_service.models import Place
from geo_service.serializers import (
    NearestPointSerializer,
    PlaceListSerializer,
    PlaceDetailSerializer,
    PlaceCreateSerializer,
)


class PlaceViewSet(viewsets.ModelViewSet):
    queryset = Place.objects.all()

    def get_serializer_class(self):
        if self.action == "get_nearest_point":
            return NearestPointSerializer
        if self.action == "list":
            return PlaceListSerializer
        if self.action in ["retrieve", "update", "partial_update", "destroy"]:
            return PlaceDetailSerializer
        return PlaceCreateSerializer

    @action(detail=False, methods=["get"])
    def get_nearest_point(self, request):
        latitude = float(request.query_params.get("latitude"))
        longitude = float(request.query_params.get("longitude"))
        distance = request.query_params.get("distance")

        point = Point(longitude, latitude, srid=4326)
        nearest_point = Place.objects.annotate(
            distance=Distance("geom", point)
        )
        if distance:
            nearest_point = nearest_point.filter(
                distance__lte=DistanceMeasure(m=int(distance))
            )
        nearest_point = nearest_point.order_by("distance").first()

        if nearest_point:
            serializer = self.get_serializer(nearest_point)
            return Response(serializer.data)
        else:
            return Response(
                {"detail": "No nearest point found."},
                status=status.HTTP_404_NOT_FOUND,
            )
