from django.contrib.gis.geos import Point
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from geo_service.models import Place

GET_NEAREST_POINT_LINK = (
    "http://127.0.0.1:8000/api/geo/places/get_nearest_point/"
)


class PlaceViewSetTestCase(APITestCase):
    def setUp(self):
        self.place1 = Place.objects.create(
            name="Place 1",
            description="Description 1",
            geom=Point(49.5883, 34.5514),
        )
        self.place2 = Place.objects.create(
            name="Place 2",
            description="Description 2",
            geom=Point(48.9226, 24.7097),
        )
        self.place3 = Place.objects.create(
            name="Place 3",
            description="Description 3",
            geom=Point(49.5870, 34.5514),
        )

    def test_get_nearest_point_with_no_distance(self):
        url = GET_NEAREST_POINT_LINK
        params = {
            "latitude": 49.5863,
            "longitude": 34.5514,
        }
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.place3.name)
        self.assertEqual(response.data["description"], self.place3.description)
        self.assertEqual(response.data["latitude"], self.place3.geom.y)
        self.assertEqual(response.data["longitude"], self.place3.geom.x)

    def test_get_nearest_point_with_no_point_inside_distance(self):
        url = GET_NEAREST_POINT_LINK
        params = {"latitude": 49.5863, "longitude": 34.5514, "distance": 10}
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "No nearest point found.")

    def test_get_nearest_point_with_no_data(self):
        url = GET_NEAREST_POINT_LINK
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data, "You have to provide latitude and longitude."
        )

    def test_get_nearest_point_with_invalid_data(self):
        url = GET_NEAREST_POINT_LINK
        params = {
            "latitude": "fffefes",
            "longitude": "adfe3334",
            "distance": 10,
        }
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data, "You have to provide valid latitude and longitude."
        )

    def test_get_nearest_point_with_few_points_inside_distance(self):
        url = GET_NEAREST_POINT_LINK
        params = {
            "latitude": 49.5863,
            "longitude": 34.5514,
            "distance": 10_000_000,
        }
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.place3.name)
        self.assertEqual(response.data["description"], self.place3.description)
        self.assertEqual(response.data["latitude"], self.place3.geom.y)
        self.assertEqual(response.data["longitude"], self.place3.geom.x)

    def test_list(self):
        url = reverse("geoservice:place-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        places = Place.objects.all()
        self.assertEqual(len(response.data), places.count())

    def test_retrieve(self):
        url = reverse("geoservice:place-detail", args=[self.place1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        place = Place.objects.get(id=self.place1.id)

        self.assertEqual(place.name, response.data["name"])
        self.assertEqual(place.description, response.data["description"])
        self.assertEqual(place.geom.y, response.data["latitude"])
        self.assertEqual(place.geom.x, response.data["longitude"])

    def test_create(self):
        url = reverse("geoservice:place-list")
        data = {
            "name": "New Place",
            "description": "New Description",
            "latitude": 50.476831,
            "longitude": 35.676254,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update(self):
        url = reverse("geoservice:place-detail", args=[self.place1.id])

        updated_data = {
            "name": "Updated Place",
            "description": "Updated Description",
            "latitude": 50.476831,
            "longitude": 35.676254,
        }

        response = self.client.put(url, updated_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.place1.refresh_from_db()

        self.assertEqual(self.place1.name, updated_data["name"])
        self.assertEqual(self.place1.description, updated_data["description"])
        self.assertEqual(self.place1.geom.y, updated_data["latitude"])
        self.assertEqual(self.place1.geom.x, updated_data["longitude"])

    def test_partial_update(self):
        url = reverse("geoservice:place-detail", args=[self.place1.id])

        partial_update_data = {
            "latitude": 50.587587,
            "longitude": 36.588157,
        }

        response = self.client.patch(url, partial_update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.place1.refresh_from_db()

        self.assertEqual(self.place1.geom.y, partial_update_data["latitude"])
        self.assertEqual(self.place1.geom.x, partial_update_data["longitude"])

    def test_destroy(self):
        url = reverse("geoservice:place-detail", args=[self.place1.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
