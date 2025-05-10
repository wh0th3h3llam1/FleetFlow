<template>
  <v-dialog v-model="itemFilterDialog" width="35%">
    <v-card>
      <v-card-title class="background-primary text-white px-3 py-2">
        <span class="text-subtitle-1 text-uppercase">Item Filters</span>
        <v-spacer />
        <v-btn small icon @click="itemFilterDialog = false">
          <v-icon class="text-white">mdi-close</v-icon>
        </v-btn>
      </v-card-title>
      <v-card-text class="pa-0">
        <v-form ref="itemFilterForm">
          <v-row no-gutters class="pt-4 px-4 background-light_primary">
            <v-col cols="12">
              <v-select
                hide-details
                outlined
                dense
                :menu-props="{ offsetY: true }"
                label="Select Storage Type"
                placeholder="Select Storage Type"
                :items="storageTypes"
                item-text="name"
                item-value="value"
                multiple
                :value="itemFilter.status"
                @change="syncItemFilter($event, 'storage_type')"
                class="mb-4 background-white"
              ></v-select>
            </v-col>
            <v-col cols="12">
              <v-select
                hide-details
                outlined
                dense
                :menu-props="{ offsetY: true }"
                label="Select Unit"
                placeholder="Select Unit"
                :items="unitOptions"
                item-text="name"
                item-value="value"
                multiple
                :value="itemFilter.status"
                @change="syncItemFilter($event, 'unit')"
                class="mb-4 background-white"
              ></v-select>
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
                  label="Order By"
                  :items="orderBy"
                  :value="itemFilter.ordering"
                  :menu-props="{ offsetY: true }"
                  @change="syncItemFilter($event, 'ordering')"
              ></v-select>
            </v-col>
            <v-col cols="6" class="pl-2">
              <v-select
                  hide-details
                  outlined
                  dense
                  label="Sort By"
                  :items="sortBy"
                  :value="itemFilter.sorting"
                  :menu-props="{ offsetY: true }"
                  @change="syncItemFilter($event, 'sorting')"
              ></v-select>
            </v-col>
          </v-row>
        </v-form>
      </v-card-text>
      <v-card-actions class="pa-4 background-light_grey">
        <v-spacer></v-spacer>
        <v-btn small depressed @click="itemFilterDialog = false">
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
      itemFilter: {},
      storageTypes: [
        {
          name: "Frozen",
          value: "Frozen",
        },
        {
          name: "Chilled",
          value: "Chilled",
        },
        {
          name: "Dry",
          value: "Dry",
        },
      ],
      unitOptions: [
        {
          name: "Case",
          value: "case",
        },
        {
          name: "K.G.",
          value: "kg",
        },
        {
          name: "Each",
          value: "each",
        },
      ],
      orderBy: [
        {
          text: "Item Number",
          value: "item_no",
        },
        {
          text: "Storage Type",
          value: "storage_type",
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
    };
  },
  watch: {
    itemFilterDialog(value) {
      if (value) {
        let filters = localStorage.getItem("itemFilters");
        if (!filters) {
          filters = {};
        }
        if (typeof filters == typeof "string") {
          filters = JSON.parse(filters);
        }
        this.itemFilter = filters;
      }
    },
  },
  computed: {
    itemFilterDialog: {
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
    allTags() {
      return this.$store.getters["vehicle/GET_TAG_LIST"]
    },
  },
  methods: {
    syncItemFilter(value, key) {
      let filters = localStorage.getItem("itemFilters");
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
      this.itemFilter = filters;
      localStorage.setItem("itemFilters", JSON.stringify(filters));
    },
    applyFilters(reload) {
      this.$emit("itemFilterChanged");
      this.itemFilterDialog = false;
    },
    resetFilters(reload) {
      this.itemFilter = {};
      localStorage.removeItem("itemFilters");
      this.$emit("itemFilterChanged");
      if (this.$refs.itemFilterForm) {
        this.$refs.itemFilterForm.reset();
      }
    },
  },
};
</script>