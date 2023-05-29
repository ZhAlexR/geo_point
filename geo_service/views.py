from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance as DistanceMeasure
from drf_spectacular.utils import (
    OpenApiParameter,
    extend_schema,
    OpenApiExample,
)
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

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="latitude",
                type=float,
                description="Latitude coordinate for the reference point.",
                required=True,
                location=OpenApiParameter.QUERY,
                examples=[
                    OpenApiExample(
                        value=49.5883,
                        name="Poltava example",
                        description="Latitude coordinate for Poltava",
                    ),
                    OpenApiExample(
                        value=48.9226,
                        name="Ivano-Frankivsk example",
                        description="Latitude coordinate for Ivano-Frankivsk",
                    ),
                ],
            ),
            OpenApiParameter(
                name="longitude",
                type=float,
                description="Longitude coordinate for the reference point.",
                required=True,
                location=OpenApiParameter.QUERY,
                examples=[
                    OpenApiExample(
                        value=34.5514,
                        name="Poltava example",
                        description="Longitude coordinate for Poltava",
                    ),
                    OpenApiExample(
                        value=24.7097,
                        name="Ivano-Frankivsk example",
                        description="Longitude coordinate for Ivano-Frankivsk",
                    ),
                ],
            ),
            OpenApiParameter(
                name="distance",
                type=int,
                description="Maximum distance in meters from the reference point (optional).",
                required=False,
                location=OpenApiParameter.QUERY,
                examples=[
                    OpenApiExample(
                        value="",
                        name="No value",
                        description="Example distance value 1",
                    ),
                    OpenApiExample(
                        value=1000,
                        name="1 km example",
                        description="Example distance value 1",
                    ),
                    OpenApiExample(
                        value=500000,
                        name="500 km example",
                        description="Example distance value 2",
                    ),
                ],
            ),
        ],
        responses={200: NearestPointSerializer},
    )
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

    @extend_schema(
        responses={200: PlaceListSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        parameters=[],
        responses={200: PlaceDetailSerializer},
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        request=PlaceCreateSerializer,
        responses={201: PlaceDetailSerializer},
        examples=[
            OpenApiExample(
                name="Add Chernivtsi",
                description="This example shows how to add Chernivtsi to database.",
                value={
                    "name": "Chernivtsi",
                    "description": "Chernivtsi is the administrative, political and religious center of Chernivtsi "
                    "region, an important cultural and scientific and educational center of Ukraine",
                    "latitude": 48.291771,
                    "longitude": 25.934528,
                },
            ),
            OpenApiExample(
                name="Add Belhorod",
                description="This example shows how to add Belhorod to database.",
                value={
                    "name": "Belhorod",
                    "description": "Bilhorod is the capital, political and religious center of Belhorod People "
                    "Republic",
                    "latitude": 50.476831,
                    "longitude": 35.676254,
                },
            ),
        ],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        request=PlaceCreateSerializer,
        responses={200: PlaceDetailSerializer},
        examples=[
            OpenApiExample(
                name="Change Bilhorod",
                description="This example shows how to add Bilhorod in database.",
                value={
                    "name": "Bilhorod",
                    "description": "Bilhorod is the capital, political and religious center of Bilhorod People "
                    "Republic",
                    "latitude": 50.476831,
                    "longitude": 35.676254,
                },
            ),
        ],
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        request=PlaceCreateSerializer,
        responses={200: PlaceDetailSerializer},
        examples=[
            OpenApiExample(
                name="Change wrong Bilhorod coordinates",
                description="Changing the coordinates of Grayvoron to Bilhorod (everyone is wrong sometimes)",
                value={"latitude": 50.587587, "longitude": 36.588157},
            ),
        ],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        responses={204: "No Content"},
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
