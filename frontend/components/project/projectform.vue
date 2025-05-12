<template>
  <v-dialog persistent v-model="projectFormDialog" fullscreen scrollable>
    <v-card class="pa-4">
      <v-card-title>
        <span
          class="
            text-lg-subtitle-1 text-xl-h6 text-uppercase
            font-weight-black
            primary--text
            mb-4
          "
          >{{ formType }} Project</span
        >
        <v-spacer />
        <v-btn
          depressed
          text
          small
          icon
          class="primary-text mt-n4"
          @click="closeDialog()"
        >
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>
      <v-card-text class="pt-4" @scroll="reSetColumn()">
        <v-form ref="projectForm" id="projectForm" v-model="isValid">
          <v-alert v-if="nonFieldError.length" dense type="error">
            <v-list
              class="pa-0"
              dense
              style="background: inherit !important"
              v-for="(error, i) in nonFieldError"
              :key="i"
            >
              <v-list-item dense style="min-height: 20px !important">
                <span>{{ i }} .</span><span>{{ error }}</span>
              </v-list-item>
            </v-list>
          </v-alert>
          <v-row class="pb-2">
            <v-col cols="6" lg="4">
              <v-text-field
                outlined
                hide-details="auto"
                class="background-white"
                label="Project Name*"
                :rules="[(v) => !!v || 'Project Name is required']"
                :error-messages="error.project_name"
                :value="projectFormDetails.project_name"
                @input="syncData($event, 'project_name')"
              ></v-text-field>
            </v-col>
            <v-col cols="6" lg="4">
              <v-text-field
                outlined
                hide-details="auto"
                class="background-white"
                label="Project ID*"
                :rules="[(v) => !!v || 'Project ID is required']"
                :error-messages="error.project_id"
                :value="projectFormDetails.project_id"
                @input="syncData($event, 'project_id')"
              ></v-text-field>
            </v-col>
            <v-col cols="6" lg="4">
              <v-select
                outlined
                hide-details="auto"
                class="background-white"
                label="Select Template*"
                ref="select"
                :menu-props="{ offsetY: true }"
                name="planning_template"
                :items="templateList"
                :rules="[(v) => !!v || 'Template is required']"
                :error-messages="error.planning_template"
                :value="projectFormDetails.planning_template"
                @change="syncData($event, 'planning_template')"
              ></v-select>
            </v-col>
            <v-col cols="12">
              <v-text-field
                outlined
                ref="projectFormAddress"
                hide-details="auto"
                placeholder="Enter Address *"
                class="background-white"
                :rules="[(v) => !!v || 'Base Address is required']"
                :error-messages="error.base_address"
                :value="projectFormDetails.base_address"
              ></v-text-field>
            </v-col>
            <v-col cols="6">
              <v-text-field
                outlined
                hide-details="auto"
                class="background-white"
                label="Latitude*"
                type="number"
                step="0.0000001"
                v-model="latitude"
                :rules="[(v) => !!v || 'Latitude is required']"
                :error-messages="error.base_coordinates"
                :value="projectFormDetails.base_coordinates.latitude"
                @input="syncData($event, 'base_coordinates', 'latitude')"
              ></v-text-field>
            </v-col>
            <v-col cols="6">
              <v-text-field
                outlined
                hide-details="auto"
                class="background-white"
                label="Longitude*"
                type="number"
                step="0.0000001"
                v-model="longitude"
                :rules="[(v) => !!v || 'Latitude is required']"
                :error-messages="error.base_coordinates"
                :value="projectFormDetails.base_coordinates.longitude"
                @input="syncData($event, 'base_coordinates', 'longitude')"
              ></v-text-field>
            </v-col>
            <v-col cols="6">
              <v-switch
                dense
                hide-details="auto"
                class="mt-0 pt-0"
                label="Update Customer Location"
                :error-messages="error.update_customer_location"
                :input-value="projectFormDetails.update_customer_location"
                @change="syncData($event, 'update_customer_location')"
              ></v-switch>
            </v-col>
          </v-row>
          <v-row class="pt-2">
            <v-col cols="12">
              <span class="text-body-1">Order Notification</span>
            </v-col>
            <v-col cols="6">
              <v-switch
                dense
                hide-details="auto"
                class="mt-0 pt-0"
                label="Order Creation"
                :true-value="true"
                :false-value="false"
                :error-messages="error.order_creation_notification"
                :input-value="projectFormDetails.order_creation_notification"
                @change="syncData($event, 'order_creation_notification')"
              ></v-switch>
            </v-col>
            <v-col cols="12" class="d-flex justify-center">
              <span class="text-h6">Set Project's Serviceable area</span>
            </v-col>
            <v-col cols="12" v-if="projectFormDialog" class="cf-zone-map">
              <CommonGmap
                mapWidth="100%"
                mapHeight="500px"
                :dialog-status="projectFormDialog"
                ref="projectFormMap"
                :isDrawable="true"
                :clusterMarkers="false"
              />
            </v-col>
          </v-row>
        </v-form>
      </v-card-text>
      <v-card-actions class="d-flex justify-center pb-4">
        <v-btn
          type="submit"
          :disabled="!isValid"
          class="primary text-uppercase mr-3"
          @click.prevent="submitProjectForm()"
        >
          <span>Submit</span>
        </v-btn>
        <v-btn
          type="reset"
          v-if="formType == 'add'"
          class="primary text-uppercase"
          @click="clear()"
        >
          <span>Reset</span>
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  props: {
    value: Boolean,
    formType: {
      type: String,
      default: "add",
    },
  },
  mounted() {

    this.$store.dispatch("trip_planing_templates/GET_ALL_TEMPLATE_LIST");

    const interval = setInterval(() => {
      if (
        this.$refs.projectFormAddress &&
        window.google &&
        window.google.maps
      ) {
        clearInterval(interval);
        let input = this.$refs.projectFormAddress.$refs.input;

        this.autocomplete = new window.google.maps.places.Autocomplete(input);

        this.autocomplete.addListener("place_changed", () => {
          let place = this.autocomplete.getPlace();
          let lat = place.geometry.location.lat();
          let lon = place.geometry.location.lng();

          setTimeout(() => {
            this.syncData(
              place.name + ", " + place.formatted_address,
              "base_address"
            );
            this.longitude = lon;
            this.latitude = lat;
          }, 100);
        });
      }
    }, 100);
  },
  data() {
    return {
      error: [],
      google: null,
      nonFieldError: [],
      isValid: false,
    };
  },
  computed: {
    templateList() {
      return this.$store.getters[
        "trip_planing_templates/GET_TEMPLATE_LIST_FOR_DROPDOWN"
      ];
    },
    projectFormDialog: {
      get() {
        return this.value;
      },
      set(value) {
        this.$emit("input", value);
      },
    },
    projectFormDetails: {
      get() {
        return this.$store.state.project.projectForm;
      },
      set(value) {
        this.$store.commit("project/SET_PROJECT_DETAILS", value);
      },
    },
    latitude: {
      get() {
        if (
          this.projectFormDetails &&
          this.projectFormDetails.base_coordinates &&
          this.projectFormDetails.base_coordinates.latitude
        ) {
          return this.projectFormDetails.base_coordinates.latitude;
        } else {
          return null;
        }
      },
      set(value) {
        this.syncData(value, "base_coordinates", "latitude");
      },
    },
    longitude: {
      get() {
        if (
          this.projectFormDetails &&
          this.projectFormDetails.base_coordinates &&
          this.projectFormDetails.base_coordinates.longitude
        ) {
          return this.projectFormDetails.base_coordinates.longitude;
        } else {
          return null;
        }
      },
      set(value) {
        this.syncData(value, "base_coordinates", "longitude");
      },
    },
  },
  methods: {
    reSetColumn() {
      this.$refs.select.blur();
    },
    closeDialog() {
      this.projectFormDialog = false;
      this.clear();
    },
    syncData(input_value, key, subKey) {
      if (this.error[key]) {
        this.error[key] = null;
        delete this.error[key];
      }
      this.$store.commit("project/SYNC_PROJECT_FORM_DETAILS", {
        key: key,
        value: input_value,
        subKey: subKey,
      });
    },
    loadServisableArea(coordinates) {
      let interval = setInterval(() => {
        if (this.$refs.projectFormMap) {
          clearInterval(interval);
          this.$refs.projectFormMap.initMap();
          this.$refs.projectFormMap.loadEditableMultiPolygon(coordinates);
        }
      }, 100);
    },
    submitProjectForm() {
      let getdata = this.$refs.projectFormMap.getZoneData();
      if (getdata) {
        this.syncData(getdata, "serviceable_area");
      } else {
        if (this.formType == "edit") {
          this.$notifier.showMessage({
            content: "Please draw your Geofence",
            color: "error",
          });
          return false;
        }
      }

      if (this.formType == "add") {
        this.$store
          .dispatch("project/ADD_PROJECT", this.projectFormDetails)
          .then((result) => {
            this.closeDialog();
            this.$notifier.showMessage({
              content: "Project Added successfully",
              color: "success",
            });
            this.$store.dispatch("project/GET_ALL_PROJECT_LIST")
          })
          .catch((err) => {
            if ("non_field_errors" in err) {
              this.nonFieldError = err.non_field_errors;
            }
            this.error = err;
          });
      } else {
        this.$store
          .dispatch("project/UPDATE_PROJECT_DETAILS", this.projectFormDetails)
          .then((result) => {
            this.closeDialog();
            this.$notifier.showMessage({
              content: "Project Updated successfully",
              color: "success",
            });
          })
          .catch((err) => {
            if ("non_field_errors" in err) {
              this.nonFieldError = err.non_field_errors;
            }
            this.error = err;
          });
      }
    },
    clear() {
      this.projectFormDetails = {
        project_name: null,
        base_address: null,
        project_id: null,
        base_coordinates: {
          latitude: null,
          longitude: null,
        },
      };
      this.$refs.projectForm.reset();
    },
  },
};
</script>
