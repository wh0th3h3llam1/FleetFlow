<template>
  <v-btn x-small fab icon text @click="removeRow">
    <v-icon color="red">mdi-delete</v-icon>
  </v-btn>
</template>

<script>
export default {
  methods: {
    removeRow() {
      this.$parent.$parent.$parent.$parent.$parent.removeDataFromRow(this.params.data.oldIndex, this.params.rowIndex);
    },
  },
};
</script>

<style>
</style>