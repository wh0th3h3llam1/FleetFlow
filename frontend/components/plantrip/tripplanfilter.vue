<template>
  <v-dialog v-model="tripplanFilterDialog" width="35%">
    <v-card>
      <v-card-title class="background-primary text-white px-3 py-2">
        <span class="text-subtitle-1 text-uppercase">Trip Plan Filters</span>
        <v-spacer />
        <v-btn small icon @click="tripplanFilterDialog = false">
          <v-icon class="text-white">mdi-close</v-icon>
        </v-btn>
      </v-card-title>
      <v-card-text class="pa-0">
        <v-form ref="tripplanFilterForm">
          <v-row no-gutters class="pt-4 px-4 background-light_primary">
        <v-col cols="12">
              <CommonCustomselect
                :itemsList="allProjects"
                label="Select Project"
                placeholder="Select Project"
                :returnObject="false"
                :value="tripplanFilter.project"
                :isMounted="tripplanFilterDialog"
                @selectionChanged="syncTripPlanFilter($event, 'project')"
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
                label=" Status"
                placeholder="Select Plan Status"
                :items="planStatus"
                item-text="name"
                item-value="value"
                multiple
                :value="tripplanFilter.status"
                @change="syncTripPlanFilter($event, 'status')"
                class="mb-4 background-white"
              ></v-select>
            </v-col>
          </v-row>
          <v-row no-gutters class="pb-4 pt-2 px-4 background-white">
            <v-col cols="12" class="px-1 pb-1 mb-4 border-bottom-light_black">
              <span class="text-subtitle-1 font-weight-bold text-grey">
                Filter By Date Range
              </span>
            </v-col>
            <v-col
              cols="12"
              lg="6"
              xl="6"
              :class="`pb-4 ${$vuetify.breakpoint.lgAndUp ? 'pr-2' : null}`"
            >
              <v-menu
                ref="startDateMenu"
                v-model="startDateMenu"
                :close-on-content-click="false"
                :return-value.sync="startDate"
                transition="scale-transition"
                offset-y
                min-width="auto"
              >
                <template v-slot:activator="{ on, attrs }">
                  <v-text-field
                    label="Start Date"
                    prepend-inner-icon="mdi-calendar"
                    hide-details
                    outlined
                    readonly
                    dense
                    :value="tripplanFilter.from_date"
                    @input="syncTripPlanFilter($event, 'from_date')"
                    v-bind="attrs"
                    v-on="on"
                  ></v-text-field>
                </template>
                <v-date-picker
                  :value="tripplanFilter.from_date"
                  @click:date="
                    $refs.startDateMenu.save(startDate),
                      syncTripPlanFilter($event, 'from_date')
                  "
                  no-title
                  scrollable
                >
                </v-date-picker>
              </v-menu>
            </v-col>
            <v-col
              cols="12"
              lg="6"
              xl="6"
              :class="`pb-4 ${$vuetify.breakpoint.lgAndUp ? 'pl-2' : null}`"
            >
              <v-menu
                ref="endDateMenu"
                v-model="endDateMenu"
                :close-on-content-click="false"
                :return-value.sync="endDate"
                transition="scale-transition"
                offset-y
                min-width="auto"
              >
                <template v-slot:activator="{ on, attrs }">
                  <v-text-field
                    label="End Date"
                    prepend-inner-icon="mdi-calendar"
                    outlined
                    hide-details
                    readonly
                    dense
                    v-bind="attrs"
                    v-on="on"
                    :value="tripplanFilter.to_date"
                    @input="syncTripPlanFilter($event, 'to_date')"
                  ></v-text-field>
                </template>
                <v-date-picker
                  :value="tripplanFilter.to_date"
                  @click:date="
                    $refs.endDateMenu.save(endDate),
                      syncTripPlanFilter($event, 'to_date')
                  "
                  no-title
                  scrollable
                >
                </v-date-picker>
              </v-menu>
            </v-col>
          </v-row>
          <v-row no-gutters class="pb-4 px-4 background-white">
            <v-col cols="12" class="px-1 pb-1 mb-4 border-bottom-light_black">
              <span class="text-subtitle-1 font-weight-bold text-grey">
                Ordering & Sorting
              </span>
            </v-col>
            <v-col cols="6" class="pb-4 pr-2">
              <v-select
                  hide-details
                  outlined
                  dense
                  label="Order by"
                  :items="orderBy"
                  :value="tripplanFilter.ordering"
                  :menu-props="{ offsetY: true }"
                  @change="syncTripPlanFilter($event, 'ordering')"
              ></v-select>
            </v-col>
            <v-col cols="6" class="pb-4 pl-2">
              <v-select
                  hide-details
                  outlined
                  dense
                  label="Sort by"
                  :items="sortBy"
                  :value="tripplanFilter.sorting"
                  :menu-props="{ offsetY: true }"
                  @change="syncTripPlanFilter($event, 'sorting')"
              ></v-select>
            </v-col>
          </v-row>
        </v-form>
      </v-card-text>
      <v-card-actions class="pa-4 background-light_grey">
        <v-spacer></v-spacer>
        <v-btn small depressed @click="tripplanFilterDialog = false">
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
      tripplanFilter: {},
      startDate: null,
      startDateMenu: false,
      endDate: null,
      endDateMenu: false,
      planStatus: [
        {
          name: "Pending",
          value: "PENDING",
        },
        {
          name: "In Progress",
          value: "IN_PROGRESS",
        },
        {
          name: "Post Processing",
          value: "POST_PROCESSING",
        },
        {
          name: "Completed",
          value: "COMPLETED",
        },
        {
          name: "Failed",
          value: "FAILED",
        },
        {
          name: "Cancelled",
          value: "CANCELED",
        },
      ],
      orderBy: [
        {
          text: "Plan Name",
          value: "plan_name",
        },
        {
          text: "Progress",
          value: "progress",
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
    tripplanFilterDialog(value) {
      if (value) {
        let filters = localStorage.getItem("tripplanFilters");
        if (!filters) {
          filters = {};
        }
        if (typeof filters == typeof "string") {
          filters = JSON.parse(filters);
        }
        this.tripplanFilter = filters;
      }
    },
  },
  computed: {
    tripplanFilterDialog: {
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
    syncTripPlanFilter(value, key) {
      let filters = localStorage.getItem("tripplanFilters");
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
      this.tripplanFilter = filters;
      localStorage.setItem("tripplanFilters", JSON.stringify(filters));
    },
    applyFilters(reload) {
      this.$emit("tripplanFilterChanged");
      this.tripplanFilterDialog = false;
    },
    resetFilters(reload) {
      this.tripplanFilter = {};
      localStorage.removeItem("tripplanFilters");
      if (this.$refs.tripplanFilterForm) {
        this.$refs.tripplanFilterForm.reset();
      }
      this.$emit("tripplanFilterChanged");
    },
  },
};
</script>