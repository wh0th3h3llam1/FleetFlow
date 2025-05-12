<template>
  <v-dialog v-model="openRemarkCardDialog" scrollable width="700">
    <v-card>
      <v-card-title class="background-primary text-white px-3 py-2">
        <span class="text-subtitle-1 text-uppercase">Remarks </span>
        <v-spacer></v-spacer>
        <v-btn
          depressed
          color="white"
          icon
          small
          @click="openRemarkCardDialog = false"
        >
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>
      <v-card-text class="pa-0">
        <v-row class="px-8 my-4" no-gutters>
          <v-col cols="12" v-if="orderDetails.status == 'cancelled'">
            <h6 class="body-1" v-if="orderDetails.cancellation_remarks">
              {{ orderDetails.cancellation_remarks }}
            </h6>
            <h6 class="body-1" v-else>No Remarks</h6>
            <span class="caption">{{ orderDetails.cancelled_time }}</span>
          </v-col>
          <v-col
            cols="12"
            v-else-if="
              orderDetails.status == 'successful' ||
              orderDetails.status == 'failed' ||
              orderDetails.status == 'partially_delivered'
            "
          >
            <h6 class="body-1" v-if="orderDetails.remarks">
              {{ orderDetails.remarks }}
            </h6>
            <h6 class="body-1" v-else>No Remarks</h6>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>


<script>
export default {
  data() {
    return {};
  },
  props: {
    value: Boolean,
    orderDetails: Object,
  },
  computed: {
    openRemarkCardDialog: {
      get() {
        return this.value;
      },
      set(value) {
        this.$emit("input", value);
      },
    },
  },
};
</script>