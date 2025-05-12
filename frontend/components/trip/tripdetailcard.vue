<template>
  <div
    @click="$emit('selectTrip')"
    class="
      mb-4
      border-x-light_grey
      border-y-light_grey
      full-width
      background-white
      rounded-lg
    "
    :class="
      selectedTrip != null && selectedTrip.id == trip.id
        ? 'selected-card'
        : null
    "
  >
    <div class="pa-2 background-light_grey rounded-t-lg">
      <v-row dense>
        <v-col cols="6">
          <v-tooltip right>
            <template v-slot:activator="{ on, attrs }">
              <span
                v-bind="attrs"
                v-on="on"
                class="text-body-2 font-weight-bold"
              >
                {{ trip.reference_number }}
              </span>
            </template>
            <span>Reference Number</span>
          </v-tooltip>
        </v-col>
        <v-col cols="6" class="d-flex justify-end">
          <div>
            <span class="caption text-capitalize">
              {{ trip.status }}
            </span>
            <v-avatar
              :class="getTripStatusLightColor(trip.status)"
              size="16"
              class="ml-1"
            ></v-avatar>
          </div>
        </v-col>
      </v-row>
    </div>
    <div class="pa-2">
      <v-row no-gutters>
        <v-col cols="6" class="text-caption">
          <v-tooltip right>
            <template v-slot:activator="{ on, attrs }">
              <span v-on="on" v-bind="attrs">
                {{ trip.driver }}
              </span>
            </template>
            <span>Driver Name</span>
          </v-tooltip>
        </v-col>
        <v-col cols="6" class="text-caption d-flex justify-end">
          <v-tooltip right>
            <template v-slot:activator="{ on, attrs }">
              <span v-on="on" v-bind="attrs">
                <b>{{ trip.driver_number }}</b>
              </span>
            </template>
            <span>Driver Contact Number</span>
          </v-tooltip>
        </v-col>
      </v-row>
      <v-row no-gutters v-if="trip && trip.vehicle_info">
        <v-col cols="6" class="text-caption">
          <v-tooltip right>
            <template v-slot:activator="{ on, attrs }">
              <span v-on="on" v-bind="attrs">
                <v-icon small>mdi-truck</v-icon>
                {{ trip.vehicle_info.vehicle_plate_no }}
              </span>
            </template>
            <span>Assigned Vehicle</span>
          </v-tooltip>
        </v-col>
        <v-col cols="6" class="d-flex justify-end text-caption">
          <v-tooltip right>
            <template v-slot:activator="{ on, attrs }">
              <span v-on="on" v-bind="attrs">
                <b>{{ trip.trip_date }}</b>
              </span>
            </template>
            <span>Trip Date</span>
          </v-tooltip>
        </v-col>
      </v-row>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    trip: {
      required: true,
      type: Object,
    },
  },
  computed: {
    selectedTrip() {
      return this.$store.state.trip.currentTrip;
    },
  },
  methods: {
    getTripStatusLightColor(status) {
      switch (status) {
        case "scheduled":
          return "light_unassigned";
        case "active":
          return "light_assigned";
        case "paused":
          return "light_pickedup";
        case "completed":
          return "light_successful";
      }
    },
  },
};
</script>

<style>
</style>