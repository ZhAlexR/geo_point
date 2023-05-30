from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from rest_framework import serializers
from rest_framework.test import APITestCase
from geo_service.models import Place
from geo_service.serializers import (
    PlaceCreateSerializer,
    PlaceListSerializer,
    PlaceDetailSerializer,
    NearestPointSerializer,
)


class PlaceSerializerTests(APITestCase):

    def setUp(self):
        self.place1 = Place.objects.create(
            name="Place 1",
            description="Description 1",
            geom=Point(49.5883, 34.5514)
        )
        self.place2 = Place.objects.create(
            name="Place 2",
            description="Description 2",
            geom=Point(48.9226, 24.7097)
        )

    def test_place_create_serializer(self):
        data = {
            "name": "Test Place",
            "description": "Test Description",
            "latitude": 34.5514,
            "longitude": 49.5883
        }
        serializer = PlaceCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        place = serializer.save()
        self.assertIsInstance(place, Place)
        self.assertEqual(place.name, "Test Place")
        self.assertEqual(place.description, "Test Description")
        point = Point(49.5883, 34.5514, srid=4326)
        self.assertEqual(place.geom, point)

    def test_place_list_serializer(self):
        place = Place.objects.create(
            name="Test Place",
            description="This is a test place",
            geom=Point(34.5514, 49.5883)
        )
        serializer = PlaceListSerializer(place)
        self.assertEqual(serializer.data["id"], place.id)
        self.assertEqual(serializer.data["name"], "Test Place")
        self.assertEqual(serializer.data["description"], "This is a test place")
        self.assertIsNotNone(serializer.data["latitude"])
        self.assertIsNotNone(serializer.data["longitude"])

    def test_place_detail_serializer(self):
        place = Place.objects.create(
            name="Test Place",
            description="This is a test place",
            geom=Point(34.5514, 49.5883)
        )
        serializer = PlaceDetailSerializer(place)
        self.assertEqual(serializer.data["id"], place.id)
        self.assertEqual(serializer.data["name"], "Test Place")
        self.assertEqual(serializer.data["description"], "This is a test place")
        self.assertIsNotNone(serializer.data["latitude"])
        self.assertIsNotNone(serializer.data["longitude"])

    def test_nearest_point_serializer(self):
        place = Place.objects.create(
            name="Test Place",
            description="This is a test place",
            geom=Point(34.5514, 49.5883)
        )
        place.distance = Distance(m=1000)
        serializer = NearestPointSerializer(place)
        self.assertEqual(serializer.data["id"], place.id)
        self.assertEqual(serializer.data["name"], "Test Place")
        self.assertEqual(serializer.data["description"], "This is a test place")
        self.assertIsNotNone(serializer.data["latitude"])
        self.assertIsNotNone(serializer.data["longitude"])
        self.assertEqual(serializer.data["distance"], 1000)
