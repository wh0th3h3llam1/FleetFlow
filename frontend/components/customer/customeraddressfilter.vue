<template>
  <v-dialog v-model="customerFilterDialog" width="35%">
    <v-card>
      <v-card-title class="background-primary text-white px-3 py-2">
        <span class="text-subtitle-1 text-uppercase"
          >Customer Address Filters
        </span>
        <v-spacer />
        <v-btn small icon @click="customerFilterDialog = false">
          <v-icon class="text-white">mdi-close</v-icon>
        </v-btn>
      </v-card-title>
      <v-card-text class="pa-0">
        <v-form ref="customerFilterForm">
          <v-row no-gutters class="pt-4 px-4 background-light_primary">
            <v-col cols="12">
              <CommonCustomselect
                :itemsList="allProjects"
                label="Select Project"
                :returnObject="false"
                :value="customerFilter.project"
                :isMounted="customerFilterDialog"
                @selectionChanged="syncCustomerFilter($event, 'project')"
                :dense="true"
                class="mb-4 background-white"
              />
            </v-col>
            <v-col cols="12">
              <CommonCustomselect
                :itemsList="customerTags"
                item-text="tag"
                item-value="tag"
                label="Select Tag"
                :returnObject="false"
                :value="customerFilter.tags"
                :isMounted="customerFilterDialog"
                @selectionChanged="syncCustomerFilter($event, 'tags')"
                :dense="true"
                class="mb-4 background-white"
              />
            </v-col>
            <v-col cols="12">
              <v-select
                hide-details
                outlined
                dense
                label="Customer Type"
                :items="customerType"
                :value="customerFilter.customer_type"
                :menu-props="{ offsetY: true }"
                @change="syncCustomerFilter($event, 'customer_type')"
                class="mb-4 background-white"
              ></v-select>
            </v-col>
          </v-row>
          <v-row no-gutters class="px-4 pt-4">
            <v-col cols="12" class="px-1 pb-1 mb-4 border-bottom-light_black">
              <span class="text-subtitle-1 font-weight-bold text-grey">
                Filter By Time Slots
              </span>
            </v-col>
            <v-col
              cols="12"
              lg="6"
              xl="6"
              :class="`pb-4 ${$vuetify.breakpoint.lgAndUp ? 'pr-2' : null}`"
            >
              <v-menu
                ref="fromTimeMenu"
                v-model="fromTimeMenu"
                :close-on-content-click="false"
                :nudge-right="40"
                transition="scale-transition"
                :return-value.sync="customerFilter.from_time"
                offset-y
                max-width="290px"
                min-width="290px"
              >
                <template v-slot:activator="{ on, attrs }">
                  <v-text-field
                    label="From Time"
                    type="time"
                    outlined
                    dense
                    readonly
                    class="background-white"
                    hide-details="auto"
                    prepend-inner-icon="mdi-clock-time-four-outline"
                    :value="customerFilter.from_time"
                    v-bind="attrs"
                    v-on="on"
                  ></v-text-field>
                </template>
                <v-time-picker
                  format="24hr"
                  :value="customerFilter.from_time"
                  full-width
                  @change="syncCustomerFilter($event, 'from_time')"
                ></v-time-picker>
              </v-menu>
            </v-col>
            <v-col
              cols="12"
              lg="6"
              xl="6"
              :class="`pb-4 ${$vuetify.breakpoint.lgAndUp ? 'pl-2' : null}`"
            >
              <v-menu
                ref="toTimeMenu"
                v-model="toTimeMenu"
                :close-on-content-click="false"
                :nudge-right="40"
                transition="scale-transition"
                :return-value.sync="customerFilter.to_time"
                offset-y
                max-width="290px"
                min-width="290px"
              >
                <template v-slot:activator="{ on, attrs }">
                  <v-text-field
                    label="To Time"
                    placeholder="To Time"
                    type="time"
                    outlined
                    dense
                    readonly
                    class="background-white"
                    hide-details="auto"
                    prepend-inner-icon="mdi-clock-time-four-outline"
                    :value="customerFilter.to_time"
                    v-bind="attrs"
                    v-on="on"
                  ></v-text-field>
                </template>
                <v-time-picker
                  format="24hr"
                  dense
                  :value="customerFilter.to_time"
                  full-width
                  @change="syncCustomerFilter($event, 'to_time')"
                ></v-time-picker>
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
                  label="Order By"
                  :items="orderBy"
                  :value="customerFilter.ordering"
                  :menu-props="{ offsetY: true }"
                  @change="syncCustomerFilter($event, 'ordering')"
              ></v-select>
            </v-col>
            <v-col cols="6" class="pl-2">
              <v-select
                  hide-details
                  outlined
                  dense
                  label="Sort by"
                  :items="sortBy"
                  :value="customerFilter.sorting"
                  :menu-props="{ offsetY: true }"
                  @change="syncCustomerFilter($event, 'sorting')"
                  class="mb-4 background-white"
              ></v-select>
            </v-col>
          </v-row>
        </v-form>
      </v-card-text>
      <v-card-actions class="pa-4 background-light_grey">
        <v-spacer></v-spacer>
        <v-btn small depressed @click="customerFilterDialog = false">
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
      fromTimeMenu: false,
      toTimeMenu: false,
      customerFilter: {},
      customerTags: [],
      orderBy: [
        {
          text: "Customer Code",
          value: "customer_code",
        },
        {
          text: "Customer Name",
          value: "customer_name",
        },
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
      customerType: [
        {
          text: "B2B",
          value: "B2B",
        },
        {
          text: "B2C",
          value: "B2C",
        },
      ],
    };
  },
  watch: {
    customerFilterDialog(value) {
      if (value) {
        let filters = localStorage.getItem("customerFilters");
        if (!filters) {
          filters = {};
        }
        if (typeof filters == typeof "string") {
          filters = JSON.parse(filters);
        }
        this.customerFilter = filters;
      }
    }
  },
  computed: {
    customerFilterDialog: {
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
    getCustomerTags() {
      this.$store.dispatch("customer/customerAddress/GET_TAG_LIST")
        .then((response) => {
          this.customerTags = response
        });
    },
    syncCustomerFilter(value, key) {
      let filters = localStorage.getItem("customerFilters");
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
      if (key == "from_time") {
        this.fromTimeMenu = false;
      }
      if (key == "to_time") {
        this.toTimeMenu = false;
      }
      this.$nextTick(() => {
        this.customerFilter = filters;
      });
      localStorage.setItem("customerFilters", JSON.stringify(filters));
      this.$forceUpdate();
    },
    applyFilters(reload) {
      this.$emit("customerFilterChanged");
      this.customerFilterDialog = false;
    },
    resetFilters(reload) {
      this.customerFilter = {};
      localStorage.removeItem("customerFilters");
      if (this.$refs.customerFilterForm) {
        this.$refs.customerFilterForm.reset();
      }
      this.$emit("customerFilterChanged");
    },
  },
  mounted() {
    this.getCustomerTags();
  }
};
</script>