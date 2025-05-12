
<template>
  <v-app>
    <CommonDriverAppHeader>
      <nuxt />
    </CommonDriverAppHeader>
  </v-app>
</template>


<script>
import { Loader } from "@googlemaps/js-api-loader";
export default {
  name: "driverAppLayout",
  async mounted() {
    if (window.google == undefined) {
      const loader = new Loader({
        apiKey: process.env.mapsKey,
        version: "weekly",
        libraries: ["places", "geometry", "drawing"],
      });
      await loader.load();
    }
  },
  created() {
    this.$store.dispatch("driverapp/GET_DRIVER_DETAILS").then((res) => {
      if (res.trip != null) {
        this.$store.dispatch("driverapp/GET_TRIP_DETAILS", res.trip);
      }
    });
  },
};
</script>
