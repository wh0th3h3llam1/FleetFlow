<template>
  <div>
    <v-tooltip top>
      <template v-slot:activator="{ on, attrs }">
        <v-btn
          class="mt-2 mr-2 grey text-white"
          depressed
          small
          v-bind="attrs"
          v-on="on"
          v-show="params.data.status.toLowerCase() !== 'failed'"
          :disabled="
            params.data.status.toLowerCase() === 'in_progress' ||
            params.data.status.toLowerCase() === 'pending'
          "
          @click="goTo"
        >
          <v-icon small class="ma-0"> mdi-eye </v-icon>
        </v-btn>
      </template>
      <span>Plan View</span>
    </v-tooltip>

    <v-tooltip top>
      <template v-slot:activator="{ on, attrs }">
        <v-btn
          class="mt-2 mr-2 grey text-white"
          depressed
          small
          v-bind="attrs"
          v-on="on"
          v-show="params.data.status.toLowerCase() === 'failed'"
          @click="retryPlan(params.data.id)"
        >
          <v-icon small class="ma-0"> mdi-reload </v-icon>
        </v-btn>
      </template>
      <span>Retry Plan</span>
    </v-tooltip>

    <v-tooltip top>
      <template v-slot:activator="{ on, attrs }">
        <v-btn
          class="mt-2 mr-2 pa-0 error text-white"
          depressed
          v-bind="attrs"
          v-on="on"
          @click="deletePlans"
        >
          <v-icon small class="ma-0"> mdi-delete </v-icon>
        </v-btn>
      </template>
      <span>Delete Details</span>
    </v-tooltip>

    <v-tooltip top>
      <template v-slot:activator="{ on, attrs }">
        <v-btn
          class="mt-2 info text-white"
          depressed
          small
          v-bind="attrs"
          v-on="on"
          @click="showingInformation"
        >
          <v-icon class="ma-0"> mdi-information-variant </v-icon>
        </v-btn>
      </template>
      <span>information</span>
    </v-tooltip>
  </div>
</template>

<script>
export default {
  data() {
    return {
      openDriverDetails: false,
    };
  },
  methods: {
    showingInformation() {
      // this.params.context.parentComponent.openFailedReasonDialog(
      //   this.params.data
      // );

      this.params.context.parentComponent.openPlanInformationDialog();
      this.$store.dispatch(
        "trip_planning/GET_PLAN_INFORMATION",
        this.params.data.id
      );
    },
    deletePlans() {
      this.params.context.parentComponent.deleteRecentPlans(
        this.params.data.id
      );
    },
    goTo() {
      this.$store.commit(
        "trip_planning/SET_SELECTED_PLAN_ID",
        this.params.data.id
      );
      this.$router.push({
        name: "planning_trips",
        path: "/planning_trips",
      });
    },
    retryPlan(id) {
      this.$store
        .dispatch("trip_creation/RETRY_PLAN_TRIP", id)
        .then((response) => {
          this.$router.push({
            name: "plan_trips",
            path: "/plan_trips",
          });

          this.$notifier.showMessage({
            content: response.message,
            color: "success",
          });
        });
    },
  },
};
</script>