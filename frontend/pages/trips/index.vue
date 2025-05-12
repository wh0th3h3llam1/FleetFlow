<template>
  <v-row no-gutters>
    <v-col cols="3" lg="3" md="3">
      <TripTriplist
        @toggleChart="toggleChart"
        @showTripDetails="openTripDetails"
      />
    </v-col>
    <v-col :cols="mdColumn" class="position-relative expand-transation">
      <CommonGmap
        :mapHeight="containerHeight"
        mapWidth="auto"
        ref="tripMap"
        page="trip"
        :clusterMarkers="true"
      />
      <div class="rounded-l-lg position-absolute details-toggle-btn">
        <v-btn
          :class="`rounded-0 rounded-l-lg background-${getTripStatusColor(
            currentTrip.status
          )}`"
          fab
          small
          depressed
          v-if="defaultSet"
          @click="changeMapSize"
        >
          <v-icon color="white" :class="rotatedIcon">
            mdi-arrow-right-bold
          </v-icon>
        </v-btn>
      </div>
      <CommonMapinfo :legends="legends" >
       <v-row  no-gutters >
         <v-col cols="2" class="d-flex justify-center align-center">
           <div style="height:4px;background:#3498eb;width:80%" class="my-2"></div>
         </v-col>
         <v-col cols="10" class="d-flex justify-start">
                  <span class="my-1 mx-2 text-caption float-left">
             Planned Route
          </span>
         </v-col>
         <v-col cols="2" class="d-flex justify-center align-center">
           <div style="height:4px;background:red;width:80%" class="my-2"></div>
         </v-col>
         <v-col cols="10" class="d-flex justify-start">
                  <span class="my-1 mx-2 text-caption float-left">
             Actual Route
          </span>
         </v-col>
       </v-row>
      </CommonMapinfo>
    </v-col>
    <v-col cols="3" md="3" lg="3" v-if="setmdColumn">
      <TripTripdetails :reloadChart="reloadChart" />
    </v-col>
  </v-row>
</template>

<script>
import {
  WarehouseIcon,
  OrderUnassignedIcon,
  OrderAssignedIcon,
  OrderPickupIcon,
  OrderSuccessfulIcon,
  OrderFailedIcon,
  OrderCancelledIcon,
  OrderEnrouteIcon,
} from "~/static/mapIcons/icons";

export default {
  data() {
    return {
      reloadChart: false,
      setmdColumn: false,
      defaultSet: false,
      mdColumn: 9,
      statusColor: "",
      rotatedIcon: "",
      legends: [
        { text: "Warehouse", marker: WarehouseIcon },
        { text: "Unassigned", marker: OrderUnassignedIcon },
        { text: "Assigned", marker: OrderAssignedIcon },
        { text: "Shipped", marker: OrderPickupIcon },
        { text: "Delivered", marker: OrderSuccessfulIcon },
        { text: "Returned", marker: OrderFailedIcon },
        { text: "Cancelled", marker: OrderCancelledIcon },
        { text: "Partially Delivered", marker: OrderEnrouteIcon },
      ],
    };
  },
  computed: {
    containerHeight() {
      return `${window.innerHeight - 64}px`;
    },
    currentTrip() {
      return this.$store.state.trip.currentTrip;
    },
  },
  methods: {
    getTripStatusColor(status) {
      switch (status) {
        case "scheduled":
          return "unassigned";
        case "active":
          return "assigned";
        case "paused":
          return "pickedup";
        case "completed":
          return "successful";
      }
    },
    toggleChart(value) {
      this.reloadChart = value;
    },
    openTripDetails(e, route, locations, driver_location, id) {
      let data = {
        id: id,
      };
      this.toggleChart(false);
      let warehouse = locations.warehouse;
      let orders = locations.locations;
      let driverDetail = {
        driver_location: driver_location,
      };
      this.$refs.tripMap.clearGeoJson();
      this.$refs.tripMap.clearMarker();
      this.$refs.tripMap.initMap();
      this.$refs.tripMap.loadRoutes(
        route,
        orders,
        warehouse,
        driverDetail,
        data
      );
      this.setmdColumn = true;
      this.defaultSet = true;
      this.mdColumn = 6;
      this.rotatedIcon = "";
      this.toggleChart(true);
    },
    changeMapSize() {
      if (this.setmdColumn) {
        this.setmdColumn = false;
        this.mdColumn = 9;
        this.rotatedIcon = "mdi-rotate-180";
      } else {
        this.setmdColumn = true;
        this.mdColumn = 6;
        this.rotatedIcon = "";
      }
    },
  },
};
</script>

<style>
.details-toggle-btn {
  top: 1px;
  right: 0px;
}
.expand-transation {
  transition: 0.3s;
}
</style>