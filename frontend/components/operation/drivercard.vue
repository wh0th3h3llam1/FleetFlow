<template>
  <div
    @click="$emit('selectDriver')"
    class="
      mb-4
      border-x-light_grey
      border-y-light_grey
      full-width
      background-white
      rounded-lg
    "
    :class="
      selectedDriver != null && selectedDriver.id == driver.id
        ? 'selected-card'
        : null
    "
  >
    <div class="pa-2 background-light_grey rounded-t-lg">
      <v-row dense>
        <v-col cols="6">
          <span class="text-body-2 font-weight-bold">
            {{ driver.driver_name }}
          </span>
        </v-col>
        <v-col cols="6" class="d-flex justify-end">
          <div>
            <span class="caption text-capitalize">
              {{ driver.status }}
            </span>
            <v-avatar
              :class="getDriverStatusColor(driver.status)"
              size="16"
              class="ml-1"
            ></v-avatar>
          </div>
        </v-col>
      </v-row>
    </div>
    <div class="pa-2">
      <v-row no-gutters>
        <v-col cols="6" class="text-caption"> {{ driver.username }} </v-col>
        <v-col cols="6" class="text-caption d-flex justify-end">
          <b>{{ driver.contact_number }}</b>
        </v-col>
      </v-row>
      <v-row no-gutters v-if="driver && driver.project_name">
        <v-col cols="6" class="text-caption"> Project </v-col>
        <v-col cols="6" class="d-flex justify-end text-caption">
          <b>{{ driver.project_name }}</b>
        </v-col>
      </v-row>
      <v-row no-gutters v-if="driver && driver.zone_name">
        <v-col cols="6" class="text-caption"> Zone </v-col>
        <v-col cols="6" class="d-flex justify-end text-caption text-justify">
          <b>{{ driver.zone_name }}</b>
        </v-col>
      </v-row>
      <v-row no-gutters v-if="driver && driver.vehicle">
        <v-col cols="6" class="text-caption"> Vehicle </v-col>
        <v-col cols="6" class="d-flex justify-end text-caption">
          <b>{{ driver.vehicle }}</b>
        </v-col>
      </v-row>
      <v-row no-gutters class="pt-1" v-if="showChatButton">
        <v-col cols="12" class="d-flex justify-end">
          <v-btn
            x-small
            depressed
            color="primary"
            @click.stop.prevent="$emit('showChat')"
          >
            <span class="text-caption">Chat&nbsp;</span>
          </v-btn>
        </v-col>
      </v-row>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    driver: {
      required: true,
    },
    selectedDriver: {
      required: false,
    },
    showChatButton: {
      required: false,
      default: false,
    },
  },
  methods: {
    getDriverStatusColor(status) {
      switch (status) {
        case "Off Duty":
          return "grey";
        case "On Duty":
          return "pgreen";
        case "Break":
          return "orange";
      }
    },
  },
};
</script>

<style>
</style>