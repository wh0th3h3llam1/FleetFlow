<template>
  <div>
    <v-tooltip top>
      <template v-slot:activator="{ on, attrs }">
        <v-btn
          class="mt-2 info text-white"
          depressed
          small
          v-bind="attrs"
          v-on="on"
          @click="openWarningInfoDialog"
          v-show="
            (params.data.warnings && params.data.warnings.length != 0) ||
            (params.data.zone_details &&  params.data.zone_details.warnings &&
              params.data.zone_details.warnings.length != 0)
          "
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
    return {};
  },
  methods: {
    openWarningInfoDialog() {
      this.params.context.parentComponent.openWarningDialog(
        this.params.data
      );
    },
  },
};
</script>