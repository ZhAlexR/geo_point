from django.urls import path

from geo_service.views import PlaceListAPIView

app_name = "geo_service"

urlpatterns = [
    path("places/", PlaceListAPIView.as_view(), name="place-list"),
]
