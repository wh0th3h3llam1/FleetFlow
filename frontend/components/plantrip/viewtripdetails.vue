<template>
  <div class="px-3" style="height: 92vh; display: flex; flex-direction: column">
    <v-card-title class="d-flex justify-space-between">
      <!-- :class="getColor(currentTrip.status)" -->
      <div>
        <h4
          class="
            text-lg-subtitle-1 text-xl-h6
            font-weight-bold
            text-uppercase
            primary--text
          "
        >
          Trip Information
        </h4>
      </div>
      <div class="d-flex justify-center">
        <v-tooltip bottom>
          <template v-slot:activator="{ on, attrs }">
            <v-btn
              depressed
              :small="$vuetify.breakpoint.lgAndDown"
              class="white"
              style="width: 30px !important"
              v-bind="attrs"
              v-on="on"
            >
              <v-icon :small="$vuetify.breakpoint.lgAndDown">mdi-pencil</v-icon>
            </v-btn>
          </template>
          <span>Edit Trip</span>
        </v-tooltip>
        <v-tooltip bottom>
          <template v-slot:activator="{ on, attrs }">
            <v-btn
              depressed
              :small="$vuetify.breakpoint.lgAndDown"
              class="white"
              style="width: 30px !important"
              v-bind="attrs"
              v-on="on"
            >
              <v-icon :small="$vuetify.breakpoint.lgAndDown">mdi-book</v-icon>
            </v-btn>
          </template>
          <span>Trip Logs</span>
        </v-tooltip>
        <v-tooltip bottom>
          <template v-slot:activator="{ on, attrs }">
            <v-btn
              depressed
              :small="$vuetify.breakpoint.lgAndDown"
              class="white"
              style="width: 30px !important"
              v-bind="attrs"
              v-on="on"
            >
              <v-icon :small="$vuetify.breakpoint.lgAndDown"
                >mdi-share-variant</v-icon
              >
            </v-btn>
          </template>
          <span>Share</span>
        </v-tooltip>
        <v-tooltip bottom>
          <template v-slot:activator="{ on, attrs }">
            <v-btn
              depressed
              :small="$vuetify.breakpoint.lgAndDown"
              class="white"
              style="width: 30px !important"
              v-bind="attrs"
              v-on="on"
            >
              <v-icon :small="$vuetify.breakpoint.lgAndDown"
                >mdi-map-marker</v-icon
              >
            </v-btn>
          </template>
          <span>Change Map Coordinates</span>
        </v-tooltip>
      </div>
    </v-card-title>
    <hr class="primary" />
    <v-card-text class="pa-0 px-4 overflow-y-auto">
      <v-row no-gutters class="px-4">
        <v-col cols="6" class="pt-6">
          <span>
            <v-icon class="mr-5" small color="primary">mdi-cart</v-icon>
            Trip-000-001
          </span>
        </v-col>
        <v-col cols="6" class="pt-6">
          <span class="text-capitalize">
            <v-icon class="mr-5" small color="primary"
              >mdi-checkbox-blank</v-icon
            >
            Active
          </span>
        </v-col>
        <v-col cols="6" class="pt-6" v-if="currentTrip.trip_date">
          <span small>
            <v-icon class="mr-5" small color="primary"
              >mdi-calendar-check</v-icon
            >
            10-07-2021 Last update
          </span>
        </v-col>
        <v-col cols="6" class="pt-6">
          <span small>
            <v-icon class="mr-5" small color="primary"
              >mdi-page-layout-header</v-icon
            >
            project 1
          </span>
        </v-col>
        <v-col cols="6" class="pt-6" v-if="currentTrip.trip_start">
          <span small style="position: relative">
            <v-icon class="mr-5" small color="primary">mdi-truck</v-icon>
            <v-icon
              class="mr-5"
              style="
                position: absolute;
                left: 11px;
                top: -10px;
                font-size: 14px;
              "
              small
              color="primary"
              >mdi-timer</v-icon
            >
            10-07-2021
          </span>
        </v-col>
        <v-col cols="6" class="pt-6">
          <span small style="position: relative">
            <v-icon class="mr-5" small color="primary"> mdi-truck </v-icon>
            <v-icon
              class="mr-5"
              style="
                position: absolute;
                left: 11px;
                top: -10px;
                font-size: 14px;
              "
              small
              color="primary"
              >mdi-timelapse</v-icon
            >
            11-07-2021
          </span>
        </v-col>
      </v-row>

      <v-row no-gutters class="pt-4 pb-3">
        <v-col cols="12">
          <span class="text-body-1"> Driver Details </span>
          <hr class="primary mt-2" />
        </v-col>

        <v-col cols="12">
          <v-row no-gutters class="px-4">
            <v-col cols="6" class="pt-6">
              <span small>
                <v-icon class="mr-5" small color="primary"
                  >mdi-account-circle</v-icon
                >
                Ajit patel
              </span>
            </v-col>
            <v-col cols="6" class="pt-6">
              <span small>
                <v-icon class="mr-5" small color="primary"
                  >mdi-cellphone</v-icon
                >
                7852000001
              </span>
            </v-col>
            <v-col cols="6" class="pt-6">
              <span small>
                <v-icon class="mr-5" small color="primary">mdi-truck</v-icon>
                Dx-000-1001
              </span>
            </v-col>
            <v-col cols="6" class="pt-6">
              <span small style="position: relative">
                <v-icon class="mr-5" small color="primary"> mdi-truck </v-icon>
                <v-icon
                  class="mr-5"
                  style="
                    position: absolute;
                    left: 11px;
                    top: -10px;
                    font-size: 14px;
                  "
                  small
                  color="primary"
                  >mdi-lan</v-icon
                >
                Open Body
              </span>
            </v-col>
          </v-row>
        </v-col>
        <v-col cols="12" class="d-flex justify-left mt-12">
          <PieChart :data="datacollection" :options="options" :height="150" />
        </v-col>
      </v-row>

      <v-row no-gutters class="pt-4 pb-3">
        <v-col cols="12">
          <span class="text-body-1"> Order Details </span>
        </v-col>

        <v-col cols="12">
          <v-row no-gutters class="px-4"> </v-row>
        </v-col>

        <v-col cols="12" class="px-1 pb-2 pt-4">
          <hr class="primary mt-2" />
          <v-row no-gutters>
            <v-col
              cols="4"
              class="
                pa-4
                d-flex
                justify-center
                align-center
                border-right-primary
              "
            >
              <span> Successful </span>
            </v-col>
            <v-col
              cols="4"
              class="d-flex justify-center align-center border-right-primary"
            >
              <span> Failed </span>
            </v-col>

            <v-col cols="4" class="d-flex justify-center align-center">
              <span> Total </span>
            </v-col>

            <v-col cols="4" class="d-flex justify-center border-right-primary">
              <span v-if="currentTrip.order_count"> 10 </span>
              <span v-else> N/A </span>
            </v-col>
            <v-col cols="4" class="d-flex justify-center border-right-primary">
              <span v-if="currentTrip.order_count"> 1 </span>
              <span v-else> N/A </span>
            </v-col>
            <v-col cols="4" class="d-flex justify-center">
              <span v-if="currentTrip.order_count"> 21 </span>
              <span v-else> N/A </span>
            </v-col>
          </v-row>
          <hr class="primary mt-2" />
        </v-col>

        <v-col cols="12">
          <v-row no-gutters class="px-4">
            <v-col cols="6" class="text-body-2 py-1">Number Of orders </v-col>
            <v-col
              cols="6"
              class="text-subtitle-1 d-flex justify-end py-1 font-weight-bold"
            >
              <span v-if="currentTrip.trip_orders">2</span>
              <span v-else>N/A</span>
            </v-col>
            <v-col cols="6" class="text-body-2 py-1"
              >Number of Customers
            </v-col>
            <v-col
              cols="6"
              class="text-subtitle-1 d-flex justify-end py-1 font-weight-bold"
            >
              <span>2</span>
            </v-col>
            <v-col cols="6" class="text-body-2 py-1">Total Quantity </v-col>
            <v-col
              cols="6"
              class="text-subtitle-1 d-flex justify-end py-1 font-weight-bold"
            >
              <span>101</span>
            </v-col>
            <v-col
              cols="6"
              class="text-body-2 py-1"
              v-if="currentTrip.planned_distance"
            >
              Planned Trip Distance
            </v-col>
            <v-col
              cols="6"
              class="text-subtitle-1 d-flex justify-end py-1 font-weight-bold"
              v-if="currentTrip.planned_distance"
            >
              <span>{{ currentTrip.planned_distance }} Km</span>
            </v-col>

            <v-col cols="6" class="text-body-2 py-1"
              >Planned Trip Duration
            </v-col>
            <v-col
              cols="6"
              class="text-subtitle-1 d-flex justify-end py-1 font-weight-bold"
            >
              <span>1 Day 2 Hours</span>
            </v-col>
            <v-col cols="6" class="text-body-2 py-1"
              >Actual Trip Distance
            </v-col>
            <v-col
              cols="6"
              class="text-subtitle-1 d-flex justify-end py-1 font-weight-bold"
            >
              <span>452 Km</span>
            </v-col>

            <v-col cols="6" class="text-body-2 py-1"
              >Actual Trip Duration
            </v-col>
            <v-col
              cols="6"
              class="text-subtitle-1 d-flex justify-end py-1 font-weight-bold"
            >
              <span>1 Day 3 Hours</span>
            </v-col>
          </v-row>
        </v-col>
      </v-row>

      <v-row no-gutters class="mt-3">
        <v-col cols="12">
          <span class="text-body-1">Logs </span>
          <hr class="primary my-2" />
        </v-col>
        <v-col cols="12">
          <v-timeline dense>
            <v-timeline-item>
              <v-card>
                <v-card-title class="py-1 headline">
                  <span class="text-xl-h6 text-lg-body-2">Trip Started</span>
                </v-card-title>
                <v-card-text class="pt-1">
                  <span> This pickup by driver 10:19 Am</span>
                </v-card-text>
              </v-card>
            </v-timeline-item>
          </v-timeline>
        </v-col>
      </v-row>
    </v-card-text>
  </div>
</template>

<script>
import PieChart from "~/components/common/charts/PieChart.vue";
export default {
  components: {
    PieChart,
  },
  data() {
    return {
      tripStatus: "active",
      containerHeight: null,
      datacollection: {
        labels: ["Break Time", "Travelling Time", "Processing Time"],
        datasets: [
          {
            backgroundColor: ["#ADACAC", "#D0CFCF", "#F2F2F2"],
            data: [10, 30, 10],
          },
        ],
      },
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
    currentTrip() {
      return this.$store.state.trip.currentTrip;
    },
  },
  methods: {
    getColor(tripStatus) {
      switch (tripStatus) {
        case "scheduled":
          return "orange";
        case "active":
          return "blue";
        case "completed":
          return "pgreen";
        case "cancelled":
          return "red";
      }
    },
  },
  mounted() {
    if (process.browser) {
      if (this.$vuetify.breakpoint.xl) {
        this.containerHeight =
          ((window.innerHeight / 100) * 78).toFixed() + "px";
      } else if (this.$vuetify.breakpoint.lg) {
        this.containerHeight =
          ((window.innerHeight / 100) * 74).toFixed() + "px";
      }
    }
  },
};
</script>

<style scoped>
</style>

