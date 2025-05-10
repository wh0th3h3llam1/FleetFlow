<template>
  <v-app>
    <CommonNavigationDrawer />
    <CommonHeader />
    <v-main style="position: relative">
      <v-alert
        style="
          height: 100%;
          width: 100%;
          position: absolute;
          top: 0;
          left: 0;
          z-index: 4;
          opacity: 0.7;
        "
        dark
        border="top"
        transition="scale-transition"
        class="text-center black d-flex justify-center align-center"
        v-if="$nuxt.isOffline"
      >
        <h1>You are offline</h1>
      </v-alert>
      <v-container
        fluid
        class="pa-0 overflow-y-auto"
        style="height: 100% !important; position: absolute"
      >
        <nuxt />
      </v-container>
      <CommonSnackbar />
      <CommonLoader />
    </v-main>
  </v-app>
</template>

<script>
import { Loader } from "@googlemaps/js-api-loader";
export default {
  name:"default",
  middleware: "auth",
  data() {
    return {};
  },
  methods: {},
  async mounted() {
    if (window.google == undefined) {
      const loader = new Loader({
        apiKey: process.env.mapsKey,
        version: "weekly",
        libraries: ["places", "geometry", "drawing"],
      });
      await loader.load();
    }
    this.$store.dispatch("project/GET_ALL_PROJECT_LIST");
  },
  async beforeCreate() {
    this.loaded = false;
    await this.$store
      .dispatch("profile/GET_USER_PROFILE_INFO")
      .then((result) => {})
      .catch((err) => {
        this.$notifier.showMessage({
          content: "Something went wrong",
          color: "error",
        });
      });
  },
};
</script>
