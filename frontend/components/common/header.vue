<template>
  <v-app-bar clipped-left fixed app>
    <v-toolbar-title class="d-flex">
      <img
        :src="logo"
        height="120px"
        width="180px"
      />
    </v-toolbar-title>
    <v-spacer />
    <div class="pr-3">
      <CommonUsernotifications v-model="openNotifications" />
    </div>

    <v-menu
      v-model="menu"
      :close-on-content-click="false"
      :nudge-width="150"
      min-width="100px"
      offset-y
      transition="slide-y-transition"
    >
      <template v-slot:activator="{ on, attrs }">
        <div v-bind="attrs" v-on="on">
          <v-avatar height="90%">
            <img
              src="~/static/user.png"
              style="width: 95% !important"
              alt="User"
            />
          </v-avatar>
          <span class="text-primary font-weight-bold pl-1"
            >{{ userDetails.first_name }} {{ userDetails.last_name }}</span
          >
        </div>
      </template>
      <v-card elevation="0">
        <v-card-text class="pa-0">
          <v-list>
            <v-list-item @click="openProfileDialog = true">
              <v-icon>mdi-account</v-icon>
              <span class="pl-2">Profile</span>
            </v-list-item>
            <v-list-item @click="openChangePasswordDialog = true">
              <v-icon>mdi-lock-reset</v-icon>
              <span class="pl-2">Change Password</span>
            </v-list-item>
            <v-list-item @click="logout()">
              <v-icon>mdi-logout</v-icon>
              <span class="pl-2">Logout</span>
            </v-list-item>
          </v-list>
        </v-card-text>
      </v-card>
    </v-menu>

    <Profile v-model="openProfileDialog" />
    <ProfileChangepassword v-model="openChangePasswordDialog" />
  </v-app-bar>
</template>

<script>
import { makeInstance, encryptLocal } from "~/assets/js/encryptLocal";
import Logo from "@/static/header_logo.png";

export default {
  data() {
    return {
      menu: false,
      menu1: false,
      logo : Logo,
      openNotifications: false,
      openProfileDialog: false,
      openChangePasswordDialog: false,
    };
  },
  computed: {
    userDetails() {
      return this.$store.state.profile.userProfile;
    },
  },
  methods: {
    logout() {
      this.$store.dispatch("auth/LOGOUT");
    },
  },
  mounted() {
    this.$store
      .dispatch("profile/GET_USER_PROFILE_INFO")
      .then((result) => {
        if (encryptLocal) {
          encryptLocal.setItem("permissions", result.data.permissions);
        }
      })
      .catch((err) => {
        this.$notifier.showMessage({
          content: "Something went wrong",
          color: "error",
        });
      });
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