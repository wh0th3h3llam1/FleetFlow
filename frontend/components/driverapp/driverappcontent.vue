<template>
  <v-card class="d-flex flex-column" style="width: 100%">
    <div>
      <v-card elevation="0">
        <v-card-text class="light_grey">
          <v-row no-gutters class="px-0">
            <v-col cols="12">
              <v-row
                v-if="
                  tripdetails &&
                  tripdetails.status == 'scheduled' &&
                  tripdetails.status != 'active'
                "
              >
                <v-col cols="4" class="px-1"> </v-col>
                <v-col cols="4" class="px-1">
                  <v-btn
                    class="text-uppercase rounded-0 light_subBlue white--text"
                    small
                    elevation="1"
                    :disabled="
                      driverDetails.status == 'off_duty' ||
                      driverDetails.status == 'break'
                    "
                    block
                    @click="tripStatusChange(tripdetails.id, 'active')"
                  >
                    <span class="text-uppercase"> Start Trip </span>
                  </v-btn>
                </v-col>
                <v-col cols="4" class="px-1"> </v-col>
              </v-row>
              <v-row v-if="driverDetails && driverDetails.status == 'break'">
                <v-col cols="4" class="px-1"> </v-col>
                <v-col cols="4" class="px-1">
                  <v-btn
                    class="text-uppercase rounded-0 light_subBlue white--text"
                    small
                    elevation="1"
                    @click="tripPause(driverDetails.id, 'on_duty')"
                    block
                  >
                    <span class="text-uppercase">Resume Trip</span>
                  </v-btn>
                </v-col>
                <v-col cols="4" class="px-1"> </v-col>
              </v-row>

              <v-row
                v-if="
                  tripdetails &&
                  tripdetails.status !== 'scheduled' &&
                  driverDetails.status != 'break' &&
                  canCompleted != true
                "
              >
                <v-col cols="12" class="px-1">
                  <v-btn
                    class="text-uppercase rounded-0 light_subBlue white--text"
                    small
                    elevation="1"
                    @click="tripPause(driverDetails.id, 'break')"
                    :disabled="
                      driverDetails.status == 'off_duty' ||
                      driverDetails.status == 'break'
                    "
                    block
                  >
                    <span class="text-uppercase">take a brake </span>
                  </v-btn>
                </v-col>
              </v-row>
              <v-row v-if="canCompleted">
                <v-col cols="12" class="px-1">
                  <v-btn
                    class="text-uppercase rounded-0 light_red white--text"
                    small
                    :disabled="tripdetails.status == 'completed'"
                    elevation="1"
                    @click="tripStatusChange(tripdetails.id, 'completed')"
                    block
                  >
                    <span class="text-uppercase"> complete</span>
                  </v-btn>
                </v-col>
              </v-row>
            </v-col>
            <v-col cols="12" class="" style="height: 38px">
              <v-expansion-panels
                accordion
                tile
                flat
                class="light_grey px-8"
                style="
                  position: absolute;
                  z-index: 2;
                  width: 100%;
                  left: 0;
                  right: 0;
                "
              >
                <v-expansion-panel class="light_grey">
                  <v-expansion-panel-header
                    class="px-1 pt-5"
                    style="min-height: 38px; height: 38px"
                  >
                    <b>
                      <h4 class="text-right pr-5 light_black--text">
                        View Order Details
                      </h4></b
                    >
                    <template v-slot:actions>
                      <v-btn rounded icon small class="primary text--white"
                        ><v-icon class="white--text"> $expand </v-icon></v-btn
                      >
                    </template>
                  </v-expansion-panel-header>
                  <v-expansion-panel-content class="driver-app-expansion">
                    <v-card
                      elevation="0"
                      class="ma-0 pa-0 mb-6"
                      v-if="tripdetails"
                    >
                      <v-card-title class="grey py-1 ma-0">
                        <h5 class="white--text pa-0 ma-0">Trip Details</h5>
                        <v-spacer></v-spacer>
                        <h5 class="white--text pa-0 ma-0">
                          {{ tripdetails.trip_date }}
                        </h5>
                      </v-card-title>
                      <v-card-text class="py-4 px-8 ma-0">
                        <div class="d-flex my-1">
                          <p class="ma-0">Trip ID</p>
                          <v-spacer></v-spacer>
                          <p class="ma-0">
                            <b>{{ tripdetails.id }}</b>
                          </p>
                        </div>
                        <div class="d-flex my-1">
                          <p class="ma-0">Trip Status</p>
                          <v-spacer></v-spacer>
                          <p class="ma-0 text-capitilize">
                            <b>{{ tripdetails.status }}</b>
                          </p>
                        </div>
                        <div
                          class="d-flex my-1"
                          v-if="
                            tripdetails.driver && tripdetails.driver.username
                          "
                        >
                          <p class="ma-0">Driver</p>
                          <v-spacer></v-spacer>
                          <p class="ma-0">
                            <b>{{ tripdetails.driver.username }}</b>
                          </p>
                        </div>
                        <div class="d-flex my-1" v-if="tripdetails.helper_nam">
                          <p class="ma-0">Helper</p>
                          <v-spacer></v-spacer>
                          <p class="ma-0">
                            <b>{{ tripdetails.helper_name }}</b>
                          </p>
                        </div>
                        <div
                          class="d-flex my-1"
                          v-if="
                            tripdetails.vehicle &&
                            tripdetails.vehicle.vehicle_plate_no
                          "
                        >
                          <p class="ma-0">Vehicle</p>
                          <v-spacer></v-spacer>
                          <p class="ma-0">
                            <b>{{ tripdetails.vehicle.vehicle_plate_no }}</b>
                          </p>
                        </div>
                        <div
                          class="d-flex my-1"
                          v-if="
                            tripdetails.trip_order_count &&
                            tripdetails.trip_order_count.total
                          "
                        >
                          <p class="ma-0">Total Orders</p>
                          <v-spacer></v-spacer>
                          <p class="ma-0">
                            <b>{{ tripdetails.trip_order_count.total }}</b>
                          </p>
                        </div>
                        <div class="d-flex mt-4">
                          <!-- <v-divider></v-divider> -->
                        </div>

                        <div class="d-flex mb-4">
                          <h4>Truck Partition</h4>
                        </div>

                        <div v-if="tripdetails.trip_partition">
                          <PieChart
                            :data="{
                              labels: [`Chilled`, 'Dry', 'Frozen'],
                              datasets: [
                                {
                                  backgroundColor: [
                                    '#50b7d0',
                                    '#ee872c',
                                    '#d16bc8',
                                  ],
                                  data: [
                                    tripdetails.trip_partition.chilled,
                                    tripdetails.trip_partition.dry,
                                    tripdetails.trip_partition.frozen,
                                  ],
                                },
                              ],
                            }"
                            :options="options"
                            :height="120"
                          />
                        </div>
                        <div class="d-flex my-4">
                          <!-- <v-divider></v-divider> -->
                        </div>

                        <div class="d-flex">
                          <h4>Total Orders</h4>
                        </div>

                        <div class="mb-2">
                          <v-row no-gutters v-if="tripdetails.trip_order_count">
                            <v-col cols="3" class="text-center py-2">
                              <h4 class="primary--text text-caption">
                                Unattempted
                              </h4>
                            </v-col>
                            <v-col cols="3" class="text-center py-2">
                              <h4 class="primary--text text-caption">
                                Partially
                              </h4>
                            </v-col>
                            <v-col cols="3" class="text-center py-2">
                              <h4 class="primary--text text-caption">
                                Returned
                              </h4>
                            </v-col>
                            <v-col cols="3" class="text-center py-2">
                              <h4 class="primary--text text-caption">
                                Delivered
                              </h4>
                            </v-col>
                          </v-row>

                          <v-row no-gutters v-if="tripdetails.trip_order_count">
                            <v-col
                              cols="3"
                              class="light_unassigned text-center py-2"
                            >
                              <b>
                                <h4 class="white--text text--bold">
                                  {{ tripdetails.trip_order_count.unattempted }}
                                </h4></b
                              >
                            </v-col>
                            <v-col
                              cols="3"
                              class="light_partially_delivered text-center py-2"
                            >
                              <b>
                                <h4 class="white--text text--bold">
                                  {{ tripdetails.trip_order_count.partial }}
                                </h4></b
                              >
                            </v-col>
                            <v-col
                              cols="3"
                              class="light_failed text-center py-2"
                            >
                              <b>
                                <h4 class="white--text text--bold">
                                  {{ tripdetails.trip_order_count.failed }}
                                </h4></b
                              >
                            </v-col>
                            <v-col
                              cols="3"
                              class="light_pgreen text-center py-2"
                            >
                              <b>
                                <h4 class="white--text text--bold">
                                  {{ tripdetails.trip_order_count.successful }}
                                </h4></b
                              >
                            </v-col>
                          </v-row>
                        </div>
                      </v-card-text>
                    </v-card>
                  </v-expansion-panel-content>
                </v-expansion-panel>
              </v-expansion-panels>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
    </div>

    <v-tabs-items v-model="tabs" style="height: 100%; overflow-y: scroll">
      <v-tab-item>
        <div
          class="pa-4 get-last"
          v-show="
            tripdetails &&
            tripdetails.status == 'active' &&
            tripdetails.status != 'completed'
          "
        >
          <v-expansion-panels
            accordion
            tile
            flat
            class="mb-4"
            v-for="(order, i) in orders"
            :key="i"
          >
            <v-expansion-panel>
              <v-expansion-panel-header
                hide-actions=""
                class="px-1 pt-5 rounded-t-lg light_black"
                style="min-height: 30px; height: 30px"
              >
                <div class="d-flex justify-space-between align-center">
                  <b>
                    <h4 class="pl-5 white--text">
                      {{ order.reference_number }}
                    </h4></b
                  >
                  <v-chip
                    class="rounded-sm white--text mt-n1 mr-2"
                    :class="coloredOrderStatus(order.status)"
                    small
                  >
                    {{ OrderTextStatus(order.status) }}
                  </v-chip>
                </div>
              </v-expansion-panel-header>
              <v-expansion-panel-content class="driver-app-expansion">
                <v-card elevation="0" class="ma-0 pa-0 light_grey">
                  <v-card-title class="py-0 ma-0">
                    <v-row no-gutters class="py-4">
                      <v-col cols="12" class="d-flex">
                        <p class="d-app-card-title">Customer Name</p>
                        <v-spacer></v-spacer>
                        <p class="d-app-card-text">
                          {{ order.contact_person }}
                        </p>
                      </v-col>
                      <v-col cols="12" class="d-flex">
                        <p class="d-app-card-title">Order Type</p>
                        <v-spacer></v-spacer>
                        <p class="d-app-card-text">{{ order.order_type }}</p>
                      </v-col>
                      <v-col cols="12" class="d-flex" v-if="order.order_value">
                        <p class="d-app-card-title">Order Value</p>
                        <v-spacer></v-spacer>
                        <p class="d-app-card-text">{{ order.order_value }}</p>
                      </v-col>
                      <v-col cols="12">
                        <div class="my-2">
                          <v-divider></v-divider>
                        </div>
                      </v-col>
                      <v-col cols="12">
                        <div>
                          <p class="d-app-card-title">
                            <b>Destination</b>
                          </p>
                          <p class="d-app-card-title" style="line-height: 22px">
                            {{ order.drop_address }}
                          </p>
                        </div>
                      </v-col>
                    </v-row>
                  </v-card-title>
                  <v-card-text class="pt-0 pb-2 px-0 ma-0 light_grey">
                    <v-row no-gutters class="mx-2 px-4 py-2 white">
                      <v-col cols="12" class="d-flex">
                        <p class="d-app-card-title">Proof of Delivery</p>
                        <v-spacer></v-spacer>
                        <p class="d-app-card-text">
                          <b>{{
                            order.require_proof_of_delivery ? "Yes" : "No"
                          }}</b>
                        </p>
                      </v-col>
                      <v-col cols="12" class="d-flex">
                        <p class="d-app-card-title">Quantity</p>
                        <v-spacer></v-spacer>
                        <p class="d-app-card-text">
                          <b>{{ order.total_quantity }}</b>
                        </p>
                      </v-col>
                      <v-col cols="12" class="d-flex">
                        <p class="d-app-card-title">Payment Type</p>
                        <v-spacer></v-spacer>
                        <p class="d-app-card-text">
                          <b>{{ order.payment_type }}</b>
                        </p>
                      </v-col>
                      <v-col
                        cols="12"
                        class="d-flex"
                        v-if="order.payment_collected"
                      >
                        <p class="d-app-card-title">Add Collaction Amount</p>
                        <v-spacer></v-spacer>
                        <p class="d-app-card-text">
                          <b>
                            <v-chip small class="primary white--text rounded-0">
                              {{ order.payment_collected }}
                            </v-chip>
                          </b>
                        </p>
                      </v-col>
                    </v-row>
                    <div class="text-right px-3 pt-3 pb-2">
                      <v-btn
                        small
                        @click="openDeliveredItemDialog(order.id)"
                        :disabled="
                          driverDetails && driverDetails.status == 'break'
                        "
                        v-show="
                          order.status == 'unassigned' ||
                          order.status == 'assigned' ||
                          order.status == 'pickedup'
                        "
                        class="white--text light_successful mr-2"
                        >Delivered</v-btn
                      >
                      <v-btn
                        :disabled="
                          driverDetails && driverDetails.status == 'break'
                        "
                        v-show="
                          order.status == 'unassigned' ||
                          order.status == 'assigned' ||
                          order.status == 'pickedup'
                        "
                        @click="openReturnOrderDialog(order.id)"
                        small
                        class="white--text light_failed"
                        >Returned</v-btn
                      >
                    </div>
                  </v-card-text>
                </v-card>
              </v-expansion-panel-content>
            </v-expansion-panel>
          </v-expansion-panels>
        </div>
        <DriverappDriverappdeliveryform v-model="openDeliveredItemFormDialog" />
        <DriverappDriverappreturnform v-model="openReturnOrderFormDialog" />
      </v-tab-item>
      <v-tab-item eager>
        <CommonGmap
          mapWidth="100%"
          :mapHeight="mapHeight"
          ref="driverappViewTrip"
        />
      </v-tab-item>
    </v-tabs-items>

    <v-tabs
      color="light_red"
      v-model="tabs"
      fixed-tabs
      style="position: sticky; z-index: 3; bottom: 0"
    >
      <v-tab>Trip View</v-tab>
      <v-tab @click="getMapDetail(tripdetails.id)">Map View</v-tab>
    </v-tabs>
  </v-card>
