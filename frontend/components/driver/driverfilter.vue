<template>
  <v-dialog v-model="driverFilterDialog" width="35%">
    <v-card>
      <v-card-title class="background-primary text-white px-3 py-2">
        <span class="text-subtitle-1 text-uppercase">Driver Filters</span>
        <v-spacer />
        <v-btn small icon @click="driverFilterDialog = false">
          <v-icon class="text-white">mdi-close</v-icon>
        </v-btn>
      </v-card-title>
      <v-card-text class="pa-0">
        <v-form ref="driverFilterForm">
          <v-row no-gutters class="pt-4 px-4 background-light_primary">
            <v-col cols="12">
              <CommonCustomselect
                :itemsList="allProjects"
                label="Select Project"
                placeholder="Select Project"
                :returnObject="false"
                :value="driverFilter.project"
                :isMounted="driverFilterDialog"
                @selectionChanged="syncDriverFilter($event, 'project')"
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
                label="Select Duty Status"
                placeholder="Select Duty Status"
                :items="driverDutyStatus"
                item-text="name"
                item-value="value"
                multiple
                :value="driverFilter.status"
                @change="syncDriverFilter($event, 'status')"
                class="mb-4 background-white"
              ></v-select>
            </v-col>
            <v-col cols="12">
              <v-select
                hide-details
                outlined
                dense
                :menu-props="{ offsetY: true }"
                label="Select Status"
                placeholder="Select Status"
                :items="driverStatus"
                item-text="name"
                item-value="value"
                :value="driverFilter.is_active"
                @change="syncDriverFilter($event, 'is_active')"
                class="mb-4 background-white"
              ></v-select>
            </v-col>
          </v-row>
          <v-row no-gutters class="px-4 pt-4">
            <v-col cols="12" class="px-1 pb-1 mb-4 border-bottom-light_black">
              <span class="text-subtitle-1 font-weight-bold text-grey">
                Filter By Assignment
              </span>
            </v-col>
            <v-col cols="6">
              <v-select
                hide-details
                outlined
                dense
                :menu-props="{offsetY: true}"
                label="Vehicle Assigned"
                placeholder="Vehicle Assigned"
                :items="vehicleAssigned"
                item-text="name"
                item-value="value"
                :value="driverFilter.vehicle_assigned"
                @change="syncDriverFilter($event, 'vehicle_assigned')"
                class="mb-4 mr-2 background-white"
              >
              </v-select>
            </v-col>
            <v-col cols="6">
              <v-select
                hide-details
                outlined
                dense
                :menu-props="{offsetY: true}"
                label="Zone Assigned"
                placeholder="Zone Assigned"
                :items="zoneAssigned"
                item-text="name"
                item-value="value"
                :value="driverFilter.zone_assigned"
                @change="syncDriverFilter($event, 'zone_assigned')"
                class="mb-4 ml-2 background-white"
              >
              </v-select>
            </v-col>
          </v-row>
          <v-row no-gutters class="pb-4 px-4 background-white">
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
                  :value="driverFilter.ordering"
                  :menu-props="{ offsetY: true }"
                  @change="syncDriverFilter($event, 'ordering')"
              ></v-select>
            </v-col>
            <v-col cols="6" class="pl-2">
              <v-select
                  hide-details
                  outlined
                  dense
                  label="Sort by"
                  :items="sortBy"
                  :value="driverFilter.sorting"
                  :menu-props="{ offsetY: true }"
                  @change="syncDriverFilter($event, 'sorting')"
              ></v-select>
            </v-col>
          </v-row>
        </v-form>
      </v-card-text>
      <v-card-actions class="pa-4 background-light_grey">
        <v-spacer></v-spacer>
        <v-btn small depressed @click="driverFilterDialog = false">
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
      driverFilter: {},
      driverDutyStatus: [
        {
          name: "On Duty",
          value: "on_duty",
        },
        {
          name: "On Break",
          value: "break",
        },
        {
          name: "Off Duty",
          value: "off_duty",
        }
      ],
      driverStatus: [
        {
          name: "Active",
          value: "true",
        },
        {
          name: "Deactive",
          value: "false",
        },
      ],
      vehicleAssigned: [
        {
          name: "Assigned",
          value: "true",
        },
        {
          name: "Not Assigned",
          value: "false",
        },
      ],
      zoneAssigned: [
        {
          name: "Assigned",
          value: "true",
        },
        {
          name: "Not Assigned",
          value: "false",
        },
      ],
      orderBy: [
        {
          text: "Status",
          value: "status",
        },
        {
          text: "Driver Name",
          value: "user__first_name",
        }
      ],
      sortBy: [
        {
          text: "Ascending",
          value: "ascending",
        },
        {
          text: "Descending",
          value: "descending",
        },
      ],
    };
  },
  watch: {
    driverFilterDialog(value) {
      if (value) {
        let filters = localStorage.getItem("driverFilters");
        if (!filters) {
          filters = {};
        }
        if (typeof filters == typeof "string") {
          filters = JSON.parse(filters);
        }
        this.driverFilter = filters;
      }
    },
  },
  computed: {
    driverFilterDialog: {
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
    syncDriverFilter(value, key) {
      let filters = localStorage.getItem("driverFilters");
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
      this.driverFilter = filters;
      localStorage.setItem("driverFilters", JSON.stringify(filters));
    },
    applyFilters(reload) {
      this.$emit("driverFilterChanged");
      this.driverFilterDialog = false;
    },
    resetFilters(reload) {
      this.driverFilter = {};
      localStorage.removeItem("driverFilters");
      this.$emit("driverFilterChanged");
      if (this.$refs.driverFilterForm) {
        this.$refs.driverFilterForm.reset();
      }
    },
  },
};
</script>