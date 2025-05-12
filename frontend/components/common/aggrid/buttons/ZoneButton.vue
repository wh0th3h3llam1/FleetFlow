<template>
  <div>
    <v-tooltip top>
      <template v-slot:activator="{ on, attrs }">
        <v-btn
          class="mt-2 edit text-white"
          small
          v-bind="attrs"
          v-on="on"
          v-if="userPermissions.zone && userPermissions.zone.change"
          @click="btnClickedHandler"
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
          class="mt-2 delete darken-1 text-white"
          small
          v-bind="attrs"
          v-on="on"
          v-if="userPermissions.zone && userPermissions.zone.delete"
          @click="btnDeleteZone"
          depressed
        >
          <v-icon small class="ma-0">mdi-delete</v-icon>
        </v-btn>
      </template>
      <span>Delete Details</span>
    </v-tooltip>
  </div>
</template>

<script>
import { makeInstance, encryptLocal } from "~/assets/js/encryptLocal";

export default {
  data() {
    return {
      openZoneForm: false,
      userPermissions: encryptLocal.getItem("permissions"),
    };
  },
  computed: {},
  methods: {
    async btnClickedHandler() {
      this.$parent.$parent.editZone(this.params.data.id);
    },
    btnDeleteZone() {
      this.$parent.$parent.deleteZone(this.params.data.id);
    },
  },
  mounted() {},
  beforeCreate() {
    if (encryptLocal == null) {
      makeInstance(localStorage.getItem("user"));
    }
  },
};
</script>