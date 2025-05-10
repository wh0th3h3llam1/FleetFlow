<template>
  <div>
    <v-tooltip top>
      <template v-slot:activator="{ on, attrs }">
        <v-btn
          class="mt-2 edit text-white"
          small
          v-bind="attrs"
          v-on="on"
          v-if="
            userPermissions.customeraddress &&
            userPermissions.customeraddress.change
          "
          @click="btnClickedHandler()"
          depressed
        >
          <v-icon small class="ma-0">mdi-pencil</v-icon>
        </v-btn>
      </template>
      <span>Edit Details</span>
    </v-tooltip>
  </div>
</template>

<script>
import { makeInstance, encryptLocal } from "~/assets/js/encryptLocal";

export default {
  data() {
    return {
      openCustomerAddressForm: false,
      userPermissions: encryptLocal.getItem("permissions"),
    };
  },
  computed: {},
  methods: {
    async btnClickedHandler() {
      this.$parent.$parent.editCustomer(this.params.data.id);
    },
  },
  beforeCreate() {
    if (encryptLocal == null) {
      makeInstance(localStorage.getItem("user"));
    }
  },
};
</script>