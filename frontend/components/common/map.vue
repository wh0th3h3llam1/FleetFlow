<template>
  <div class="card-body table-responsive" style="position: relative">
    <div
      id="map"
      class="map"
      :style="{ width: mapWidth, height: mapHeight }"
    ></div>
    <v-icon id="delete-button" class="map-delete-icon" v-if="page == 'zone'" style="display: block"
      >mdi-delete</v-icon
    >

    <div class="legend" v-if="this.page == 'trip'">
      <h3>Information</h3>
      <hr style="margin: 10px 0px" />
      <div>
        <!-- ==== Note : Driver Location Showing in Future =============
         <div style="display:flex;align-items:center;margin-bottom:10px;">
            <img style="height: 20px;width: 20px;margin-right:10px"
                src="{%static 'img/truck.png'%}"></img>
            <span>Last Driver Location</span>
        </div> -->
        <div v-for="(legend, index) in tripLegends" :key="index" class="d-flex">
          <div>
            <v-img contain class="legend-img" :src="legend.marker"></v-img>
          </div>
          <span>{{ legend.text }}</span>
        </div>

        <div
          style="display: flex; align-items: center; margin-bottom: 15px"
          
        >
          <div
            style="
              height: 2px;
              width: 20px;
              margin-right: 20px;
              background-color: #14895f;
            "
          ></div>
          <span>Planned Route</span>
        </div>
        <!--==== Note : Actual Driver route Showing in Future =============
         <div style="display:flex;align-items:center">
            <div
                style="height: 10px;width: 20px;margin-right:10px;border-top: 3px dashed #7bc268 ;">
            </div>
            <span style="padding-bottom: 8px;">Actual Route</span>
        </div> -->
      </div>
    </div>
  </div>
</template>

