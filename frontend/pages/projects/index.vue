<template>
  <div>
    <ProjectProjectlist />
  </div>
</template>

<script>
export default {
  data() {
    return {};
  },
  mounted() {
    this.$store.dispatch(
      "trip_planing_templates/GET_ALL_PLANNING_TEMPLATES",
      {}
    );
  },
};
</script>

<style>
</style>