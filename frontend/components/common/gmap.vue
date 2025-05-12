<template>
  <div class="position-relative">
    <div id="gmap" :style="{ width: mapWidth, height: mapHeight }"></div>
    <div v-if="isDrawable" class="position-absolute delete-zone-btn-container">
      <v-btn x-small depressed color="white">
        <v-icon
          class="btn-icon grey--text"
          v-if="isDrawable"
          @click="deleteShape()"
        >
          mdi-delete
        </v-icon>
      </v-btn>
    </div>
  </div>
</template>

<script>
import {
  WarehouseIcon,
  OrderAssignedIcon,
  TripPlanningLocationIcon,
  OrderEnrouteIcon,
  OrderUnassignedIcon,
  OrderPickupIcon,
  OrderSuccessfulIcon,
  OrderFailedIcon,
  OrderCancelledIcon,
  TruckIcon,
} from "~/static/mapIcons/icons";
import MarkerClusterer from "@google/markerclusterer";

import { OverlappingMarkerSpiderfier } from "ts-overlapping-marker-spiderfier";

export default {
  props: {
    mapHeight: {
      type: String,
      required: true,
    },
    mapWidth: {
      type: String,
      required: true,
    },
    dialogStatus: {
      type: Boolean,
      require: false,
      default: false,
    },
    infowindowType: {
      type: String,
      require: false,
      default: "order",
    },
    showZones: {
      type: Boolean,
      default: false,
    },
    clusterMarkers: {
      type: Boolean,
      default: false,
    },
    isDrawable: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      map: null,
      lat: 37.335964,
      lng: -121.881291,
      markers: [],
      tripId: null,
      markerCluster: null,
      drawingManager: null,
      driverMarkers: [],
      selectedShape: null,
      multiPolygonInstances: [],
      editedZone: [],
      bounds: null,
      coordinates: [],
      oms: null,
      imagePath: "/mapIcons/KP",
      polyOptions: {
        strokeColor: "#FF0000",
        strokeOpacity: 0.8,
        strokeWeight: 2,
        fillColor: "#00FF00",
        fillOpacity: 0.35,
        editable: true,
      },
    };
  },
  watch: {
    isDialogOpen(value) {
      if (!value) {
        this.clearMarker();
        this.clearGeoJson();
        this.clearDriverMarker();
        this.deleteShape();
      }
    },
  },
  computed: {
    isDialogOpen() {
      return this.dialogStatus;
    },
    actualRoute() {
      return this.$store.state.trip.actualroute
        ? this.$store.state.trip.actualroute
        : [];
    },
  },
  methods: {
    initMap(center = null) {
      if (!center) var center = new google.maps.LatLng(this.lat, this.lng);

      this.map = new google.maps.Map(document.getElementById("gmap"), {
        zoom: 10,
        center: center,
        disableDefaultUI: true,
        keepSpiderfied: true,
        styles: [
          { elementType: "geometry", stylers: [{ color: "#212121" }] },
          {
            elementType: "labels.text.stroke",
            stylers: [{ color: "#212121" }],
          },
          { elementType: "labels.text.fill", stylers: [{ color: "#757575" }] },
          { elementType: "labels.icon", stylers: [{ visibility: "off" }] },
          {
            featureType: "administrative",
            elementType: "geometry",
            stylers: [{ color: "#757575" }],
          },
          {
            featureType: "administrative.country",
            elementType: "labels.text.fill",
            stylers: [{ color: "#9e9e9e" }],
          },
          {
            featureType: "administrative.locality",
            elementType: "labels.text.fill",
            stylers: [{ color: "#bdbdbd" }],
          },
          {
            featureType: "administrative.land_parcel",
            elementType: "labels.text.stroke",
            stylers: [{ color: "#9e9e9e" }],
          },
          {
            featureType: "poi.park",
            elementType: "geometry",
            stylers: [{ color: "#181818" }],
          },
          {
            featureType: "poi.park",
            elementType: "labels.text.fill",
            stylers: [{ color: "#616161" }],
          },
          {
            featureType: "poi.park",
            elementType: "labels.text.stroke",
            stylers: [{ color: "#1b1b1b" }],
          },
          {
            featureType: "road",
            elementType: "geometry.fill",
            stylers: [{ color: "#2c2c2c" }],
          },
          {
            featureType: "road",
            elementType: "labels.text.fill",
            stylers: [{ color: "#8a8a8a" }],
          },
          {
            featureType: "road.highway",
            elementType: "geometry",
            stylers: [{ color: "#3c3c3c" }],
          },
          {
            featureType: "road.highway.controlled_access",
            elementType: "geometry",
            stylers: [{ color: "#4e4e4e" }],
          },
          {
            featureType: "road.arterial",
            elementType: "geometry",
            stylers: [{ color: "#373737" }],
          },
          {
            featureType: "road.local",
            elementType: "labels.text.fill",
            stylers: [{ color: "#616161" }],
          },
          {
            featureType: "transit",
            elementType: "labels.text.fill",
            stylers: [{ color: "#757575" }],
          },
          {
            featureType: "water",
            elementType: "geometry",
            stylers: [{ color: "#000000" }],
          },
          {
            featureType: "water",
            elementType: "labels.text.fill",
            stylers: [{ color: "#3d3d3d" }],
          },
        ],
      });
      if (this.isDrawable) {
        this.drawingManager = new google.maps.drawing.DrawingManager({
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
          this.drawingManager,
          "overlaycomplete",
          this.overlayCompleteCallback.bind(this)
        );
      }
    },
    overlayCompleteCallback(event) {
      this.setSelection(event);
      if (event.type == "polygon") {
        window.google.maps.event.addListener(
          this.selectedShape.overlay.getPath(),
          "insert_at",
          () => {
            this.setSelection(event);
          }
        );
        window.google.maps.event.addListener(
          this.selectedShape.overlay.getPath(),
          "set_at",
          () => {
            this.setSelection(event);
          }
        );
      } else {
        window.google.maps.event.addListener(
          this.selectedShape.overlay,
          "bounds_changed",
          () => {
            this.setSelection.bind(this);
          }
        );
      }
      this.drawingManager.setDrawingMode(null);
      this.drawingManager.setOptions({
        drawingControl: false,
      });
    },
    constructCordinates(shapeType) {
      this.coordinates = [];
      if (shapeType == "polygon") {
        this.selectedShape.overlay
          .getPath()
          .getArray()
          .forEach((ele) => this.coordinates.push([ele.lng(), ele.lat()]));
        this.coordinates.push(this.coordinates[0]);
      } else {
        let bounds = this.selectedShape.overlay.getBounds();
        this.coordinates = [
          [bounds.getSouthWest().lng(), bounds.getSouthWest().lat()],
          [bounds.getNorthEast().lng(), bounds.getSouthWest().lat()],
          [bounds.getNorthEast().lng(), bounds.getNorthEast().lat()],
          [bounds.getSouthWest().lng(), bounds.getNorthEast().lat()],
          [bounds.getSouthWest().lng(), bounds.getSouthWest().lat()],
        ];
      }
    },
    convertToGeoJSON(coordinates) {
      if (!coordinates) {
        coordinates = this.coordinates;
      }
      if (coordinates.length == 0) {
        return false;
      } else {
        let GeoJSON = {
          type: "Feature",
          geometry: {
            type: "Polygon",
            coordinates: [coordinates],
          },
          properties: {},
        };
        return GeoJSON;
      }
    },
    setEditablePolygon(path, coordinates) {
      this.selectedShape = new google.maps.Polygon({
        paths: path,
        strokeColor: "yellow",
        strokeOpacity: 0.8,
        strokeWeight: 2,
        fillColor: "yellow",
        fillOpacity: 0.1,
        editable: true,
      });
      this.selectedShape.setMap(this.map);
      this.coordinates = coordinates;
      this.drawingManager.setDrawingMode(null);
      this.drawingManager.setOptions({
        drawingControl: false,
      });
      window.google.maps.event.addListener(
        this.selectedShape.getPath(),
        "insert_at",
        (event) => {
          this.coordinates = [];
          this.selectedShape
            .getPath()
            .getArray()
            .forEach((ele) => this.coordinates.push([ele.lng(), ele.lat()]));
          this.coordinates.push(this.coordinates[0]);
        }
      );
      window.google.maps.event.addListener(
        this.selectedShape.getPath(),
        "set_at",
        (event) => {
          this.coordinates = [];
          this.selectedShape
            .getPath()
            .getArray()
            .forEach((ele) => this.coordinates.push([ele.lng(), ele.lat()]));
          this.coordinates.push(this.coordinates[0]);
        }
      );
    },
    clearSelection() {
      if (this.selectedShape) {
        if (this.selectedShape.overlay) {
          this.selectedShape.overlay.setEditable(false);
        }
        this.selectedShape = null;
      }
    },
    setSelection(shape) {
      this.clearSelection();
      this.selectedShape = shape;
      if (shape.overlay.getEditable() == false) {
        shape.overlay.setEditable(true);
      }
      this.constructCordinates(this.selectedShape.type);
    },
    loadRoutes(routes, orders, warehouse, driverDetail, data = null) {
      if (data != null && data.id) {
        this.tripId = data.id;
      } else {
        this.tripId = null;
      }

      let interval = setInterval(() => {
        if (this.map !== null) {
          clearInterval(interval);

          // this.clearMarker();
          // this.clearGeoJson();
          if (driverDetail) {
            this.clearDriverMarker();

            this.loadDrivers([driverDetail]);
          }

          this.bounds = new google.maps.LatLngBounds();
          if (warehouse) {
            let infowindow = new google.maps.InfoWindow({ maxWidth: 470 });
            let iconType = "warehouse";
            let html = `<ul class="dms-map-tooltip">
                        <li><h5 class="dms-map-tooltip-main-title">Warehouse</h5></li>
                        <li class="d-flex pa-0 ma-0">
                          <span class="dms-map-tooltip-title-text">Address: ${warehouse.address}</span>
                        </li>
                        </ul>`;

            const center = new google.maps.LatLng(
              warehouse.coordinates[1],
              warehouse.coordinates[0]
            );

            this.map.panTo(center);

            // latlngbounds.extend(center) // For auto sizeing map

            const marker = new google.maps.Marker({
              position: {
                lat: warehouse.coordinates[1],
                lng: warehouse.coordinates[0],
              },
              map: this.map,
              icon: {
                url: this.getIcon(iconType),
              },
            });

            marker.addListener("mouseover", () => {
              infowindow.setContent(html);
              infowindow.open(this.map, marker);
            });
            marker.addListener("mouseout", () => {
              infowindow.close();
            });
            this.markers.push(marker);
            this.bounds.extend(marker.position);
          }
          if (Array.isArray(orders)) {
            let infowindow = new google.maps.InfoWindow({ maxWidth: 350 });
            orders.forEach((order, index) => {
              let iconType = "order";
              let html;
              if (this.infowindowType == "customer") {
                html = `<ul class="ma-0 pa-1">
                        <li class="pb-2">
                          <span class="text-primary text-subtitle-1 font-weight-bold">${order.customer_code}</span>
                        </li>
                        <li class="pb-1 ma-0">
                          <span class="text-primary text-caption font-weight-bold">Address:</span>
                          <span class="text-primary text-caption"> ${order.address}</span>
                        </li>`;
              } else {
                html = `<ul class="ma-0 pa-1">
                        <li class="pb-2">
                          <span class="text-primary text-subtitle-1 font-weight-bold">${order.reference_number}</span>
                        </li>
                        <li class="pb-1 ma-0">
                          <span class="text-primary text-caption font-weight-bold">Address:</span>
                          <span class="text-primary text-caption"> ${order.address}</span>
                        </li>`;
              }

              if (order.status) {
                html =
                  html +
                  `<li class="pb-1 ma-0">
                      <span class="text-primary text-caption font-weight-bold">Status:</span>
                      <span class="text-primary text-caption text-uppercase font-weight-black">${
                        order.status == "pickedup"
                          ? "Shipped"
                          : order.status == "successful"
                          ? "Delivered"
                          : order.status == "failed"
                          ? "Returned"
                          : order.status == "partially_delivered"
                          ? "Partially Delivered"
                          : order.status
                      }</span>
                    </li>`;
              }
              if (order.customer_name) {
                html =
                  html +
                  `<li class="pb-1 ma-0">
                    <span class="text-primary text-caption font-weight-bold">Customer Name:</span>
                    <span class="text-primary text-caption"> ${order.customer_name}</span>
                  </li>`;
              }
              if(order.events_info) {
                html =
                  html +
                  `<li class="pb-1 ma-0">
                      <span class="text-primary text-caption font-weight-bold">${this.orderTimeChange(
                        order
                      )} :</span>
                      <span class="text-primary text-caption"> ${this.orderTextChange(
                        order
                      )}</span></li>`;
              }

              if (order.delivery_window) {
                html =
                  html +
                  `<li class="pb-1 ma-0">
                    <span class="text-primary text-caption font-weight-bold">Delivery Window:</span>
                    <span class="text-primary text-caption"> ${order.delivery_window}</span>
                  </li>`;
              }
              if (order.eta && order.status == "pickedup") {
                html =
                  html +
                  `<li class="pb-1 ma-0">
                    <span class="text-primary text-caption font-weight-bold">ETA:</span>
                    <span class="text-primary text-caption"> ${order.eta}</span>
                  </li>`;
              }

              html = html + `</ul>`;

              this.oms = new OverlappingMarkerSpiderfier(this.map, {
                markersWontMove: true,
                markersWontHide: true,
                basicFormatEvents: true,
              });

              let markerData = {
                position: {
                  lat: order.coordinates[1],
                  lng: order.coordinates[0],
                },
                map: this.map,
                animation: google.maps.Animation.DROP,
              };

              markerData.icon = {
                url: this.getIcon(iconType, order.status),
              };

              if (order.sequence_number) {
                markerData.label = {
                  color: "#ffffff",
                  fontWeight: "bold",
                  fontSize: "14px",
                  text: order.sequence_number.toString(),
                };
              }

              const marker = new google.maps.Marker(markerData); // markerData works here as a LatLngLiteral

              marker.addListener("mouseover", () => {
                infowindow.setContent(html);
                infowindow.open(this.map, marker);
              });
              marker.addListener("mouseout", () => {
                infowindow.close();
              });
              this.markers.push(marker);
              this.bounds.extend(markerData.position);
              if (this.clusterMarkers && orders.length - 1 == index) {
                this.overlappingMakerShow();
              }
              if (
                order.actual_delivery_location &&
                order.actual_delivery_location.coordinates &&
                order.actual_delivery_location.coordinates.length
              ) {
                this.loadOrdersActualDeliveryLocation(
                  order.actual_delivery_location
                );
              }
            });
            this.map.fitBounds(this.bounds);
          }

          if (routes && routes.features.length) {
            routes.features.forEach((route) => {
              this.map.data.addGeoJson(route);
            });
            this.map.data.setStyle((feature) => {
              var color = this.getRandomColor(this.$route.name);
              return {
                fillColor: color,
                strokeWeight: 2,
                strokeColor: color,
              };
            });
          }
        }
      }, 100);
      if (this.tripId) {
        this.getActualDriverRoute();
      }
    },
    orderTimeChange(order) {
      switch (order.status) {
        case "unassigned":
          return "";
        case "assigned":
          return "Assigned on";
        case "pickedup":
          return "Shipped on";
        case "partially_delivered":
          return "Partially Delivered";
        case "successful":
          return "Delivered on";
        case "failed":
          return "Returned on";
        case "returned":
          return "Returned on";
        case "cancelled":
          return "Cancelled on";
        default:
          return null;
      }
    },
    orderTextChange(order) {
      if(order && order.events_info) {
        switch (order.status) {
          case "unassigned":
            return "";
          case "assigned":
            return order.events_info.assigned_on;
          case "pickedup":
            return order.events_info.picked_up_on;
          case "partially_delivered":
            return order.events_info.completed_on;
          case "successful":
            return order.events_info.completed_on;
          case "failed":
            return order.events_info.failed_on;
          case "returned":
            return order.events_info.failed_on;
          case "cancelled":
            return order.events_info.cancelled_on;
          default:
            return null;
        }
      }
    },
    setDriverRoute() {
      let route = [];
      this.actualRoute.forEach((item) => {
        route.push({
          lat: parseFloat(item[1]),
          lng: parseFloat(item[0]),
        });
      });
      const flightPath = new google.maps.Polyline({
        path: route,
        geodesic: true,
        strokeColor: "#FF0000",
        strokeOpacity: 1.0,
        strokeWeight: 3,
      });

      flightPath.setMap(this.map);
    },
    getActualDriverRoute() {
      this.$store
        .dispatch("trip/GET_ACTUAL_DRIVER_ROUTE", this.tripId)
        .then((response) => {
          this.setDriverRoute();
        });
    },
    clusterMarkersshwoing() {
      this.initMap();
      this.markerCluster = new MarkerClusterer(this.map, this.markers, {
        imagePath:
          "https://developers.google.com/maps/documentation/javascript/examples/markerclusterer/m",
        height: 66,
        width: 66,
        maxZoom: 14,
      });
    },
    overlappingMakerShow() {
      this.markers.forEach((marker, i) => {
        google.maps.event.addListener(marker, "spider_click", function (e) {
          // 'spider_click', not plain 'click'
        });
        this.oms.addMarker(marker); // adds the marker to the spiderfier _and_ the map
      });
    },
    loadOrdersActualDeliveryLocation(actualLocation) {
      let infowindow = new google.maps.InfoWindow({ maxWidth: 350 });
      let html = `<ul class="ma-0 pa-1">
                    <li class="pb-2">
                      <span class="text-primary text-subtitle-1 font-weight-bold">Actual Delivery Location</span>
                    </li>
                    <li class="pb-1 ma-0">
                      <span class="text-primary text-caption font-weight-bold">Time Stamp :</span>
                      <span class="text-primary text-caption"> ${actualLocation.timestamp}</span>
                    </li>`;
      let markerData = {
        position: {
          lat: actualLocation.coordinates[1],
          lng: actualLocation.coordinates[0],
        },
        map: this.map,
        animation: google.maps.Animation.DROP,
      };

      const marker = new google.maps.Marker(markerData);
      marker.addListener("mouseover", () => {
        infowindow.setContent(html);
        infowindow.open(this.map, marker);
      });
      marker.addListener("mouseout", () => {
        infowindow.close();
      });
      this.markers.push(marker);
      this.bounds.extend(markerData.position);
    },
    loadDrivers(driversList) {
      let interval = setInterval(() => {
        if (this.map !== null) {
          clearInterval(interval);

          for (let index = 0; index < driversList.length; index++) {
            const driver = driversList[index];

            if (driver.driver_location.location == null) {
              continue;
            }
            let infowindow = new google.maps.InfoWindow({ maxWidth: 350 });
            let html = `<ul class="dms-map-tooltip">
                          <li><h5 class="dms-map-tooltip-main-title">${driver.driver_location.name}</h5></li>
                          <li class="d-flex pa-0 ma-0">
                            <span class="text-primary text-caption font-weight-bold">Time Stamp: </span>
                            <span class="text-primary text-caption"> ${driver.driver_location.timestamp}</span>
                          </li>
                        </ul>`;

            const marker = new google.maps.Marker({
              position: {
                lat: driver.driver_location.location[1],
                lng: driver.driver_location.location[0],
              },
              map: this.map,
              icon: {
                url: this.getIcon("driver"),
              },
            });

            // driver info window
            marker.addListener("mouseover", () => {
              infowindow.setContent(html);
              infowindow.open(this.map, marker);
            });
            marker.addListener("mouseout", () => {
              infowindow.close();
            });

            // driver route click event
            marker.addListener("click", () => {
              this.$emit("selectDriver", driver);
            });
            this.driverMarkers.push(marker);
          }
        }
      });
    },
    loadEditableMultiPolygon(coordinates) {
      let interval = setInterval(() => {
        if (this.map) {
          clearInterval(interval);
          if (coordinates.length > 0) {
            coordinates.forEach((array, index) => {
              let path = [];
              array[0].forEach((element) => {
                path.push({ lat: element[1], lng: element[0] });
              });
              this.multiPolygonInstances[index] = new google.maps.Polygon({
                paths: path,
                strokeColor: "yellow",
                strokeOpacity: 0.8,
                strokeWeight: 2,
                fillColor: "yellow",
                fillOpacity: 0.1,
                editable: true,
              });
              this.multiPolygonInstances[index].setMap(this.map);
            });
          }
        }
      }, 100);
    },
    deleteShape() {
      if (this.selectedShape) {
        if (this.selectedShape.overlay) {
          this.selectedShape.overlay.setMap(null);
        } else {
          this.selectedShape.setMap(null);
        }
        this.drawingManager.setOptions({
          drawingControl: true,
        });
        this.coordinates = [];
      }
      if (this.multiPolygonInstances) {
        while (this.multiPolygonInstances.length != 0) {
          this.multiPolygonInstances[0].setMap(null);
          this.multiPolygonInstances.splice(0, 1);
        }
      }
    },
    getZoneData() {
      let zone;
      if (this.multiPolygonInstances.length > 0) {
        this.multiPolygonInstances.forEach((ins, index) => {
          this.editedZone.push([
            ins
              .getPath()
              .getArray()
              .map((ele) => {
                return [ele.lng(), ele.lat()];
              }),
          ]);
          if (this.multiPolygonInstances.length == index + 1) {
            zone = { coordinates: this.editedZone, type: "MultiPolygon" };
          }
        });
      } else {
        zone = this.convertToGeoJSON().geometry;
      }
      return zone;
    },
    getIcon(iconFor, status) {
      if (iconFor == "order") {
        switch (status) {
          case "assigned":
            return OrderAssignedIcon;

          case "unassigned":
            return OrderUnassignedIcon;

          case "pickedup":
            return OrderPickupIcon;

          case "partially_delivered":
            return OrderEnrouteIcon;

          case "successful":
            return OrderSuccessfulIcon;

          case "failed":
            return OrderFailedIcon;

          case "cancelled":
            return OrderCancelledIcon;

          default:
            return TripPlanningLocationIcon;
        }
      }
      if (iconFor == "warehouse") {
        return WarehouseIcon;
      }
      if (iconFor == "driver") {
        return TruckIcon;
      }
    },
    getRandomColor(route) {
      if (route == "trips") {
        return "#3498eb";
      }
      var letters = "0123456789ABCDEF";
      var color = "#";
      for (var i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
      }
      return color;
    },
    async clearMarker() {
      if (this.clusterMarkers && this.markerCluster) {
        this.markerCluster = null;
      }
      while (this.markers.length) {
        const marker = this.markers[0];
        marker.setMap(null);
        this.markers.splice(0, 1);
      }
      this.bounds = [];
    },
    async clearDriverMarker() {
      for (let index = 0; index < this.driverMarkers.length; index++) {
        const marker = this.driverMarkers[index];
        marker.setMap(null);
      }
    },
    clearGeoJson() {
      if (this.map !== null) {
        this.map.data.forEach((feature) => {
          this.map.data.remove(feature);
        });
      }
    },
  },
  mounted() {
    let interval = setInterval(() => {
      if (window.google && window.google.maps) {
        this.initMap();
        clearInterval(interval);
      }
    }, 100);
  },
};
</script>

<style>
.delete-zone-btn-container {
  top: 140px;
  right: 10px;
}
.delete-zone-btn-container button {
  height: 40px !important;
  width: 40px !important;
  border-radius: 0 !important;
}
.delete-zone-btn-container .btn-icon {
  font-size: 20px !important;
  padding: 10px 10px !important;
}
</style>
