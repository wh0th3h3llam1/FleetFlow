<template>
  <v-row no-gutters v-if="error.statusCode === 404 || error.statusCode === 500">
    <v-col cols="12" class="d-flex justify-center">
      <NuxtLink to="/"> Home page </NuxtLink>
    </v-col>
    <v-col cols="12" class="d-flex justify-center">
      <v-img
        contain
        max-height="80%"
        max-width="80%"
        :lazy-src="
          error.statusCode === 404 ? '/404_error.svg' : '/500_error.svg'
        "
        :src="error.statusCode === 404 ? '/404_error.svg' : '/500_error.svg'"
      ></v-img>
    </v-col>
  </v-row>
</template>

<script>
export default {
  name:"error",
  layout: "empty",
  props: {
    error: {
      type: Object,
      default: null,
    },
  },
  data() {
    return {
      pageNotFound: "404 Not Found",
      otherError: "An error occurred",
    };
  },
  head() {
    const title =
      this.error.statusCode === 404 ? this.pageNotFound : this.otherError;
    return {
      title,
    };
  },
};
</script>

<style scoped>
h1 {
  font-size: 20px;
}
</style>
