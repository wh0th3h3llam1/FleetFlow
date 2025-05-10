<template>
  <div>
    <v-select
      dense
      hide-details
      class="float-left"
      style="width: 60px"
      :items="itemsPerPageValues"
      v-model="itemsPerPage"
    ></v-select>
    <v-btn
      :disabled="pageNo == 1"
      x-small
      fab
      text
      class="rounded-lg elevation-0"
      @click="previousPage()"
    >
      <v-icon>mdi-arrow-left</v-icon>
    </v-btn>
    <span class="pa-2">
      <span>{{ pageNo }}</span>
      <span>/</span>
      <span>{{ numOfPages }}</span>
    </span>
    <v-btn
      x-small
      fab
      text
      :disabled="pageNo == numOfPages || numOfPages == 0"
      class="rounded-lg elevation-0"
      @click="nextPage()"
    >
      <v-icon>mdi-arrow-right</v-icon>
    </v-btn>
  </div>
</template>

<script>
export default {
  props: {
    pageNo: {
      require: true,
    },
    numOfPages: {
      require: true,
    },
    pageSize: {
      require: true,
    },
  },
  computed: {
    itemsPerPageValues() {
      return [10, 20, 50, 100];
    },
    itemsPerPage: {
      get() {
        return this.pageSize;
      },
      set(value) {
        this.$emit("itemsPerPageChange", value);
      },
    },
  },
  methods: {
    previousPage() {
      this.$emit("prevPage");
    },
    nextPage() {
      this.$emit("nextPage");
    },
  },
};
</script>

<style>
</style>