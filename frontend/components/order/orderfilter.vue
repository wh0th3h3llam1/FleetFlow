<template>
  <v-dialog
    v-model="orderFilterDialog"
    width="35%"
    @keydown.enter="applyFilters(true)"
  >
    <v-card>
      <v-card-title class="background-primary text-white px-3 py-2">
        <span class="text-subtitle-1 text-uppercase"> Order Filters </span>
        <v-spacer />
        <v-btn small icon @click="orderFilterDialog = false">
          <v-icon class="text-white">mdi-close</v-icon>
        </v-btn>
      </v-card-title>
      <v-card-text class="pa-0">
        <v-form ref="orderFilterForm">
          <v-row no-gutters class="pt-4 px-4 background-light_primary">
            <v-col cols="12">
              <CommonCustomselect
                :itemsList="orderType"
                label="Select Status"
                :isMounted="orderFilterDialog"
                itemText="name"
                itemValue="value"
                :dense="true"
                :value="orderFilter.status"
                class="mb-4 background-white"
                @selectionChanged="syncOrderFilter($event, 'status')"
                :returnObject="false"
              />
            </v-col>
            <v-col
              cols="12"
              lg="6"
              :class="`mb-4 ${$vuetify.breakpoint.lgAndUp ? 'pr-2' : null}`"
            >
              <v-select
                hide-details
                outlined
                dense
                label="Select Payment Type"
                :items="paymentType"
                item-text="title"
                item-value="value"
                class="background-white"
                :value="orderFilter.payment_type"
                @change="syncOrderFilter($event, 'payment_type')"
                :menu-props="{ offsetY: true }"
              ></v-select>
            </v-col>
            <v-col
              cols="12"
              lg="6"
              :class="`mb-4 ${$vuetify.breakpoint.lgAndUp ? 'pl-2' : null}`"
            >
              <v-select
                multiple
                hide-details
                outlined
                dense
                label="Select Project"
                :items="allProjects"
                class="background-white"
                :value="orderFilter.project"
                @change="syncOrderFilter($event, 'project')"
                :menu-props="{ offsetY: true }"
              >
                <template v-slot:selection="{ item, index }">
                  <span v-if="index === 0">{{ item.text }} &nbsp;</span>
                  <span v-if="index === 1" class="grey--text text-caption">
                    (+{{ orderFilter.project.length - 1 }} others)
                  </span>
                </template>
              </v-select>
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
                    :value="orderFilter.from_date"
                    @input="syncOrderFilter($event, 'from_date')"
                    v-bind="attrs"
                    v-on="on"
                  ></v-text-field>
                </template>
                <v-date-picker
                  :value="orderFilter.from_date"
                  @click:date="
                    $refs.startDateMenu.save(startDate),
                      syncOrderFilter($event, 'from_date')
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
                    :value="orderFilter.to_date"
                    @input="syncOrderFilter($event, 'to_date')"
                  ></v-text-field>
                </template>
                <v-date-picker
                  :value="orderFilter.to_date"
                  @click:date="
                    $refs.endDateMenu.save(endDate),
                      syncOrderFilter($event, 'to_date')
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
                  :value="orderFilter.ordering"
                  :menu-props="{ offsetY: true }"
                  @change="syncOrderFilter($event, 'ordering')"
              ></v-select>
            </v-col>
            <v-col cols="6" class="pl-2">
              <v-select
                  hide-details
                  outlined
                  dense
                  label="Sort by"
                  :items="sortBy"
                  :value="orderFilter.sorting"
                  :menu-props="{ offsetY: true }"
                  @change="syncOrderFilter($event, 'sorting')"
              ></v-select>
            </v-col>
          </v-row>
        </v-form>
      </v-card-text>
      <v-card-actions class="pa-4 background-light_grey">
        <v-spacer></v-spacer>
        <v-btn small depressed @click="orderFilterDialog = false">
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
    filters: Object,
  },
  data() {
    return {
      startDate: null,
      startDateMenu: false,
      endDate: null,
      endDateMenu: false,
      orderFilter: {},
      orderBy: [
        {
          text: "Status",
          value: "status",
        },
        {
          text: "SO Number",
          value: "reference_number",
        },
        {
          text: "Customer Name",
          value: "customer_name",
        },
        {
          text: "Order Date",
          value: "execution_date",
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
      paymentType: [
        {
          title: "Pre-paid",
          value: "prepaid",
        },
        {
          title: "COD",
          value: "cod",
        },
      ],
      orderType: [
        {
          name: "Unassigned",
          value: "unassigned",
        },
        {
          name: "Assigned",
          value: "assigned",
        },
        {
          name: "Shipped",
          value: "pickedup",
        },
        {
          name: "Partially Delivered",
          value: "partially_delivered",
        },
        {
          name: "Delivered",
          value: "successful",
        },
        {
          name: "Returned",
          value: "failed",
        },
        {
          name: "Cancelled",
          value: "cancelled",
        },
      ],
    };
  },
  watch: {
    orderFilterDialog(value) {
      if (value) {
        this.$store.dispatch("project/GET_ALL_PROJECT_LIST");
        let filters = localStorage.getItem("orderFilters");
        if (!filters) {
          filters = {};
        }
        if (typeof filters == typeof "string") {
          filters = JSON.parse(filters);
        }
        this.orderFilter = filters;
      }
    },
  },
  computed: {
    orderFilterDialog: {
      get() {
        return this.value;
      },
      set(value) {
        this.$emit("input", value);
      },
    },
    allProjects() {
      return this.$store.getters["project/PROJECT_LIST_FOR_FILTER"];
    },
  },
  methods: {
    syncOrderFilter(value, key) {
      let filters = localStorage.getItem("orderFilters");
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
      this.orderFilter = filters;
      localStorage.setItem("orderFilters", JSON.stringify(filters));
    },
    applyFilters(reload) {
      this.$emit("filterChanged");
      this.orderFilterDialog = false;
    },
    resetFilters(reload) {
      this.orderFilter = {};
      localStorage.removeItem("orderFilters");
      this.$emit("filterChanged");
      this.$parent.get_order_list(reload);
    },
  },
  mounted() {
    this.$store.dispatch("project/GET_ALL_PROJECT_LIST");
  },
};
</script>