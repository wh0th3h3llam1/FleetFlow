<template>
  <v-dialog
    v-model="orderDetailsDialog"
    scrollable
    width="80%"
    max-width="1000px"
  >
    <v-card>
      <v-card-title class="background-primary py-2 px-4">
        <span class="text-uppercase text-white text-body-1">Order Details</span>
        <v-spacer />
        <v-btn fab depressed x-small @click="closeDialog">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>
      <v-card-text class="pa-0">
        <v-row no-gutters>
          <v-col cols="7">
            <CommonOrderdetail :orderDetail="orderDetails" />
          </v-col>
          <v-col cols="5" class="border-left-light_grey">
            <CommonOrderlogs :orderDetail="orderDetails" />
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  props: {
    value: Boolean,
  },
  data() {
    return {};
  },
  computed: {
    orderDetails() {
      return this.$store.state.order.orderDetailStore.order;
    },
    orderDetailsDialog: {
      get() {
        return this.value;
      },
      set(value) {
        this.$emit("input", value);
      },
    },
  },
  methods: {
    closeDialog() {
      this.orderDetailsDialog = false;
    },
  },
};
</script>

<style>
</style>