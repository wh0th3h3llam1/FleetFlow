<template>
  <v-overlay :value="showLoader" z-index="1000">
    <v-progress-circular indeterminate size="64"></v-progress-circular>
  </v-overlay>
</template>

<script type="module">
export default {
  props: {},
  data() {
    return {};
  },
  computed: {
    showLoader() {
      return this.$store.state.showLoader;
    },
  },
};
</script>