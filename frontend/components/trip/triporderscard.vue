<template>
  <div>
    <v-row no-gutters>
      <v-col cols="10" class="cf-card-space">
        <v-tooltip right>
          <template v-slot:activator="{ on, attrs }">
            <span
              v-bind="attrs"
              v-on="on"
              class="cf-card-text font-weight-bold"
            >
              <v-icon class="pr-1 primary--text cf-icon">mdi-cart</v-icon>
              {{ order.reference_number }}
            </span>
          </template>
          <span>Reference Number</span>
        </v-tooltip>
      </v-col>
      <v-col cols="2" class="d-flex justify-end cf-card-space">
        <v-checkbox
          class="ma-0 pa-0"
          hide-details
           :input-value="isChecked"
          @change="toggleOrderSelection($event, index)"
        ></v-checkbox>
      </v-col>
    </v-row>
    <v-row no-gutters>
      <v-col cols="12" class="cf-card-space">
        <v-icon class="pr-1 primary--text cf-icon"> mdi-account-box </v-icon>
        <span class="cf-card-text font-weight-noraml">
          {{ order.customer_name }}
        </span>
      </v-col>
      <v-col cols="6" class="cf-card-space">
        <v-icon class="pr-1 primary--text cf-icon"> mdi-calendar-check </v-icon>
        <span class="cf-card-text font-weight-normal text-capitalize">
          {{ order.execution_date }} | {{ order.payment_type }}
        </span>
      </v-col>
      <v-col cols="6" class="text-right pr-3 cf-card-space">
        <span
          :color="coloredOrderStatus(order.status)"
          class="caption text-capitalize"
        >
          {{ order.status }}
        </span>
        <v-avatar
          :color="coloredOrderStatus(order.status)"
          size="16"
          class="ml-2"
        >
        </v-avatar>
      </v-col>
    </v-row>
  </div>
</template>
<script>
export default {
  props: {
    order: Object,
    index: Number,
    isChecked:Boolean,
  },
  data() {
    return {};
  },
  methods: {
    toggleOrderSelection(isChecked, orderIndex) {
      this.$emit("sendData",isChecked, orderIndex);
    },
    coloredOrderStatus(status) {
      switch (status) {
        case "unassigned":
          return "#3f3f3f";
        case "assigned":
          return "#1ab7d0";
        case "picked_up":
          return "#f28c33";
        case "delivery-attempted":
          return "#15895f";
        case "delivered":
          return "#79c267";
        case "returned":
          return "#9e1d1d";
        case "cancelled":
          return "#ff6663";
        default:
          return "#ffffff";
      }
    },
  },
};
</script>