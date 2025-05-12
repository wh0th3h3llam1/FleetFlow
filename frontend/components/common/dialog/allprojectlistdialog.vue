<template>
  <v-dialog v-model="openAllProjectListDialog" scrollable max-width="500px">
    <v-card>
      <v-card-title class="d-flex justify-center primary text-white">
        <span class="text-body-1">Select Projects</span>
        <span class="white--text">
          <v-icon
            color="white"
            style="position: absolute; right: 10px; top: 15px;"
            @click="closeDialog()">
            mdi-close
          </v-icon>
        </span>
      </v-card-title>
      <v-card-text class="pa-0" style="height: 400px">
        <v-row no-gutters>
          <v-col cols="12" class="px-4 pt-4 d-flex justify-center">
            <v-alert border="left" colored-border type="info" >
              If you don't select any projects, All projects will be selected by
              default!
            </v-alert>
          </v-col>
          <v-col cols="12" class="pa-4 d-flex justify-center">
            <multiselect
              id="allProjects"
              class="cf-multipe-select"
              v-model="projects"
              :options="allProjects"
              :multiple="true"
              placeholder="Select Project"
              track-by="text"
              :limit="1"
              :limitText="(count) => `+ ${count}`"
              label="text"
              group-values="projects"
              group-label="selectAll"
              :group-select="true"
              :close-on-select="false"
              :showLabels="false"
              tag-position="bottom"
              :max-height="200"
            >
            </multiselect>
          </v-col>
        </v-row>
      </v-card-text>
      <v-card-actions class="d-flex justify-end">
        <v-btn class="primary" @click="downloadData">
          <span>Download</span>
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import Multiselect from "vue-multiselect";

export default {
  props: {
    value: {
      type: Boolean,
      required: true,
    },
    parent: {
      type: String,
      required: true,
    },
  },
  components: {
    Multiselect,
  },
  data() {
    return {
      projects: [],
    };
  },
  watch: {
    openAllProjectListDialog(value) {
      if (value) {
        this.$store.dispatch("project/GET_ALL_PROJECT_LIST");
      }
    },
  },
  computed: {
    openAllProjectListDialog: {
      get() {
        return this.value;
      },
      set(value) {
        this.$emit("input", value);
      },
    },
    allProjects() {
      return [
        {
          selectAll: "Select All Projects",
          projects: this.$store.getters["project/PROJECT_LIST_FOR_DROPDOWN"],
        },
      ];
    },
  },
  methods: {
    downloadData() {
      let projectArray = this.projects.map((project) => project.value);
      if (this.parent == "zones") {
        this.$parent.downloadAllZones(projectArray);
      }
      if(this.parent == 'customers'){
        this.$parent.downloadAllCustomers(projectArray);
      }
      if(this.parent == 'vehicles'){
        this.$parent.downloadAllVehicles(projectArray);
      }
      if(this.parent == 'drivers'){
        this.$parent.downloadAllDrivers(projectArray);
      }
    },
    closeDialog() {
      this.openAllProjectListDialog = false;
    },
  },
  mounted() {},
};
</script>
