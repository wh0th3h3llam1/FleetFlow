<template>
  <v-dialog v-model="openDriverRejectDialog" scrollable width="700">
    <v-card>
      <v-card-title class="background-primary text-white px-3 py-2">
        <span class="text-subtitle-1 text-uppercase">Reasons for Unassignment of Driver</span>
        <v-spacer></v-spacer>
        <v-btn
          depressed
          color="white"
          icon
          small
          @click="openDriverRejectDialog = false"
        >
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>
      <v-card-text class="pa-0">
        <h3 class="px-8 pt-4 text-uppercase">Possible Unassignment Reasons</h3>
        <v-row class="px-8 my-4" no-gutters>
          <ul>
            <v-col class="py-1" cols="12" v-for="(item,i) in reason" :key="i">
              <h6 class="body-2">
                <li class="px-1 py-0 text-uppercase">{{ item }}</li>
              </h6>
            </v-col>
          </ul>
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
    reason : Array
  },
  computed: {
    openDriverRejectDialog: {
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