<script>
import baseIcon from "@/static/base.png";
import unattemptedPng from "@/static/location_red_icon.png";
import failedPng from "@/static/location_black_icon.png";
import complatedPng from "@/static/location_blue_icon.png";
export default {
  props: {
    mapWidth: String,
    mapHeight: String,
    formType: {
      type: String,
      default: "add",
    },
    coordination: Object,
    page: String,
  },
  data() {
    return {
      map: null,
      data: {},
      baseIcon: baseIcon,
      failedMarker: failedPng,
      unattemptedMarker: unattemptedPng,
      completedMarker: complatedPng,
      tripLegends: [
        { text: "Successful Order", marker: complatedPng },
        { text: "Failed Order", marker: failedPng },
        { text: "Unattempted Order", marker: unattemptedPng },
      ],
      markers: [],
      apiKey: process.env.mapsKey,
      lat: 37.335964,
      lng: -121.881291,
      polyOptions: {
        strokeColor: "#FF0000",
        strokeOpacity: 0.8,
        strokeWeight: 2,
        fillColor: "#00FF00",
        fillOpacity: 0.35,
        editable: true,
      },
      feature: null,
      selectedShape: null,
    };
  },
  methods: {
    orderLocation(locations) {
      let base = {
        url: this.baseIcon,
        scaledSize: new google.maps.Size(40, 40), // scaled size
        origin: new google.maps.Point(0, -6), // origin
        anchor: new google.maps.Point(20, 40),
      };
      let failedMarker = {
        url: this.failedMarker,
        scaledSize: new google.maps.Size(42, 42), // scaled size
        origin: new google.maps.Point(0, -6), // origin
        anchor: new google.maps.Point(21, 42), // anchor
      };
      let statusunattemptedMarker = {
        url: this.unattemptedMarker,
        scaledSize: new google.maps.Size(42, 42), // scaled size
        origin: new google.maps.Point(0, -6), // origin
        anchor: new google.maps.Point(21, 42), // anchor
      };
      let statuscompletedMarker = {
        url: this.completedMarker,
        scaledSize: new google.maps.Size(42, 42), // scaled size
        origin: new google.maps.Point(0, -6), // origin
        anchor: new google.maps.Point(21, 42), // anchor
      };

      let status = this.$store.state.order.orderDetailStore.order.status;

      if (locations.length !== 0) {
        var bounds = new google.maps.LatLngBounds();

        let marker = new google.maps.Marker();

        this.markers.forEach((marker, index) => {
          marker.setMap(null);
        });

        for (const i in locations) {
          if (i == "drop_point") {
            let position = new google.maps.LatLng(
              locations[i]["coordinates"][1],
              locations[i]["coordinates"][0]
            );
            bounds.extend(position);
            marker = new google.maps.Marker({
              position: position,
              map: this.map,
              icon: checkStatus(status),
            });
            this.markers.push(marker);
          } else {
            let position = new google.maps.LatLng(
              locations[i]["coordinates"][1],
              locations[i]["coordinates"][0]
            );
            bounds.extend(position);
            marker = new google.maps.Marker({
              position: position,
              map: this.map,
              icon: base,
            });
            this.markers.push(marker);
          }
        }
        bounds.getCenter();
        this.map.fitBounds(bounds);
      }
      function checkStatus(status) {
        switch (status) {
          case "unassigned":
            return statusunattemptedMarker;
          case "assigned":
            return statusunattemptedMarker;
          case "pickedup":
            return statusunattemptedMarker;
          case "successful":
            return statuscompletedMarker;
          case "failed":
            return failedMarker;

          default:
            return null;
        }
      }
    },
    childMethod(route, location) {
      let base = {
        url: this.baseIcon,
        scaledSize: new google.maps.Size(40, 40), // scaled size
        origin: new google.maps.Point(0, -6), // origin
        anchor: new google.maps.Point(20, 40),
      };
      let failedMarker = {
        url: this.failedMarker,
        scaledSize: new google.maps.Size(42, 42),
        origin: new google.maps.Point(0, -6), // origin
        anchor: new google.maps.Point(21, 42), // anchor
      };
      let statusunattemptedMarker = {
        url: this.unattemptedMarker,
        scaledSize: new google.maps.Size(42, 42), // scaled size
        origin: new google.maps.Point(0, -6), // origin
        anchor: new google.maps.Point(21, 42), // anchor
      };
      let statuscompletedMarker = {
        url: this.completedMarker,
        scaledSize: new google.maps.Size(42, 42), // scaled size
        origin: new google.maps.Point(0, -6), // origin
        anchor: new google.maps.Point(21, 42), // anchor
      };

      // ===== Set Marker ======================================

      if (
        location &&
        Object.keys(location).length !== 0 &&
        location.constructor === Object
      ) {
        this.markers.forEach((marker, index) => {
          marker.setMap(null);
        });

        var bounds = new google.maps.LatLngBounds();
        let infowindow = new google.maps.InfoWindow({ maxWidth: 470 });
        const baseMarker = new google.maps.Marker({
          position: {
            lat: location.warehouse.coordinates[1],
            lng: location.warehouse.coordinates[0],
          },
          map: this.map,
          icon: base,
        });

        baseMarker.setMap(this.map);
        bounds.extend(baseMarker.position);
        this.markers.push(baseMarker);
        google.maps.event.addListener(
          baseMarker,
          "mouseover",
          (function (baseMarker) {
            return function () {
              let html = "";
              html += `<ul class=" dms-map-tooltip">
                        <li><h5 class=" dms-map-tooltip-main-title">Base Address</h5></li>
                        <li class="d-flex pa-0 ma-0">
                          <span class="dms-map-tooltip-title pa-0 ma-0"></span>
                          <h6 class="dms-map-tooltip-title-text"> ${location.warehouse.address}</h6>
                        </li>
                        </ul>`;
              infowindow.setContent(html);
              infowindow.open(this.map, baseMarker);
            };
          })(baseMarker)
        );
        baseMarker.addListener("mouseout", function () {
          infowindow.close();
        });

        location.locations.forEach((data, index) => {
          const marker = new google.maps.Marker({
            position: { lat: data.coordinates[1], lng: data.coordinates[0] },
            map: this.map,
            icon:
              data.status == "complated"
                ? statuscompletedMarker
                : data.status == "failed"
                ? failedMarker
                : statusunattemptedMarker,
            label: {
              color: "#122D4E",
              fontWeight: "bold",
              fontSize: "14px",
              text: "" + data.sequence_number,
            },
          });
          marker.setMap(this.map);
          bounds.extend(marker.position);
          this.markers.push(marker);

          let infowindow = new google.maps.InfoWindow({ maxWidth: 470 });

          google.maps.event.addListener(
            marker,
            "mouseover",
            (function (marker) {
              return function () {
                let html = "";
                html += `<ul class=" dms-map-tooltip">
                        <li><h5 class=" dms-map-tooltip-main-title">Trip Detail</h5></li>
                        <li class="d-flex ">
                          <span class="dms-map-tooltip-title">Order No</span>
                          <h6 class="dms-map-tooltip-title-text"> ${data.reference_number}</h6>
                        </li>
                        <li class="d-flex ">
                          <span class="dms-map-tooltip-title">Customer Name</span>
                          <h6 class="dms-map-tooltip-title-text"> ${data.customer_name}</h6>
                        </li>
                        <li class="d-flex ">
                          <span class="dms-map-tooltip-title">Date</span>
                          <h6 class="dms-map-tooltip-title-text"> ${data.eta}</h6>
                        </li>
                        <li class="d-flex ">
                          <span class="dms-map-tooltip-title">Address</span>
                          <h6 class="dms-map-tooltip-title-text"> ${data.address}</h6>
                        </li>
                        </ul>`;
                infowindow.setContent(html);
                infowindow.open(this.map, marker);
              };
            })(marker)
          );
          marker.addListener("mouseout", function () {
            infowindow.close();
          });
        });

        bounds.getCenter();
        this.map.fitBounds(bounds);
      } else {
        this.$notifier.showMessage({
          content: "Location not found",
          color: "error",
        });
      }

      // ===== Set Route ======================================

      if (route !== null) {
        let getroute = route.features[0].geometry.coordinates;
        let newRoutedata = [];
        getroute.forEach((data, index) => {
          newRoutedata.push({ lat: data[1], lng: data[0] });
        });
        let routeLine = new google.maps.Polyline({
          path: newRoutedata,
          geodesic: true,
          strokeColor: "#14895f",
          strokeOpacity: 1.0,
          strokeWeight: 2,
        });
        routeLine.setMap(this.map);
        this.markers.push(routeLine);
      }
    },
    initMap(center = null) {
      let that = this;
      let drawingManager;
      if (!center) var center = new google.maps.LatLng(this.lat, this.lng);

      this.map = new google.maps.Map(document.getElementById("map"), {
        zoom: 10,
        center: center,
        disableDefaultUI: false,
      });

      if (this.page == "zone") {
        drawingManager = new google.maps.drawing.DrawingManager({
          map: this.map,
          polygonOptions: this.polyOptions,
          rectangleOptions: this.polyOptions,
          drawingControl: true,
          drawingControlOptions: {
            position: google.maps.ControlPosition.RIGHT_TOP,
            editable: true,
            drawingModes: [
              google.maps.drawing.OverlayType.POLYGON,
              google.maps.drawing.OverlayType.RECTANGLE,
            ],
          },
        });

        google.maps.event.addListener(
          drawingManager,
          "overlaycomplete",
          function (event) {
            switch (event.type) {
              case google.maps.drawing.OverlayType.RECTANGLE:
                var b = event.overlay.getBounds(),
                  p = [
                    b.getSouthWest(),
                    {
                      lat: b.getSouthWest().lat(),
                      lng: b.getNorthEast().lng(),
                    },
                    b.getNorthEast(),
                    {
                      lng: b.getSouthWest().lng(),
                      lat: b.getNorthEast().lat(),
                    },
                  ];

                that.feature = new google.maps.Data.Feature({
                  geometry: new google.maps.Data.Polygon([p]),
                });

                drawingManager.setDrawingMode(null);
                drawingManager.setOptions({
                  drawingControl: false,
                });

                var newShape = event.overlay;
                newShape.type = event.type;
                google.maps.event.addListener(
                  newShape,
                  "bounds_changed",
                  function () {
                    that.setSelection(newShape);
                  }
                );
                that.setSelection(newShape);

                window.google.maps.event.addListener(
                  newShape,
                  "set_at",
                  function () {
                    that.feature = new google.maps.Data.Feature({
                      geometry: new google.maps.Data.Polygon([p]),
                    });
                  }
                );

                break;
              case google.maps.drawing.OverlayType.POLYGON:
                that.feature = new google.maps.Data.Feature({
                  geometry: new google.maps.Data.Polygon([
                    event.overlay.getPath().getArray(),
                  ]),
                });

                drawingManager.setDrawingMode(null);
                drawingManager.setOptions({
                  drawingControl: false,
                });

                var newShape = event.overlay;
                newShape.type = event.type;
                google.maps.event.addListener(newShape, "click", function () {
                  that.setSelection(newShape);
                });
                that.setSelection(newShape);

                window.google.maps.event.addListener(
                  newShape.getPath(),
                  "insert_at",
                  function () {
                    that.feature = new google.maps.Data.Feature({
                      geometry: new google.maps.Data.Polygon([
                        event.overlay.getPath().getArray(),
                      ]),
                    });
                  }
                );

                window.google.maps.event.addListener(
                  newShape.getPath(),
                  "set_at",
                  function () {
                    that.feature = new google.maps.Data.Feature({
                      geometry: new google.maps.Data.Polygon([
                        event.overlay.getPath().getArray(),
                      ]),
                    });
                  }
                );

                break;
            }
          }
        );

        google.maps.Map.prototype.getGeoJson = function (callback) {
          var geo = { type: "FeatureCollection", features: [] },
            fx = function (g, t) {
              var thatnew = [];
              var arr;
              var f = {
                MultiLineString: "LineString",
                LineString: "Point",
                MultiPolygon: "Polygon",
                Polygon: "LinearRing",
                LinearRing: "Point",
                MultiPoint: "Point",
              };

              switch (t) {
                case "Point":
                  g = g.get ? g.get() : g;
                  return [g.lng(), g.lat()];
                  break;
                default:
                  arr = g.getArray();
                  for (var i = 0; i < arr.length; ++i) {
                    thatnew.push(fx(arr[i], f[t]));
                  }
                  if (
                    t == "LinearRing" &&
                    thatnew[0] !== thatnew[thatnew.length - 1]
                  ) {
                    thatnew.push([thatnew[0][0], thatnew[0][1]]);
                  }
                  return thatnew;
              }
            };

          this.data.forEach(function (feature) {
            let _feature = { type: "Feature", properties: {} };
            let _id = feature.getId();
            let _geometry = feature.getGeometry();
            let _type = _geometry.getType();
            let _coordinates = fx(_geometry, _type);

            _feature.geometry = { type: _type, coordinates: _coordinates };
            if (typeof _id === "string") {
              _feature.id = _id;
            }

            geo.features.push(_feature);
            feature.forEachProperty(function (v, k) {
              _feature.properties[k] = v;
            });
          });
          if (typeof callback === "function") {
            callback(geo);
          }
          return geo;
        };

        google.maps.event.addDomListener(
          document.getElementById("delete-button"),
          "click",
          deleteSelectedShape
        );
        function deleteSelectedShape() {
          if (that.selectedShape) {
            that.selectedShape.setMap(null);
            that.feature = null;
            drawingManager.setOptions({
              drawingControl: true,
            });
          }
        }
      }

      if (this.page == "zone" && this.formType == "edit") {
        let data = this.coordination.coordinates[0];
        const outerCoords = [];
        var bounds = new google.maps.LatLngBounds();
        data.forEach((element, index) => {
          outerCoords.push({ lat: element[1], lng: element[0] });
          bounds.extend({ lat: element[1], lng: element[0] });
        });

        var flightPath = new google.maps.Polygon({
          path: outerCoords,
          editable: true,
          strokeColor: "#0000FF",
          strokeOpacity: 1,
          strokeWeight: 2,
          fillColor: "#00FF00",
          fillOpacity: 0.35,
        });

        flightPath.setMap(this.map);
        bounds.getCenter();
        this.map.fitBounds(bounds);
        that.setSelection(flightPath);

        that.feature = new google.maps.Data.Feature({
          geometry: new google.maps.Data.Polygon([
            flightPath.getPath().getArray(),
          ]),
        });

        google.maps.event.addListener(flightPath, "click", function () {
          that.setSelection(flightPath);
        });

        google.maps.event.addListener(
          flightPath.getPath(),
          "insert_at",
          function () {
            that.feature = new google.maps.Data.Feature({
              geometry: new google.maps.Data.Polygon([
                flightPath.getPath().getArray(),
              ]),
            });
          }
        );

        google.maps.event.addListener(
          flightPath.getPath(),
          "set_at",
          function () {
            that.feature = new google.maps.Data.Feature({
              geometry: new google.maps.Data.Polygon([
                flightPath.getPath().getArray(),
              ]),
            });
          }
        );

        drawingManager.setOptions({
          polygonOptions: this.polyOptions,
          rectangleOptions: this.polyOptions,
          drawingControl: false,
          drawingControlOptions: {
            position: google.maps.ControlPosition.RIGHT_TOP,
            editable: true,
            drawingModes: [
              google.maps.drawing.OverlayType.POLYGON,
              google.maps.drawing.OverlayType.RECTANGLE,
            ],
          },
        });
      }
    },
    GetZone() {
      if (this.feature) {
        this.map.data.add(this.feature);
        let collection = this.map.getGeoJson();
        this.$store.commit(
          "zone/SET_GEOJSON_DATA",
          collection.features[0].geometry
        );
      } else if (this.feature == null) {
        this.$notifier.showMessage({
          content: "Please draw your Geofence",
          color: "error",
        });
        return false;
      }
    },

    clearSelection() {
      if (this.selectedShape) {
        this.selectedShape.setEditable(false);
        this.selectedShape = null;
      }
    },
    setSelection(shape) {
      this.clearSelection();
      this.selectedShape = shape;
      shape.setEditable(true);
    },
  },
  mounted() {
    this.initMap();
  },
};
</script>