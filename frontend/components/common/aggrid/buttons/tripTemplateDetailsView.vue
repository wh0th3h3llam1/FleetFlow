<template>
  <div>
    <v-tooltip top>
      <template v-slot:activator="{ on, attrs }">
        <v-btn
          class="mt-2 edit text-white"
          small
          v-bind="attrs"
          v-on="on"
          @click="openTemplateEditDialog"
          depressed
        >
          <v-icon small class="ma-0">mdi-pencil</v-icon>
        </v-btn>
      </template>
      <span>Edit Details</span>
    </v-tooltip>

    <v-tooltip top>
      <template v-slot:activator="{ on, attrs }">
        <v-btn
          v-if="userPermissions.trip.change"
          class="mt-2 grey text-white"
          v-bind="attrs"
          v-on="on"
          small
          @click="openTemplateViewDialog"
          depressed
        >
          <v-icon small class="ma-0">mdi-eye</v-icon>
        </v-btn>
      </template>
      <span>View Details</span>
    </v-tooltip>
  </div>
</template>

<script>
import { makeInstance, encryptLocal } from "~/assets/js/encryptLocal";

export default {
  data() {
    return {
      userPermissions: encryptLocal.getItem("permissions"),
    };
  },
  methods: {
    openTemplateViewDialog() {
      this.$parent.$parent.openForm(true, false, this.params.data);
    },
    openTemplateEditDialog() {
      this.$parent.$parent.editTemplate(this.params.data.id, false, true);
    },
  },
  beforeCreate() {
    if (encryptLocal == null) {
      makeInstance(localStorage.getItem("user"));
    }
  },
};
</script>

<style>
</style>