<template>
  <v-dialog v-model="openWarningDialog" scrollable width="700">
    <v-card>
      <v-card-title class="background-primary text-white px-3 py-2">
        <span class="text-subtitle-1 text-uppercase">Warnings</span>
        <v-spacer></v-spacer>
        <v-btn
          depressed
          color="white"
          icon
          small
          @click="openWarningDialog = false"
        >
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>
      <v-card-text class="pa-0">
        <v-list class="px-4 pt-4" v-if="info.zone_details">
          <v-list-item
            dense
            v-for="(warning, i) in info.zone_details.warnings"
            :key="i"
          >
            <v-alert text dense dismissible type="error" style="width: 100%">
              <span>{{ warning }}</span>
            </v-alert>
          </v-list-item>
        </v-list>
        <v-list v-else class="px-4 pt-4">
          <v-list-item
            dense
            v-for="(warning, i) in info.warnings"
            :key="i"
          >
            <v-alert text dense dismissible type="error" style="width: 100%">
              <span>{{ warning }}</span>
            </v-alert>
          </v-list-item>
        </v-list>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>


<script>
export default {
  data() {
    return {};
  },
  props: {
    value: Boolean,
    info: Object,
  },
  mounted() {
  },
  computed: {
    openWarningDialog: {
      get() {
        return this.value;
      },
      set(value) {
        this.$emit("input", value);
      },
    },
  },
};
</script>