</template>


<script>
import PieChart from "@/components/common/charts/PieChart.vue";
export default {
  components: {
    PieChart,
  },
  data() {
    return {
      tabs: 0,
      openDeliveredItemFormDialog: false,
      openReturnOrderFormDialog: false,
      canCompleted: false,
      allowCompleted: [
        "partially_delivered",
        "successful",
        "failed",
        "cancelled",
      ],
      options: {
        responsive: true,
        legend: {
          display: true,
          position: "right",
        },
      },
    };
  },
  computed: {
    driverDetails() {
      return this.$store.state.driverapp.driverDetails;
    },
    tripdetails() {
      return this.$store.state.driverapp.tripDetails;
    },
    ordersLocation() {
      if (
        this.$store.state.driverapp.orderlocation &&
        this.$store.state.driverapp.orderlocation.locations &&
        this.$store.state.driverapp.orderlocation.locations.locations &&
        this.$store.state.driverapp.orderlocation.locations.warehouse
      ) {
        return this.$store.state.driverapp.orderlocation;
      }
    },
    tripRoute() {
      if (
        this.$store.state.driverapp.tripRoute &&
        this.$store.state.driverapp.tripRoute.trip_info &&
        this.$store.state.driverapp.tripRoute.trip_info.trip_route
      ) {
        return this.$store.state.driverapp.tripRoute.trip_info.trip_route;
      } else {
        return null;
      }
    },
    orders() {
      let orders = this.$store.state.driverapp.orderList;
      if (orders) {
        let Status = orders.map((item) =>
          this.allowCompleted.includes(item.status)
        );
        if (!Status.includes(false)) {
          this.canCompleted = true;
        }
      }

      return orders;
    },
    mapHeight() {
      if (this.selected_driver) {
        return `${window.innerHeight - 282}px`;
      } else {
        return `${window.innerHeight - 200}px`;
      }
    },
  },
  methods: {
    getMapDetail(id) {
      if (typeof this.tripdetails != "undefined" && typeof id != "undefined") {
        this.$store.dispatch("driverapp/GET_TRIP_ROUTE", id);
        this.$refs.driverappViewTrip.clearGeoJson();
        this.$refs.driverappViewTrip.clearMarker();
        this.$refs.driverappViewTrip.initMap();
        setTimeout(() => {
          this.$refs.driverappViewTrip.loadRoutes(
            this.tripRoute,
            this.ordersLocation.locations.locations,
            this.ordersLocation.locations.warehouse
          );
        }, 500);
      }
    },
    tripPause(id, status) {
      let payload = {
        id: id,
        data: {
          status: status,
        },
      };
      this.$store
        .dispatch("driverapp/DRIVER_DUTY", payload)
        .then((response) => {
          this.$store.dispatch("driverapp/GET_DRIVER_DETAILS").then((res) => {
            if (res.trip != null) {
              this.$store.dispatch("driverapp/GET_TRIP_DETAILS", res.trip);
            }
          });
        });
    },
    tripStatusChange(id, status) {
      let payload = {
        id: id,
        data: {
          status: status,
        },
      };

      this.$store
        .dispatch("driverapp/ACTIVE_TRIP", payload)
        .then((response) => {
          this.$store.dispatch("driverapp/GET_DRIVER_DETAILS").then((res) => {
            if (res.trip != null) {
              this.$store.dispatch("driverapp/GET_TRIP_DETAILS", res.trip);
            }
            this.$notifier.showMessage({
              content: `${status} Order Successfuly!`,
              color: "success",
            });
          });

          this.$forceUpdate();
        });
    },
    OrderTextStatus(status) {
      switch (status) {
        case "unassigned":
          return "Unassigned";
        case "assigned":
          return "Assigned";
        case "pickedup":
          return "Shipped";
        case "partially_delivered":
          return "Partially Delivered";
        case "successful":
          return "Delivered";
        case "failed":
          return "Returned";
        case "cancelled":
          return "Cancelled";
      }
    },

    coloredOrderStatus(status) {
      switch (status) {
        case "unassigned":
          return "unassigned";
        case "assigned":
          return "assigned";
        case "pickedup":
          return "Shipped";
        case "partially_delivered":
          return "partially_delivered";
        case "successful":
          return "successful";
        case "failed":
          return "failed";
        case "cancelled":
          return "cancelled";
      }
    },
    openDeliveredItemDialog(id) {
      this.$store
        .dispatch("driverapp/GET_ORDER_DETAILS", id)
        .then((response) => {
          this.openDeliveredItemFormDialog = true;
          this.$store.dispatch("driverapp/GET_PARTIALLY_REASON");
        });
    },
    openReturnOrderDialog(id) {
      this.$store
        .dispatch("driverapp/GET_ORDER_DETAILS", id)
        .then((response) => {
          this.$store.dispatch("driverapp/GET_FAILED_REASONS").then((response) => {
            this.openReturnOrderFormDialog = true;
          })
        });
    },
  },
};
</script>


<style scoped lang="scss">
@import "@/assets/scss/variables.scss";
.v-tab {
  background-color: map-get($colors-custom, "light", "light_black");
  color: white !important;
}
.v-tab--active {
  background-color: map-get($colors-custom, "solid", "primary");
  color: white;
}
.v-expansion-panel-content .v-expansion-panel-content__wrap {
  padding: 0 !important;
}
.d-app-card-title {
  font-size: 13px;
  font-weight: 400;
  padding: 0;
  margin: 0;
}
.d-app-card-text {
  font-size: 13px;
  line-height: 23px;
  padding: 0;
  margin: 0;
}
.text--bold {
  font-weight: 900 !important;
}
.get-last {
  margin-bottom: 10%;
}
</style>