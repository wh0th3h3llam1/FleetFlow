<template>
  <div>
    <v-tooltip top>
      <template v-slot:activator="{ on, attrs }">
        <v-btn
          class="edit text-white"
          small
          v-bind="attrs"
          v-on="on"
          v-if="userPermissions.dashuser && userPermissions.dashuser.change"
          @click="btnClickedHandler"
          depressed
        >
          <v-icon small class="ma-0">mdi-pencil</v-icon>
        </v-btn>
      </template>
      <span>Edit User</span>
    </v-tooltip>

    <v-tooltip top>
      <template v-slot:activator="{ on, attrs }">
        <v-btn
          class="delete darken-1 text-white"
          small
          v-bind="attrs"
          v-on="on"
          v-if="userPermissions.dashuser && userPermissions.dashuser.delete"
          @click="btnDeleteUser()"
          depressed
        >
          <v-icon small class="ma-0">mdi-delete</v-icon>
        </v-btn>
      </template>
      <span>Delete User</span>
    </v-tooltip>
  </div>
</template>

<script>
import { makeInstance, encryptLocal } from "~/assets/js/encryptLocal";

export default {
  data() {
    return {
      openUserForm: false,
      userPermissions: encryptLocal.getItem("permissions"),
    };
  },
  computed: {},
  methods: {
    async btnClickedHandler() {
      this.$parent.$parent.editUser(this.params.data.id);
    },
    btnDeleteUser() {
      this.$parent.$parent.deleteUser(this.params.data.id);
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