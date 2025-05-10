<template>
  <div>
    <v-tooltip top>
      <template v-slot:activator="{ on, attrs }">
        <v-btn
          class="mt-2 edit text-white"
          small
          v-bind="attrs"
          v-on="on"
          v-if="userPermissions.project && userPermissions.project.change"
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
          class="mt-2 grey text-white"
          small
          v-if="userPermissions.project && userPermissions.project.change"
          v-bind="attrs"
          v-on="on"
          @click="viewZones()"
          depressed
        >
          <v-icon small class="ma-0">mdi-eye</v-icon>
        </v-btn>
      </template>
      <span>View Project Zones</span>
    </v-tooltip>
  </div>
</template>


<script>
import { makeInstance, encryptLocal } from "~/assets/js/encryptLocal";

export default {
  data() {
    return {
      loader: false,
      openProjectForm: false,
      userPermissions: encryptLocal.getItem("permissions"),
    };
  },
  computed: {},
  methods: {
    btnClickedHandler() {
      // this.params.clicked(this.params.value);
      this.$parent.$parent.editProject(this.params.data.id);
    },
    viewZones() {
      this.$parent.$parent.viewZonesHandler(this.params.data);
    },
  },
  beforeCreate() {
    if (encryptLocal == null) {
      makeInstance(localStorage.getItem("user"));
    }
  },
};
</script>