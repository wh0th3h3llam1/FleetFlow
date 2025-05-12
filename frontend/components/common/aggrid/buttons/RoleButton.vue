<template>
  <div>
    <v-tooltip top>
      <template v-slot:activator="{ on, attrs }">
        <v-btn
          class="mt-2 edit text-white"
          small
          v-bind="attrs"
          v-on="on"
          v-if="userPermissions.role && userPermissions.role.change"
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
          v-bind="attrs"
          v-on="on"
          small
          v-if="
            userPermissions.role &&
            userPermissions.role.delete &&
            params.data.is_deletable
          "
          @click="btnDeleteRole"
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
      openRoleForm: false,
      userPermissions: encryptLocal.getItem("permissions"),
    };
  },
  computed: {},
  methods: {
    async btnClickedHandler() {
      this.$parent.$parent.editRole(this.params.data.id);
    },
    btnDeleteRole() {
      this.$parent.$parent.deleteRole(this.params.data.id);
    },
  },
  beforeCreate() {
    if (encryptLocal == null) {
      makeInstance(localStorage.getItem("user"));
    }
  },
};
</script>