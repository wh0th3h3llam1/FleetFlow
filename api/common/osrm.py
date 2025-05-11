import logging

import osrm
from django.conf import settings

logger = logging.getLogger(__name__)


class TripRequest(osrm.BaseRequest):
    service = "trip"

    def __init__(
        self,
        roundtrip=True,
        source="first",
        destination="last",
        steps=False,
        geometries=osrm.geometries.geojson,
        overview=osrm.overview.full,
        **kwargs
    ):
        super().__init__(**kwargs)

        assert isinstance(roundtrip, bool)
        assert isinstance(steps, bool)
        assert isinstance(geometries, osrm.osrm_geometries)
        assert isinstance(overview, osrm.osrm_overview)

        self.roundtrip = roundtrip
        self.source = source
        self.destination = destination
        self.geometries = geometries
        self.overview = overview

    def get_options(self):
        options = super().get_options()
        options.update(
            {
                "roundtrip": self._encode_bool(self.roundtrip),
                "source": self.source,
                "destination": self.destination,
                "geometries": self.geometries.value,
                "overview": self.overview.value,
            }
        )
        return options


class Client(osrm.Client):

    def trip(self, **kwargs):
        return self._request(TripRequest(**kwargs))


class OSRMClient(object):

    def __init__(self, host=settings.ROUTING_SERVER):
        self.client = Client(host=host)

    def send_request(self, service_name, payload):
        assert service_name in [
            "route",
            "match",
            "nearest",
            "trip",
        ], "Provide a valid service name."
        resp = getattr(self.client, service_name)(**payload)
        if resp["code"].lower() == "ok":
            return resp
        else:
            logger.debug(resp)
            return None

    def check_valid_coordinate(self, coordinate):
        lon, lat = coordinate
        if lon not in range(-180, 180) or lat not in range(-90, 90):
            return False
        return True

    def get_route(self, coordinates, overview=osrm.overview.false, driving_directions=False):
        geometries = osrm.geometries.geojson
        assert coordinates, "Coordinates must be provided."
        assert (
            len(coordinates) > 1
        ), "Number of coordinates needs to be at least two for calculation"
        assert overview in [
            osrm.overview.simplified,
            osrm.overview.full,
            osrm.overview.false,
        ], "Please provide valid value for overview."

        if isinstance(coordinates, list):
            if not all(filter(self.check_valid_coordinate, coordinates)):
                raise ValueError(
                    "a 'longitude' should be -180..180 and 'latitude' should be -90..90 actual {}".format(
                        coordinates
                    )
                )
        else:
            raise ValueError("Coordinates must be list of list.")

        if driving_directions:
            overview = osrm.overview.full

        resp = self.send_request(
            service_name="route",
            payload={"coordinates": coordinates, "overview": overview, "geometries": geometries},
        )
        if resp:
            distance_in_km = round(resp["routes"][0]["distance"] / 1000, 2)
            duration_in_min = resp["routes"][0]["duration"] // 60
            response = {"distance_in_km": distance_in_km, "duration_in_min": duration_in_min}
            if driving_directions:
                driving_directions_resp = resp["routes"][0]["geometry"]
                driving_directions_resp["coordinates"] = driving_directions_resp["coordinates"]
                response["driving_directions"] = driving_directions_resp
            return response

    def get_trip(
        self,
        coordinates,
        roundtrip=False,
        source="any",
        destination="any",
        overview=osrm.overview.false,
        driving_directions=False,
    ):
        geometries = osrm.geometries.geojson
        assert coordinates, "Coordinates must be provided."
        assert (
            len(coordinates) > 1
        ), "Number of coordinates needs to be at least two for calculation"
        assert isinstance(roundtrip, bool), "Please provide valid value for roundtrip {true,false}"
        assert overview in [
            osrm.overview.simplified,
            osrm.overview.full,
            osrm.overview.false,
        ], "Please provide valid value for overview."
        assert source in [
            "first",
            "any",
        ], 'Please provide valid value for " source " parameter = {first,any}'
        assert destination in [
            "last",
            "any",
        ], 'Please provide valid value for " destination " parameter = {first,any}'

        if isinstance(coordinates, list):
            if not all(filter(self.check_valid_coordinate, coordinates)):
                raise ValueError(
                    "'longitude' should be -180..180 and 'latitude' should be -90..90 actual {}".format(
                        coordinates
                    )
                )
        else:
            raise ValueError("Coordinates must be list of list.")

        if not roundtrip:
            source = "first"
            destination = "last"

        if driving_directions:
            overview = osrm.overview.full

        resp = self.send_request(
            service_name="trip",
            payload={
                "coordinates": coordinates,
                "roundtrip": roundtrip,
                "geometries": geometries,
                "source": source,
                "destination": destination,
                "overview": overview,
            },
        )
        if resp:
            trip_distance_in_km = round(resp["trips"][0]["distance"] / 1000, 2)
            trip_duration_in_min = resp["trips"][0]["duration"] // 60
            waypoints = resp["waypoints"]
            legs = resp["trips"][0]["legs"]
            response = {
                "trip_distance_in_km": trip_distance_in_km,
                "trip_duration_in_min": trip_duration_in_min,
                "waypoints": waypoints,
                "legs": legs,
            }
            if driving_directions:
                driving_directions_resp = resp["trips"][0]["geometry"]
                driving_directions_resp["coordinates"] = driving_directions_resp["coordinates"]
                response["driving_directions"] = driving_directions_resp
            return response
