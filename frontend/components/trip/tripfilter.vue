<template>
  <v-dialog v-model="tripFilterDialog" width="35%">
    <v-card>
      <v-card-title class="background-primary text-white px-3 py-2">
        <span class="text-subtitle-1 text-uppercase"> Trip Filters </span>
        <v-spacer />
        <v-btn small icon @click="tripFilterDialog = false">
          <v-icon class="text-white">mdi-close</v-icon>
        </v-btn>
      </v-card-title>
      <v-card-text class="pa-0">
        <v-form ref="tripFilterForm">
          <v-row no-gutters class="pt-4 px-4 background-light_primary">
            <v-col cols="12">
              <CommonCustomselect
                :itemsList="allProjects"
                label="Select Project"
                :returnObject="false"
                :value="tripFilter.project"
                :isMounted="tripFilterDialog"
                @selectionChanged="syncTripFilter($event, 'project')"
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
                multiple
                :value="tripFilter.status"
                @change="syncTripFilter($event, 'status')"
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
                    :value="tripFilter.start_date"
                    @input="syncTripFilter($event, 'start_date')"
                    v-bind="attrs"
                    v-on="on"
                  ></v-text-field>
                </template>
                <v-date-picker
                  :value="tripFilter.start_date"
                  @click:date="
                    $refs.startDateMenu.save(startDate),
                      syncTripFilter($event, 'start_date')
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
                    :value="tripFilter.end_date"
                    @input="syncTripFilter($event, 'end_date')"
                  ></v-text-field>
                </template>
                <v-date-picker
                  :value="tripFilter.end_date"
                  @click:date="
                    $refs.endDateMenu.save(endDate),
                      syncTripFilter($event, 'end_date')
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
            <v-col cols="6" class="pr-2">
              <v-select
                  hide-details
                  outlined
                  dense
                  label="Order by"
                  :items="orderBy"
                  :value="tripFilter.ordering"
                  :menu-props="{ offsetY: true }"
                  @change="syncTripFilter($event, 'ordering')"
              ></v-select>
            </v-col>
            <v-col cols="6" class="pl-2">
              <v-select
                  hide-details
                  outlined
                  dense
                  label="Sort by"
                  :items="sortBy"
                  :value="tripFilter.sorting"
                  :menu-props="{ offsetY: true }"
                  @change="syncTripFilter($event, 'sorting')"
              ></v-select>
            </v-col>
          </v-row>
        </v-form>
      </v-card-text>
      <v-card-actions class="pa-4 background-light_grey">
        <v-spacer></v-spacer>
        <v-btn small depressed @click="tripFilterDialog = false">
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
      startDate: null,
      startDateMenu: false,
      endDate: null,
      endDateMenu: false,
      tripFilter: {},
      statusTypes: [
        {
          name: "Scheduled",
          value: "scheduled",
        },
        {
          name: "Active",
          value: "active",
        },
        {
          name: "Paused",
          value: "paused",
        },
        {
          name: "Completed",
          value: "completed",
        },
      ],
      orderBy: [
        {
          text: "Status",
          value: "status",
        },
        {
          text: "Reference Number",
          value: "reference_number",
        },
        {
          text: "Trip Date",
          value: "trip_date",
        },
        {
          text: "Driver Name",
          value: "driver",
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
    tripFilterDialog(value) {
      if (value) {
        let filters = localStorage.getItem("tripFilters");
        if (!filters) {
          filters = {};
        }
        if (typeof filters == typeof "string") {
          filters = JSON.parse(filters);
        }
        this.tripFilter = filters;
      }
    },
  },
  computed: {
    tripFilterDialog: {
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
    syncTripFilter(value, key) {
      let filters = localStorage.getItem("tripFilters");
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
      this.tripFilter = filters;
      localStorage.setItem("tripFilters", JSON.stringify(filters));
    },
    applyFilters(reload) {
      this.$emit("tripFilterChanged");
      this.tripFilterDialog = false;
    },
    resetFilters(reload) {
      this.tripFilter = {};
      localStorage.removeItem("tripFilters");
      this.$emit("tripFilterChanged");
      if (this.$refs.tripFilterForm) {
        this.$refs.tripFilterForm.reset();
      }
      this.$parent.get_trip_list(reload);
    },
  },
};
</script>