<template>
  <v-dialog v-model="zoneFilterDialog" width="35%">
    <v-card>
      <v-card-title class="background-primary text-white px-3 py-2">
        <span class="text-subtitle-1 text-uppercase"> Zone Filters </span>
        <v-spacer />
        <v-btn small icon @click="zoneFilterDialog = false">
          <v-icon class="text-white">mdi-close</v-icon>
        </v-btn>
      </v-card-title>
      <v-card-text class="pa-0">
        <v-form ref="zoneFilterForm">
          <v-row no-gutters class="pt-4 px-4 background-light_primary">
            <v-col cols="12">
              <CommonCustomselect
                :itemsList="allProjects"
                label="Select Project"
                :returnObject="false"
                :value="zoneFilter.project"
                :isMounted="zoneFilterDialog"
                @selectionChanged="syncZoneFilter($event, 'project')"
                :dense="true"
                class="mb-4 background-white"
              />
            </v-col>
          </v-row>
          <v-row no-gutters class="pa-4">
              <v-col cols="12">
                <v-select
                    hide-details
                    outlined
                    dense
                    label="Sort by"
                    :items="sortBy"
                    :value="zoneFilter.ordering"
                    :menu-props="{ offsetY: true }"
                    @change="syncZoneFilter($event, 'ordering')"
                ></v-select>
            </v-col>
          </v-row>
        </v-form>
      </v-card-text>
      <v-card-actions class="pa-4 background-light_grey">
        <v-spacer></v-spacer>
        <v-btn small depressed @click="zoneFilterDialog = false">
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
      zoneFilter: {},
      sortBy: [
        {
          text: "Zone Name",
          value: "zone_name",
        },
        {
          text: "Zone Name (Descending)",
          value: "-zone_name",
        },
      ],
    };
  },
  watch: {
    zoneFilterDialog(value) {
      if (value) {
        let filters = localStorage.getItem("zoneFilters");
        if (!filters) {
          filters = {};
        }
        if (typeof filters == typeof "string") {
          filters = JSON.parse(filters);
        }
        this.zoneFilter = filters;
      }
    },
  },
  computed: {
    zoneFilterDialog: {
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
    syncZoneFilter(value, key) {
      let filters = localStorage.getItem("zoneFilters");
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
      this.zoneFilter = filters;
      localStorage.setItem("zoneFilters", JSON.stringify(filters));
    },
    applyFilters(reload) {
      this.$emit("zoneFilterChanged");
      this.zoneFilterDialog = false;
    },
    resetFilters(reload) {
      this.zoneFilter = {};
      localStorage.removeItem("zoneFilters");
      this.$emit("zoneFilterChanged");
      if (this.$refs.zoneFilterForm) {
        this.$refs.zoneFilterForm.reset();
      }
    },
  }
};
</script>