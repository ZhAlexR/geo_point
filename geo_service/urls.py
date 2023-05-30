from django.urls import path, include
from rest_framework import routers

from geo_service.views import PlaceViewSet


router = routers.DefaultRouter()
router.register("places", PlaceViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "geoservice"
