<template>
  <v-row no-gutters>
    <v-col cols="3" lg="3" md="3">
      <OrderOrderlist @showOrderDetails="openOrderDetails" />
    </v-col>
    <v-col :cols="mdColumn" class="position-relative expand-transation">
      <CommonGmap
        :mapHeight="containerHeight"
        ref="ordersMap"
        mapWidth="auto"
        :clusterMarkers="false"
      />
      <div class="rounded-l-lg position-absolute details-toggle-btn">
        <v-btn
          :class="`rounded-0 rounded-l-lg background-${orderStatus}`"
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
      <CommonMapinfo :legends="legends" />
    </v-col>
    <v-col cols="3" v-if="setmdColumn">
      <OrderOrderdetails />
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
  OrderEnrouteIcon,
  OrderCancelledIcon
} from "~/static/mapIcons/icons";

export default {
  data() {
    return {
      setmdColumn: false,
      mdColumn: 9,
      rotatedIcon: "mdi-rotate-180",
      defaultSet: false,
      orderStatus: "",
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
  },
  methods: {
    openOrderDetails(data) {
      this.orderStatus = data.orders[0].status;
      this.$refs.ordersMap.clearMarker();
      this.$refs.ordersMap.clearGeoJson();
      this.$refs.ordersMap.loadRoutes(
        null,
        data.orders,
        data.warehouse_details
      );

      this.setmdColumn = true;
      this.defaultSet = true;
      this.mdColumn = 6;
      this.rotatedIcon = "";
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