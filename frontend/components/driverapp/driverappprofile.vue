<template>
  <v-dialog v-model="openProfile" width="500">
    <v-card>
      <v-card-title class="primary py-0 pl-5 pr-2" style="height: 45px">
        <h5 class="white--text">Profile</h5>
        <v-spacer></v-spacer>
        <v-btn color="white" text @click="closeProfile">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>

      <v-card-text>
        <v-row class="mt-6 mb-4">
          <v-col cols="12" class="text-center pb-6">
            <v-avatar size="100">
              <v-img
                contain
                :src="
                  driverDetails.profile_image
                    ? driverDetails.profile_image
                    : image
                "
              />
            </v-avatar>
          </v-col>
          <v-col cols="2" class="text-center">
            <v-icon>mdi-account</v-icon>
          </v-col>
          <v-col cols="4" class="text-left">
            <h5 v-if="driverDetails.first_name">
              {{ driverDetails.first_name }}
            </h5>
          </v-col>
          <v-col cols="2" class="text-center">
            <v-icon style="font-size: 20px">mdi-truck</v-icon>
          </v-col>
          <v-col cols="4" class="text-left">
            <h5 v-if="driverDetails.vehicle">{{ driverDetails.vehicle }}</h5>
          </v-col>
          <v-col cols="2" class="text-center">
            <v-icon style="font-size: 20px">mdi-credit-card</v-icon>
          </v-col>
          <v-col cols="4" class="text-left">
            <h5 v-if="driverDetails.license_number">
              {{ driverDetails.license_number }}
            </h5>
          </v-col>
          <v-col cols="2" class="text-center">
            <!-- <v-icon >mdi-truck</v-icon> -->
          </v-col>
          <v-col cols="4" class="text-left">
            <!-- <h5>Dx-00-0001</h5> -->
          </v-col>
          <v-col cols="2" class="text-center">
            <v-icon style="font-size: 22px">mdi-timer-outline</v-icon>
          </v-col>
          <v-col cols="4" class="text-left">
            <h5 v-if="driverDetails.shift_start">
              {{ driverDetails.shift_start }}
            </h5>
          </v-col>
          <v-col cols="2" class="text-center">
            <v-icon style="font-size: 20px">mdi-timer</v-icon>
          </v-col>
          <v-col cols="4" class="text-left">
            <h5 v-if="driverDetails.shift_end">
              {{ driverDetails.shift_end }}
            </h5>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
import image from "@/static/user.png";
export default {
  props: {
    value: Boolean,
  },
  data() {
    return {
      image: image,
    };
  },
  computed: {
    driverDetails: {
      get() {
        return this.$store.state.driverapp.driverDetails;
      },
      set() {},
    },
    openProfile: {
      get() {
        return this.value;
      },
      set(value) {
        this.$emit("input", value);
      },
    },
  },
  methods: {
    closeProfile() {
      this.openProfile = false;
    },
  },
};
</script>