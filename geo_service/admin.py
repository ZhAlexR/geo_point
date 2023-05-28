from django.contrib.gis import admin
from geo_service.models import Place


@admin.register(Place)
class ShopAdmin(admin.OSMGeoAdmin):
    list_display = ("name", "description", "geom")
