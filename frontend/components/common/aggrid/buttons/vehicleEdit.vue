<template>
  <v-tooltip top>
    <template v-slot:activator="{ on, attrs }">
      <v-btn
        class="mt-2 edit text-white"
        small
        v-bind="attrs"
        v-on="on"
        v-if="userPermissions.vehicle && userPermissions.vehicle.change"
        @click="btnClickedHandler()"
        depressed
      >
        <v-icon small class="ma-0">mdi-pencil</v-icon>
      </v-btn>
    </template>
    <span>Edit Details</span>
  </v-tooltip>
</template>




<script>
import { makeInstance, encryptLocal } from "~/assets/js/encryptLocal";

export default {
  data() {
    return {
      openVehicleForm: false,
      loader: false,
      userPermissions: encryptLocal.getItem("permissions"),
    };
  },
  computed: {},
  methods: {
    btnClickedHandler() {
      this.$parent.$parent.editVehicle(this.params.data.id);
      this.$store.dispatch("customer/customerAddress/GET_TAG_LIST");
    },
  },
  beforeCreate() {
    if (encryptLocal == null) {
      makeInstance(localStorage.getItem("user"));
    }
  },
};
</script>