<template>
  <v-dialog v-model="openDialog" persistent max-width="600px">
    <v-card class="pa-4">
      <v-card-title>
        <span
          class="
            text-lg-subtitle-1 text-xl-h6 text-uppercase
            font-weight-black
            primary--text
          "
        >
          TiA Recommendation
        </span>
        <v-spacer></v-spacer>
        <v-btn depressed fab class="mt-n3" small @click="closeDialog">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>
      <v-card-text class="pt-3">
        <div>
          <h4 class="text-lg-subtitle-1">
            TIA is a Artificial Intelligent System that recommends you the best route available as per selected Orders, Driver and Vehicle.
          </h4>
          <br>
          <h4 class="text-lg-subtitle-1">
            It considers all the parameters such as order sequence, total order weight/volume as per vehicle weight/volume , delivery coordinates etc. to calculate route and sequence of orders.
          </h4>
        </div>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>
<script>
export default {
  props: {
    openDialog: Boolean
  },
  methods: {
    closeDialog() {
      this.$emit("closeDialog", false);
    },
  },
};
</script>