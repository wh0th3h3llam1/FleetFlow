<template>
  <v-card
    class="mx-auto overflow-hidden rounded-0 d-flex flex-column"
    width="100%"
    rounded-0
    elevation="0"
    height="100vh"
  >
    <div>
      <v-app-bar color="primary accent-4" dark style="position: relative">
        <v-toolbar-title class="d-flex justify-start">
          <v-img :src="whiteLogo" contain height="35" width="100px"></v-img>
        </v-toolbar-title>
        <v-spacer></v-spacer>

        <v-switch
          true-value="on_duty"
          :disabled="driverDetails.status  == 'break'"
          false-value="off_duty"
          :value="driverDetails.status == 'on_duty' ? 'on_duty' : 'off_duty'"
          @change="
            dutyChange($event, driverDetails.id), syncData($event, 'status')
          "
          :label="`${
            driverDetails.status == 'off_duty' ? 'Off Duty' : 'On Duty'
          }`"
          color="white"
          class="mt-5"
        >
        </v-switch>
        <v-app-bar-nav-icon
          large
          @click.stop="drawer = !drawer"
        ></v-app-bar-nav-icon>
      </v-app-bar>

      <v-navigation-drawer v-model="drawer" absolute left temporary>
        <v-list nav dense>
          <v-list-item-group
            v-model="group"
            active-class="primary--text text--primary"
          >
            <v-list-item @click="openProfile">
              <v-list-item-icon>
                <v-icon>mdi-account-circle</v-icon>
              </v-list-item-icon>

              <v-list-item-content>
                <v-list-item-title>Profile</v-list-item-title>
              </v-list-item-content>
            </v-list-item>
            <v-list-item @click="openLogout">
              <v-list-item-icon>
                <v-icon>mdi-logout</v-icon>
              </v-list-item-icon>

              <v-list-item-content>
                <v-list-item-title>Logout</v-list-item-title>
              </v-list-item-content>
            </v-list-item>
          </v-list-item-group>
        </v-list>
      </v-navigation-drawer>

      <DriverappDriverappprofile v-model="openProfileDialog" />

      <v-dialog v-model="logoutdialog" width="500">
        <v-card>
          <v-card-title class="primary py-0 pl-5 pr-2" style="height: 45px">
            <h5 class="white--text text-uppercase">Logout ?</h5>
            <v-spacer></v-spacer>
            <v-btn color="white" text @click="closeLogout">
              <v-icon>mdi-close</v-icon>
            </v-btn>
          </v-card-title>
          <v-card-text>
            <div class="px-4 pt-6 pb-1">
              <h3 color="primary">Are you sure you want to logout ?</h3>
            </div>
          </v-card-text>
          <v-card-actions class="d-flex justify-center light_grey">
            <v-btn color="white" class="primary" text @click="logout">
              Yes
            </v-btn>
            <v-btn color="white" class="primary" text @click="closeLogout">
              No
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </div>

    <v-card-text class="pa-0 d-flex" style="position: relative; height: 100%">
      <slot></slot>
    </v-card-text>
  </v-card>
</template>

<script>
import whiteLogo from "@/static/White-logo.png";
import image from "@/static/user.png";
export default {
  data() {
    return {
      drawer: false,
      group: null,
      image: image,
      tab: null,
      driverActive: "on_duty",
      openProfileDialog: false,
      logoutdialog: false,
      whiteLogo: whiteLogo,
    };
  },
  computed: {
    driverDetails: {
      get() {
        let driver = this.$store.state.driverapp.driverDetails;
        this.driverActive = driver.state;
        return driver;
      },
      set() {},
    },
  },
  methods: {
    dutyChange(status, id) {
      let payload = {
        id: id,
        data: { status: status },
      };
      this.$store.dispatch("driverapp/DRIVER_DUTY", payload);
    },
    syncData(value, key ,subkey) {
      this.$store.commit("driverapp/syncData", { value: value, key: key });
    },
    logout() {
      this.dutyChange('off_duty',this.driverDetails.id);
      this.$store.dispatch("auth/LOGOUT");
      this.closeLogout();
    },
    openProfile() {
      this.openProfileDialog = true;
    },
    openLogout() {
      this.logoutdialog = true;
    },
    closeLogout() {
      this.logoutdialog = false;
    },
  },
  watch: {
    group() {
      this.drawer = false;
    },
  },
};
</script>