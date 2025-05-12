<template>
  <v-dialog
    v-model="openTripViewDialog"
    fullscreen
    transition="dialog-bottom-transition"
    persistent
  >
    <v-card class="pa-4">
      <v-card-title>
        <v-row no-gutters>
          <v-col cols="6" class="d-flex align-center justify-start">
            <span
              class="
                text-lg-subtitle-1 text-xl-h6 text-uppercase
                font-weight-black
                primary--text
              "
            >
              Planned Trips
            </span>
          </v-col>
          <v-col cols="6" class="d-flex align-center justify-end">
            <v-btn class="float-right" @click="closeDialog()" small fab icon>
              <v-icon>mdi-close</v-icon>
            </v-btn>
          </v-col>
          <v-col
            v-if="Object.keys(trip).length > 0"
            cols="12"
            class="pt-6 pb-4"
          >
            <v-row no-gutters>
              <v-col cols="12" class="text-left">
                <v-row no-gutters>
                  <v-col cols="2" class="text-center">
                    <span class="font-weight-bold primary--text">
                      {{ trip.cargos_per.chilled }}%
                    </span>
                    <br />
                    <span class="text-caption primary--text"> Chilled </span>
                  </v-col>
                  <v-col cols="2" class="text-center">
                    <span class="font-weight-bold primary--text">
                      {{ trip.cargos_per.dry }}%
                    </span>
                    <br />
                    <span class="text-caption primary--text"> Dry </span>
                  </v-col>
                  <v-col cols="2" class="text-center">
                    <span class="font-weight-bold primary--text">
                      {{ trip.cargos_per.frozen }}%
                    </span>
                    <br />
                    <span class="text-caption primary--text"> Frozen </span>
                  </v-col>
                  <v-col cols="2" class="text-center" v-if="trip.mass !== null">
                    <span class="font-weight-bold primary--text">
                      {{ trip.mass }}
                    </span>
                    <br />
                    <span class="text-caption primary--text"> Weight </span>
                  </v-col>
                  <v-col
                    cols="2"
                    class="text-center"
                    v-if="trip.volume !== null"
                  >
                    <span class="font-weight-bold primary--text">
                      {{ trip.volume }}
                    </span>
                    <br />
                    <span class="text-caption primary--text"> Volume </span>
                  </v-col>
                  <v-col cols="2" class="text-center">
                    <span class="font-weight-bold primary--text">
                      {{ trip.orders_count }}
                    </span>
                    <br />
                    <span class="text-caption primary--text">Orders</span>
                  </v-col>
                </v-row>
              </v-col>
              <v-col cols="2" class="text-center">
                <span class="font-weight-bold primary--text">
                  {{ trip.distance }}
                </span>
                <br />
                <span class="text-caption primary--text"> Distance</span>
              </v-col>
              <v-col cols="2" class="text-center">
                <span class="font-weight-bold primary--text">
                  {{ trip.travelling_time }}
                </span>
                <br />
                <span class="text-caption primary--text">Travelling Time</span>
              </v-col>
              <v-col cols="2" class="text-center">
                <span class="font-weight-bold primary--text">
                  {{ trip.total_time }}
                </span>
                <br />
                <span class="text-caption primary--text"> Total Time</span>
              </v-col>
              <v-col cols="2" class="text-center">
                <span class="font-weight-bold primary--text">
                    {{trip.planned_locations_count}}
                </span>
                <br />
                <span class="text-caption primary--text"> Drop Points</span>
              </v-col>
            </v-row>
          </v-col>
        </v-row>
      </v-card-title>
      <v-row class="pa-0 ma-0">
        <v-col cols="12">
          <CommonGmap
            mapWidth="100%"
            mapHeight="90vh"
            ref="viewTrip"
            :dialog-status="openTripViewDialog"
            :clusterMarkers="true"
          />
        </v-col>
      </v-row>
    </v-card>
  </v-dialog>
</template>
<script>
export default {
  props: {
    value: Boolean,
    trip: {
      type: Object,
      default: {},
    },
  },
  data() {
    return {};
  },
  watch: {
    openTripViewDialog(value) {
      if (value) {
        let interval = setInterval(() => {
          if (this.$refs.viewTrip) {
            this.$refs.viewTrip.clearGeoJson();
            this.$refs.viewTrip.clearMarker();
            this.$refs.viewTrip.initMap();
            this.$refs.viewTrip.loadRoutes(
              this.$store.state.trip_planning.drivingDirections,
              this.$store.state.trip_planning.tripOrdersList,
              this.$store.state.trip_planning.warehouseDetails
            );
            clearInterval(interval);
          }
        }, 100);
      }
    },
  },
  computed: {
    openTripViewDialog: {
      get() {
        return this.value;
      },
      set(value) {
        this.$emit("input", value);
      },
    },
  },
  methods: {
    closeDialog() {
      this.openTripViewDialog = false;
    },
  },
};
</script>