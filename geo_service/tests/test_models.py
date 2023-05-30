from django.contrib.gis.geos import Point
from django.test import TestCase
from geo_service.models import Place


class PlaceModelTests(TestCase):
    def test_place_string_representation(self):
        place = Place.objects.create(
            name="Test Place",
            description="This is a test place",
            geom=Point(34.5514, 49.5883)
        )
        self.assertEqual(str(place), "Test Place")
