<template>
  <div>
    <v-tooltip top>
      <template v-slot:activator="{ on, attrs }">
        <v-btn
          class="mt-2 edit text-white"
          small
          v-bind="attrs"
          v-on="on"
          @click="btnClickedHandler"
          v-if="userPermissions.itemmaster && userPermissions.itemmaster.change"
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
      openItemForm: false,
      loader: false,
      userPermissions: encryptLocal.getItem("permissions"),
    };
  },
  methods: {
    btnClickedHandler() {
      this.$parent.$parent.editItem(this.params.data.id);
    },
  },
  beforeCreate() {
    if (encryptLocal == null) {
      makeInstance(localStorage.getItem("user"));
    }
  },
};
</script>