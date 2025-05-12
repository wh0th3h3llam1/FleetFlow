<template>
  <v-dialog v-model="tripPlaningTemplateForm" scrollable width="700">
    <v-card>
      <v-card-title class="background-primary text-white px-3 py-2">
        <span
          class="text-subtitle-1 text-uppercase"
          v-if="!readOnly && !editMode"
        >
          Create Template
        </span>
        <span
          class="text-subtitle-1 text-uppercase"
          v-if="!readOnly && editMode"
        >
          Edit Template
        </span>
        <span
          class="text-subtitle-1 text-uppercase"
          v-if="readOnly && !editMode"
        >
          View Template
        </span>
        <v-spacer></v-spacer>
        <v-btn depressed color="white" icon small @click="closeForm">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>
      <v-card-text class="pa-0">
        <v-form ref="templateForm" v-model="isTemplateFormValid">
          <v-row no-gutters class="px-4 pt-4 background-light_primary">
            <v-col class="pb-4" cols="12">
              <v-text-field
                label="Template Name *"
                class="background-white"
                dense
                :rules="[(v) => !!v || 'Template Name is required']"
                hide-details="auto"
                outlined
                :error-messages="error.template_name"
                :readonly="readOnly"
                :value="templateDetails.template_name"
                @input="syncData($event, 'template_name')"
              >
              </v-text-field>
            </v-col>
            <v-col class="pb-4 pr-2" cols="6" md="4" lg="4" xl="4">
              <v-text-field
                label="Fill Ratio"
                hide-details="auto"
                type="number"
                class="background-white"
                dense
                min="1"
                max="100"
                prepend-inner-icon=""
                outlined
                :value="templateDetails.fill_ratio"
                @input="syncData($event, 'fill_ratio')"
              >
              </v-text-field>
            </v-col>
            <v-col class="pb-4 px-2" cols="6" md="4" lg="4" xl="4"> </v-col>
            <v-col class="pb-4 pl-2" cols="6" md="4" lg="4" xl="4">
              <v-select
                outlined
                dense
                :readonly="readOnly"
                hide-details="auto"
                class="background-white"
                label="Optimization Option"
                :items="configurationOptions"
                item-text="text"
                item-value="value"
                :value="templateDetails.configuration"
                @change="syncData($event, 'configuration')"
                :menu-props="{ offsetY: true }"
              ></v-select>
            </v-col>
          </v-row>
          <v-row no-gutters class="px-4 pt-4">
            <v-col cols="8">
              <v-row no-gutters>
                <v-col class="pb-4 pr-2" cols="6" md="6" lg="6" xl="6">
                  <v-text-field
                    label="Loading Start Time *"
                    hide-details="auto"
                    type="time"
                    outlined
                    dense
                    :rules="[(v) => !!v || 'Loading start time is required']"
                    :readonly="readOnly"
                    :error-messages="error.loading_start_time"
                    :value="templateDetails.loading_start_time"
                    @input="syncData($event, 'loading_start_time')"
                  >
                  </v-text-field>
                </v-col>
                <v-col class="pb-4 pl-2" cols="6" md="6" lg="6" xl="6">
                  <v-text-field
                    label="Loading End Time *"
                    hide-details="auto"
                    type="time"
                    outlined
                    dense
                    :rules="[(v) => !!v || 'Loading end time is required']"
                    :readonly="readOnly"
                    :error-messages="error.loading_end_time"
                    :value="templateDetails.loading_end_time"
                    @input="syncData($event, 'loading_end_time')"
                  >
                  </v-text-field>
                </v-col>
                <v-col class="pb-4 pr-2" cols="6" md="6" lg="6" xl="6">
                  <v-text-field
                    label="Offloading Start Time *"
                    hide-details="auto"
                    type="time"
                    outlined
                    :rules="[(v) => !!v || 'OffLoading start time is required']"
                    dense
                    :readonly="readOnly"
                    :error-messages="error.offloading_start_time"
                    :value="templateDetails.offloading_start_time"
                    @input="syncData($event, 'offloading_start_time')"
                  >
                  </v-text-field>
                </v-col>
                <v-col class="pb-4 pl-2" cols="6" md="6" lg="6" xl="6">
                  <v-text-field
                    label="Offloading End Time *"
                    hide-details="auto"
                    type="time"
                    :rules="[(v) => !!v || 'OffLoading end time is required']"
                    outlined
                    dense
                    :error-messages="error.offloading_end_time"
                    :readonly="readOnly"
                    :value="templateDetails.offloading_end_time"
                    @input="syncData($event, 'offloading_end_time')"
                  >
                  </v-text-field>
                </v-col>
                <v-col class="pr-2" cols="6" md="6" lg="6" xl="6">
                  <v-text-field
                    label="Loading Time(In Minutes) *"
                    hide-details="auto"
                    type="number"
                    min="0"
                    :rules="[(v) => !!v || 'Loading time is required']"
                    outlined
                    dense
                    :error-messages="error.loading_time"
                    :readonly="readOnly"
                    :value="templateDetails.loading_time"
                    @input="syncData($event, 'loading_time')"
                  >
                  </v-text-field>
                </v-col>
                <v-col class="pl-2" cols="6" md="6" lg="6" xl="6">
                  <v-text-field
                    label="Offloading Time(In Minutes) *"
                    hide-details="auto"
                    type="number"
                    min="0"
                    outlined
                    dense
                    :rules="[(v) => !!v || 'Offloading time is required']"
                    :error-messages="error.offloading_time"
                    :readonly="readOnly"
                    :value="templateDetails.offloading_time"
                    @input="syncData($event, 'offloading_time')"
                  >
                  </v-text-field>
                </v-col>
              </v-row>
            </v-col>
            <v-col cols="4" class="d-flex px-4">
              <v-row no-gutters class="d-flex align-center">
                <v-col class="px-3 d-flex align-center justify-start" cols="12">
                  <v-switch
                    label="Round Trip"
                    color="primary"
                    class="ma-0 pa-0"
                    inset
                    dense
                    :readonly="readOnly"
                    :input-value="templateDetails.round_trip"
                    hide-details
                    @change="syncData($event, 'round_trip')"
                  ></v-switch>
                </v-col>
                <v-col class="px-3 d-flex align-center justify-start" cols="12">
                  <v-switch
                    label="Zone Constraint"
                    color="primary"
                    class="mb-1 mt-2 pa-0"
                    inset
                    dense
                    :readonly="readOnly"
                    :input-value="templateDetails.zone_constraint"
                    hide-details
                    @change="syncData($event, 'zone_constraint')"
                  ></v-switch>
                </v-col>
                <v-col class="px-3 d-flex align-center justify-start" cols="12">
                  <v-switch
                    label="Tag Validations"
                    color="primary"
                    class="mb-1 mt-2 pa-0"
                    inset
                    dense
                    :readonly="readOnly"
                    :input-value="templateDetails.tag_validations"
                    hide-details
                    @change="syncData($event, 'tag_validations')"
                  ></v-switch>
                </v-col>
                <v-col class="px-3 d-flex align-center justify-start" cols="12">
                  <v-switch
                    label="Disable time windows"
                    color="primary"
                    class="mt-1 mb-2 pa-0"
                    inset
                    dense
                    :readonly="readOnly"
                    :input-value="templateDetails.disable_time_windows"
                    hide-details
                    @change="syncData($event, 'disable_time_windows')"
                  ></v-switch>
                </v-col>
                <v-col class="px-3 d-flex align-center justify-start" cols="12">
                  <v-switch
                    label="Traffic Jams"
                    color="primary"
                    class="mt-1 mb-2 pa-0"
                    inset
                    dense
                    :readonly="readOnly"
                    :input-value="templateDetails.trafic_jams"
                    hide-details
                    @change="syncData($event, 'trafic_jams')"
                  ></v-switch>
                </v-col>
                <v-col class="px-3 d-flex align-center justify-start" cols="12">
                  <v-switch
                    label="Toll Roads"
                    color="primary"
                    class="ma-0 pa-0"
                    inset
                    dense
                    :readonly="readOnly"
                    :input-value="templateDetails.toll_roads"
                    hide-details
                    @change="syncData($event, 'toll_roads')"
                  ></v-switch>
                </v-col>
              </v-row>
            </v-col>
          </v-row>
          <v-row no-gutters> </v-row>
        </v-form>
      </v-card-text>
      <v-card-actions
        class="mt-4 d-flex justify-end pa-4 background-light_grey"
      >
        <v-btn
          small
          class="primary elevation-0"
          :disabled="!isTemplateFormValid || readOnly"
          @click="submitTemplate"
        >
          <span v-if="editMode">Save</span>
          <span v-else>Submit</span>
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  props: {
    value: Boolean,
    editMode: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      nonFieldError: [],
      error: {
        loading_start_time: [],
        loading_end_time: [],
        offloading_start_time: [],
        offloading_end_time: [],
      },
      isTemplateFormValid: false,
    };
  },
  computed: {
    readOnly() {
      return this.$store.state.trip_planing_templates.readOnly;
    },
    templateDetails: {
      get() {
        return this.$store.state.trip_planing_templates.templateDetails;
      },
      set(value) {
        this.$store.commit(
          "trip_planing_templates/SET_TEMPLATE_FORM_DATA",
          value
        );
      },
    },
    tripPlaningTemplateForm: {
      get() {
        return this.value;
      },
      set(value) {
        this.$emit("input", value);
      },
    },
    configurationOptions() {
      return [
        { text: "Optimize Distance", value: "optimize_distance" },
        { text: "Visual Grouping", value: "visual_grouping" },
        { text: "Optimize Transporters", value: "optimize_transporters" },
        {
          text: "Optimize Locality Grouping",
          value: "optimize_locality_grouping",
        },
        { text: "Optimize Time", value: "optimize_time" },
        { text: "Optimize Cars Then Time", value: "optimize_cars_then_time" },
        { text: "Optimize Visual Grouping", value: "optimize_visual_grouping" },
        {
          text: "Optimize Cars Then Locality Grouping",
          value: "optimize_cars_then_locality_grouping",
        },
        { text: "Optimize Money", value: "optimize_money" },
      ];
    },
  },
  methods: {
    clearForm() {
      this.templateDetails = {
        configuration: "",
        loading_end_time: null,
        loading_start_time: null,
        loading_time: null,
        offloading_end_time: null,
        offloading_start_time: null,
        offloading_time: null,
        planing_time: null,
        // result_ttl: null,
        template_name: null,
        round_trip: false,
        // disable_compatibility: false,
        toll_roads: true,
        trafic_jams: true,
        zone_constraint: false,
        tag_validations: false,
        disable_time_windows: false,
        fill_ratio: "100",
      };
      this.$refs.templateForm.reset();
      this.templateDetails = {
        fill_ratio: "100",
      };
    },
    closeForm() {
      this.clearForm();
      this.tripPlaningTemplateForm = false;
    },
    syncData(value, key) {
      if (this.error[key]) {
        this.error[key] = null;
        delete this.error[key];
      }
      this.$store.commit("trip_planing_templates/SYNC_TEMPLATE_FORM_DATA", {
        key: key,
        value: value,
      });
    },
    submitTemplate() {
      let action = "trip_planing_templates/ADD_PLANNING_TEMPLATES";
      if (this.editMode) {
        action = "trip_planing_templates/EDIT_PLANNING_TEMPLATES";
      }
      this.$store
        .dispatch(action, this.templateDetails)
        .then((res) => {
          this.$parent.getAllTemplates();
          this.closeForm();
        })
        .catch((err) => {
          if ("non_field_errors" in err) {
            this.nonFieldError = err.non_field_errors;
          }
          this.error = err;
        });
    },
  },
};
</script>

<style>
</style>
