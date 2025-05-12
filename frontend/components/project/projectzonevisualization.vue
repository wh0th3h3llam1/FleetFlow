<template>
  <v-dialog
    v-model="viewProjectZones"
    fullscreen
    hide-overlay
    transition="dialog-bottom-transition"
    eager
  >
    <v-card>
      <v-card-title>
        <span>{{ projectOnMap.project_name }}'s Zones Visualization</span>
        <v-spacer></v-spacer>
        <v-btn small icon @click="viewProjectZones = false">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>
      <v-card-text v-if="viewProjectZones">
        <CommonGmap
          mapWidth="100%"
          mapHeight="90vh"
          ref="viewZoneOnMap"
          :dialog-status="viewProjectZones"
          infowindowType="customer"
          :showZones="true"
          :clusterMarkers="true"
        />
        <v-card id="info-box" class="info-card pa-2">
          <span class="text-body-h4 font-weight-bold pr-2">Zone Name :</span
          ><span id="zone_name"></span>
        </v-card>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  props: {
    value: {
      type: Boolean,
      default: false,
      required: true,
    },
  },
  data() {
    return {
      projectOnMap: {},
    };
  },
  computed: {
    viewProjectZones: {
      get() {
        return this.value;
      },
      set(value) {
        this.$emit("input", value);
      },
    },
  },
  methods: {
    viewZones(zone) {
      this.projectOnMap = {};
      this.projectOnMap = zone;
      let params = {
        project_id: zone.project_id,
      };
      this.$store
        .dispatch("project/VIEW_PROJECTS_ZONES", params)
        .then((result) => {
          this.$refs.viewZoneOnMap.initMap();
          this.$refs.viewZoneOnMap.clearGeoJson();
          this.$refs.viewZoneOnMap.clearMarker();
          this.$refs.viewZoneOnMap.loadRoutes(
            result.data.zones,
            result.data.customer_details
          );
          this.viewProjectZones = true;
        });
    },
  },
};
</script>