from django.urls import path, include
from rest_framework import routers

from geo_service.views import PlaceViewSet

app_name = "geo_service"

router = routers.DefaultRouter()
router.register("places", PlaceViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
