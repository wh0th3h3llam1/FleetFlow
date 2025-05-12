<template>
  <v-dialog v-model="vehicleFilterDialog" width="35%">
    <v-card>
      <v-card-title class="background-primary text-white px-3 py-2">
        <span class="text-subtitle-1 text-uppercase"> Vehicle Filters </span>
        <v-spacer />
        <v-btn small icon @click="vehicleFilterDialog = false">
          <v-icon class="text-white">mdi-close</v-icon>
        </v-btn>
      </v-card-title>
      <v-card-text class="pa-0">
        <v-form ref="vehicleFilterForm">
          <v-row no-gutters class="pt-4 px-4 background-light_primary">
            <v-col cols="12">
              <CommonCustomselect
                :itemsList="allProjects"
                label="Select Project"
                :returnObject="false"
                :value="vehicleFilter.project"
                :isMounted="vehicleFilterDialog"
                @selectionChanged="syncVehicleFilter($event, 'project')"
                :dense="true"
                class="mb-4 background-white"
              />
            </v-col>
            <v-col cols="12">
              <v-select
                hide-details
                outlined
                dense
                :menu-props="{ offsetY: true }"
                label="Select Status"
                placeholder="Select Status"
                :items="statusTypes"
                item-text="name"
                item-value="value"
                :value="vehicleFilter.status"
                @change="syncVehicleFilter($event, 'status')"
                class="mb-4 background-white"
              ></v-select>
            </v-col>
            <v-col cols="12">
              <CommonCustomselect
                :itemsList="vehicleTags"
                item-text="tag"
                item-value="tag"
                label="Select Tag"
                :returnObject="false"
                :value="vehicleFilter.tags"
                :isMounted="vehicleFilterDialog"
                @selectionChanged="syncVehicleFilter($event, 'tags')"
                :dense="true"
                class="mb-4 background-white"
              />
            </v-col>
          </v-row>
          <v-row no-gutters class="py-4 px-4 background-white">
            <v-col cols="12" class="px-1 pb-1 mb-4 border-bottom-light_black">
              <span class="text-subtitle-1 font-weight-bold text-grey">
                Ordering & Sorting
              </span>
            </v-col>
            <v-col cols="6" class="pr-2">
              <v-select
                  hide-details
                  outlined
                  dense
                  label="Order by"
                  :items="orderBy"
                  :value="vehicleFilter.ordering"
                  :menu-props="{ offsetY: true }"
                  @change="syncVehicleFilter($event, 'ordering')"
              ></v-select>
            </v-col>
            <v-col cols="6" class="pl-2">
              <v-select
                  hide-details
                  outlined
                  dense
                  label="Sort by"
                  :items="sortBy"
                  :value="vehicleFilter.sorting"
                  :menu-props="{ offsetY: true }"
                  @change="syncVehicleFilter($event, 'sorting')"
              ></v-select>
            </v-col>
          </v-row>
        </v-form>
      </v-card-text>
      <v-card-actions class="pa-4 background-light_grey">
        <v-spacer></v-spacer>
        <v-btn small depressed @click="vehicleFilterDialog = false">
          Cancel
        </v-btn>
        <v-btn small depressed type="reset" @click="resetFilters(true)">
          Reset
        </v-btn>
        <v-btn small depressed color="primary" @click="applyFilters(true)">
          Apply
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  props: {
    value: Boolean,
  },
  data() {
    return {
      vehicleFilter: {},
      vehicleTags: [],
      statusTypes: [
        {
          name: "Active",
          value: "idle",
        },
        {
          name: "Deactivated",
          value: "deactivated",
        },
      ],
      orderBy: [
        {
          text: "Vehicle Plate Number",
          value: "vehicle_plate_no",
        },
        {
          text: "Status",
          value: "status",
        },
        {
          text: "Tonnage Capacity",
          value: "tonnage_capacity",
        },
        {
          text: "CBM Capacity",
          value: "cbm_capacity",
        }
      ],
      sortBy: [
        {
          text: "Ascending",
          value: "ascending",
        },
        {
          text: "Descending",
          value: "descending"
        },
      ],
    };
  },
  watch: {
    vehicleFilterDialog(value) {
      if (value) {
        let filters = localStorage.getItem("vehicleFilters");
        if (!filters) {
          filters = {};
        }
        if (typeof filters == typeof "string") {
          filters = JSON.parse(filters);
        }
        this.vehicleFilter = filters;
      }
    },
  },
  computed: {
    vehicleFilterDialog: {
      get() {
        return this.value;
      },
      set(value) {
        this.$emit("input", value);
      },
    },
    allProjects() {
      return this.$store.getters["project/PROJECT_LIST_FOR_DROPDOWN"];
    },
  },
  methods: {
    getVehicleTags() {
      this.$store.dispatch("vehicle/GET_TAG_LIST")
        .then((response) => {
          this.vehicleTags = response.filter(item => item.tag_type == "vehicle_tag")
        });
    },
    syncVehicleFilter(value, key) {
      let filters = localStorage.getItem("vehicleFilters");
      if (!filters) {
        filters = {};
      }
      if (typeof filters == typeof "string") {
        filters = JSON.parse(filters);
      }
      if (value !== null && value.length > 0) {
        filters[key] = value;
      } else {
        delete filters[key];
      }
      this.vehicleFilter = filters;
      localStorage.setItem("vehicleFilters", JSON.stringify(filters));
    },
    applyFilters(reload) {
      this.$emit("vehicleFilterChanged");
      this.vehicleFilterDialog = false;
    },
    resetFilters(reload) {
      this.vehicleFilter = {};
      localStorage.removeItem("vehicleFilters");
      this.$emit("vehicleFilterChanged");
      if (this.$refs.vehicleFilterForm) {
        this.$refs.vehicleFilterForm.reset();
      }
    },
  },
  mounted() {
    this.getVehicleTags();
  }
};
</script>