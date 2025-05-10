<template>
  <div style="overflow: scroll;">
    <v-chip
      v-for="(tagName, i) in params.data.assigned_tags"
      :key="i"
      class="mx-1"
      color="primary"
      depressed
      rounded
      small
      >{{ tagName.tag }}</v-chip
    >
  </div>
</template>

<script>
export default {
  data() {
    return {};
  },
};
</script>
