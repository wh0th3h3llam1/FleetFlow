<template>
  <div style="height: 90vh">
    <!----------------------------------------- Search & Add Order section ----------------------------------------->

    <v-row no-gutters>
      <v-col cols="12" class="pa-2">
        <v-text-field
          label="Search here.."
          prepend-inner-icon="mdi-magnify"
          hide-details="auto"
          outlined
          dense
          clearable
          aria-autocomplete="false"
          class="background-white"
        ></v-text-field>
      </v-col>
    </v-row>
    <div class="overflow-y-auto mt-4" style="height: 80vh">
      <div v-for="(trip, index) in trips" :key="index">
        <div class="card mx-0 mt-1 mb-0">
          <v-row no-gutters>
            <v-col cols="12" class="cf-card-space">
              <v-icon class="pr-1 primary--text cf-icon">
                mdi-account-box
              </v-icon>
              <span class="cf-card-text font-weight-noraml">{{
                trip.customer
              }}</span>
            </v-col>
            <v-col cols="12" class="cf-card-space">
              <v-icon class="pr-1 primary--text cf-icon">
                mdi-card-account-details-outline
              </v-icon>
              <span class="cf-card-text font-weight-noraml">{{
                trip.transport_detail.driver
              }}</span>
            </v-col>
            <v-col cols="12" class="cf-card-space">
              <v-icon class="pr-1 primary--text cf-icon"> mdi-truck </v-icon>
              <span class="cf-card-text font-weight-noraml">
                {{ trip.transport_detail.vehicle }}
              </span>
            </v-col>
            <v-col cols="6" class="cf-card-space">
              <v-icon class="pr-1 primary--text cf-icon">
                mdi-calendar-check
              </v-icon>
              <span class="cf-card-text font-weight-normal text-capitalize">
                {{ trip.date }}
              </span>
            </v-col>
            <v-col cols="6" class="text-right pr-3 cf-card-space"></v-col>
          </v-row>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      tab: null,
    };
  },
  computed: {
    trips() {
      return this.$store.state.trip_planning.tripList;
    },
  },
  methods: {},
  mounted() {},
};
</script>
