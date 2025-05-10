<template>
  <v-row no-gutters>
    <v-col cols="3" class="right-devider-shadow">
      <OperationDriverlist
        ref="operationDriversList"
        :selected-driver="selectedDriver"
        :show-driver-loader="showDriverLoader"
        @selectedDriverChanged="selectedDriverChanged"
        @getDriversList="getDriversListForOperatios"
      />
    </v-col>
    <v-col cols="9">
      <OperationOperationdetails
        ref="operationOrdersList"
        :selected_driver="selectedDriver"
        @selectedDriverChanged="selectedDriverChanged"
      />
    </v-col>
  </v-row>
</template>

<script>
export default {
  data() {
    return {
      selectedDriver: null,
      filter: {},
      showDriverLoader: false,
    };
  },
  watch: {
    selectedDriver(val) {
      if (val !== null) {
        if (val.trip !== null) {
          this.filter.trip = val.trip;
        } else {
          this.selectedDriver = null;
          this.$notifier.showMessage({
            content: "Selected driver dont have active trip.",
            color: "error",
          });
          if (this.filter.trip) {
            delete this.filter.trip;
          }
        }
      } else {
        this.loadDriversOnMap();
        if (this.filter.trip) {
          delete this.filter.trip;
        }
      }
      this.getTripOrders();
    },
  },
  methods: {
    selectedDriverChanged(driverData) {
      if (this.selectedDriver == driverData) {
        this.selectedDriver = null;
      } else {
        this.selectedDriver = driverData;
      }
    },
    getTripOrders() {
      this.$store
        .dispatch("operation/GET_OPERATIONS_LIST", this.filter)
        .then((resp) => {
          this.$refs.operationOrdersList.setMapData(
            this.$store.state.operation.mapData,
            "orders"
          );
        })
        .catch((err) => {
          if (err && err.status == 404) {
            this.$notifier.showMessage({
              content: "No data found.",
              color: "error",
            });
          }
        });
    },
    getDriversListForOperatios(filter = {}, showLoader) {
      this.showDriverLoader = showLoader;
      this.$store
        .dispatch("operation/GET_DRIVERS_LIST_FOR_OPERATIONS", filter)
        .then((resp) => {
          this.showDriverLoader = false;
          if(this.selectedDriver == null) {
            this.loadDriversOnMap();
          }
        })
        .catch((err) => {
          this.showDriverLoader = false;
        });
    },
    loadDriversOnMap() {
      let interval = setInterval(() => {
        if (this.$refs.operationOrdersList) {
          clearInterval(interval);

          this.$refs.operationOrdersList.setMapData(
            this.$refs.operationDriversList.onlineDrivers,
            "drivers"
          );
        }
      }, 500);
    },
  },
  mounted() {
    this.getTripOrders();
  },
};
</script>

<style>
</style>