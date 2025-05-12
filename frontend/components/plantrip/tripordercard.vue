<template>
  <div class="card mt-1">
    <v-row no-gutters>
      <v-col cols="10" class="cf-card-space">
        <v-tooltip right>
          <template v-slot:activator="{ on, attrs }">
            <span
              v-bind="attrs"
              v-on="on"
              class="cf-card-text font-weight-bold"
            >
              <v-icon class="pr-1 text-grey cf-icon">mdi-cart</v-icon>
              {{ order.reference_number }}
            </span>
          </template>
          <span>Reference Number</span>
        </v-tooltip>
      </v-col>
      <v-col cols="2" class="d-flex justify-end cf-card-space">
        <v-checkbox
          @change="toggleOrderSelection($event, index)"
          :input-value="isChecked"
          class="ma-0 pa-0"
          hide-details
        >
        </v-checkbox>
      </v-col>
    </v-row>
    <v-row no-gutters>
      <v-col cols="12" class="cf-card-space">
        <v-icon class="pr-1 text-grey cf-icon"> mdi-account-box </v-icon>
        <span class="cf-card-text font-weight-noraml">
          {{ order.customer_name }}
        </span>
      </v-col>
      <v-col cols="6" class="cf-card-space"> </v-col>
    </v-row>
    <v-row no-gutters>
      <v-col cols="10" class="cf-card-space">
        <v-icon class="pr-1 text-grey cf-icon"> mdi-calendar-check </v-icon>
        <span class="cf-card-text font-weight-normal text-capitalize">
          {{ order.delivery_date }}
        </span>
      </v-col>
      <v-col
        cols="2"
        class="d-flex justify-end cf-card-space"
        v-if="order.rejection_reason_list && order.rejection_reason_list.length != 0"
      >
        <v-tooltip right>
          <template v-slot:activator="{ on, attrs }">
            <span
              v-bind="attrs"
              v-on="on"
              class="cf-card-text font-weight-bold"
            >
              <v-icon
                @click="openRejectionDialog(order.rejection_reason_list)"
                class="mr-2 red--text"
              >
                mdi-information
              </v-icon>
            </span>
          </template>
          <span>Rejection Reason</span>
        </v-tooltip>
      </v-col>
    </v-row>
  </div>
</template>

<script>
export default {
  props: {
    order: Object,
    index: Number,
    isChecked: Boolean,
  },
  methods: {
    openRejectionDialog(reason){
      this.$emit("openDialog",reason);
    },
    toggleOrderSelection(isChecked, orderIndex) {
      this.$emit("sendData", isChecked, orderIndex);
    },
  },
};
</script>