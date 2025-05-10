import json

from django.contrib.gis.geos import GEOSGeometry


def generate_zone_feature_collections(zones):
    zone_section = {"type": "FeatureCollection", "features": []}
    for zone in zones:
        zone_section["features"].append(
            {
                "type": "Feature",
                "properties": {
                    "id": zone.id,
                    "zone_name": zone.zone_name,
                },
                "geometry": json.loads(GEOSGeometry(zone.geofence).geojson),
            }
        )
    return zone_section
