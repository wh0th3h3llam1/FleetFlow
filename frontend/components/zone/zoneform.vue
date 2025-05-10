<template>
  <v-dialog
    v-model="zoneFormDialog"
    fullscreen
    hide-overlay
    transition="dialog-bottom-transition"
    persistent
  >
    <v-card class="pa-4">
      <v-form
        v-if="zoneFormDialog"
        v-model="isValid"
        ref="userForm"
        id="userForm"
      >
        <v-card-title>
          <span
            class="
              text-lg-subtitle-1 text-xl-h6 text-uppercase
              font-weight-black
              primary--text
            "
          >
            {{ formType }} Zone
          </span>
          <v-spacer />
          <v-row class="d-flex justify-end pr-12">
            <v-col cols="12" md="2">
              <v-select
                :items="allProjects"
                :rules="[
                  (v) => (v != null && v.length > 0) || 'Project is required',
                ]"
                outlined
                hide-details="auto"
                dense
                class="background-white"
                label="Project*"
                :value="zoneDetails.project"
                :disabled="formType == 'edit'"
                @change="
                  syncData($event, 'project'), getSelectedProjectsZone($event)
                "
                :menu-props="{ offsetY: true }"
              ></v-select>
            </v-col>
            <v-col cols="12" md="2">
              <v-text-field
                :rules="[(v) => !!v || 'Zone name is required']"
                outlined
                hide-details="auto"
                dense
                class="background-white"
                label="Zone Name*"
                :error-messages="error.zone_name"
                :value="zoneDetails.zone_name"
                @input="syncData($event, 'zone_name')"
              ></v-text-field>
            </v-col>
            <v-col cols="12" md="3">
              <v-text-field
                :rules="[
                  (v) => !!v || 'Description is required',
                  (v) =>
                    (!!v && v.length < 100) || 'Can not be more than 100 words',
                ]"
                outlined
                hide-details="auto"
                dense
                class="background-white"
                label="Description*"
                :error-messages="error.zone_desc"
                :value="zoneDetails.zone_desc"
                @input="syncData($event, 'zone_desc')"
              ></v-text-field>
            </v-col>
            <v-col cols="12" md="1">
              <v-btn
                type="submit"
                :disabled="!isValid"
                class="primary text-uppercase mr-3"
                @click.prevent="submitZoneForm()"
              >
                <span>submit</span>
              </v-btn>
            </v-col>
          </v-row>

          <v-btn
            depressed
            text
            small
            icon
            class="primary-text"
            @click="closeDialog()"
          >
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        <v-card-text class="cf-zone-map">
          <CommonGmap
            v-show="zoneDetails.project"
            mapWidth="100%"
            mapHeight="89vh"
            :showZones="true"
            :isDrawable="true"
            ref="ZoneMap"
          />
          <v-card id="info-box" class="info-card pa-2" v-if="formType == 'edit' ">
            <span class="text-body-h4 font-weight-bold pr-2">Zone Name :</span><span id="zone_name">{{zoneDetails.zone_name}}</span>
          </v-card>
        </v-card-text>
      </v-form>
    </v-card>
  </v-dialog>
</template>

<style scoped>
.info-card {
  position: absolute;
  bottom: 60px;
  right: 26px;
  padding: 0;
  margin: 0;
  min-width: 30px !important;
  border-radius: 0;
}
</style>

<script>
import authHeader from "~/store/authHeader";

export default {
  props: {
    value: Boolean,
    formType: {
      type: String,
      default: "add",
    },
  },
  data() {
    return {
      error: {},
      nonFieldError: [],
      geofence: {},
      isValid: false,
    };
  },
  computed: {
    zoneDetails: {
      get() {
        return this.$store.state.zone.zonedetail;
      },
      set(value) {
        this.$store.commit("zone/SET_ZONE_DETAILS", value);
      },
    },
    allProjects() {
      return this.$store.getters["project/PROJECT_LIST_FOR_DROPDOWN"];
    },
    zoneFormDialog: {
      get() {
        return this.value;
      },
      set(value) {
        this.$emit("input", value);
      },
    },
  },
  methods: {
    getgeofenceData(data) {
      this.geofence = data;
    },
    closeDialog() {
      this.zoneFormDialog = false;
      this.clear();
    },
    getSelectedProjectsZone(value) {
      this.$axios
        .get("/api/v1/zones/display_zones/", {
          headers: { ...authHeader(), loader: true },
          params: { project_id: value },
        })
        .then((result) => {
          this.$refs.ZoneMap.clearGeoJson();
          this.$refs.ZoneMap.clearMarker();
          this.$refs.ZoneMap.initMap();
          this.$refs.ZoneMap.loadRoutes(result.data.zones);
        })
        .catch((err) => {
          if (message in err.response.data) {
            this.$notifier.showMessage({
              content: err.response.data.message,
              color: "error",
            });
          } else {
            this.$notifier.showMessage({
              content: "Something went wrong",
              color: "error",
            });
          }
        });
    },
    setEditZoneDetails(path, remaining_zones, coordinates) {
      let interval = setInterval(() => {
        if (this.$refs.ZoneMap) {
          clearInterval(interval);
          this.$refs.ZoneMap.clearGeoJson();
          this.$refs.ZoneMap.clearMarker();
          this.$refs.ZoneMap.initMap();
          this.$refs.ZoneMap.loadRoutes(remaining_zones);
          this.$refs.ZoneMap.setEditablePolygon(path, coordinates);
        }
      }, 500);
    },
    submitZoneForm() {
      let getdata = this.$refs.ZoneMap.convertToGeoJSON();
      if (!getdata) {
        this.$notifier.showMessage({
          content: "Please draw your Geofence",
          color: "error",
        });
        return false;
      }
      let newObject = { ...this.zoneDetails };
      newObject.geofence = getdata.geometry;
      if (this.formType == "add") {
        let newObject = { ...this.zoneDetails };
        newObject.geofence = getdata.geometry;
        this.$store
          .dispatch("zone/ADD_ZONE", newObject)
          .then((result) => {
            this.closeDialog();
            this.$notifier.showMessage({
              content: "Zone Added successfully",
              color: "success",
            });
            this.$store.commit("zone/SET_GEOJSON_DATA", null);
          })
          .catch((err) => {
            if ("non_field_errors" in err) {
              this.nonFieldError = err.non_field_errors;
            }
            this.error = err;
          });
      } else {
        this.$store
          .dispatch("zone/UPDATE_ZONE_DETAILS", newObject)
          .then((result) => {
            this.$notifier.showMessage({
              content: "Zone Updated successfully",
              color: "success",
            });
            this.$store.commit("zone/SET_GEOJSON_DATA", null);
            this.closeDialog();
          })
          .catch((err) => {
            if ("non_field_errors" in err) {
              this.nonFieldError = err.non_field_errors;
            }
            this.error = err;
          });
      }
    },

    syncData(input_value, key) {
      if (this.error[key]) {
        this.error[key] = null;
        delete this.error[key];
      }
      this.$store.commit("zone/SYNC_ZONE_FORM_DETAILS", {
        key: key,
        value: input_value,
      });
      this.$forceUpdate();
    },
    clear() {
      this.zoneDetails = {
        geofence: {},
        id: null,
        project: null,
        zone_desc: null,
        zone_name: null,
      };
      this.$store.commit("zone/SET_GEOJSON_DATA", null);
    },
  },
  mounted(){
    this.$store.dispatch('project/GET_ALL_PROJECT_LIST');
  }
};
</script>