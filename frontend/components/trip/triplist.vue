<template>
  <div class="border-right-light_grey">
    <v-row no-gutters>
      <v-col
        id="tripListHeaderContainer"
        cols="12"
        class="background-light_grey px-4 pt-4"
      >
        <v-row no-gutters>
          <v-col cols="12" class="px-2 pt-2">
            <span class="text-h5 text-uppercase font-weight-bold text-grey">
              Trips
            </span>
          </v-col>
          <v-col cols="12" class="d-flex px-2 pt-2 pb-4">
            <v-text-field
              label="Search here.."
              prepend-inner-icon="mdi-magnify"
              hide-details="auto"
              outlined
              dense
              class="background-white"
              :value="tripFilter.search"
              @input="syncTripFilter($event, 'search')"
            ></v-text-field>
            <v-tooltip bottom>
              <template v-slot:activator="{ on, attrs }">
                <v-btn
                  small
                  fab
                  depressed
                  color="primary"
                  class="ml-1 rounded"
                  v-bind="attrs"
                  v-on="on"
                  @click="get_trip_list(true)"
                >
                  <v-icon small>mdi-refresh</v-icon>
                </v-btn>
              </template>
              <span>Refresh</span>
            </v-tooltip>

            <v-tooltip bottom>
              <template v-slot:activator="{ on, attrs }">
                <v-btn
                  small
                  fab
                  depressed
                  color="primary"
                  class="ml-1 rounded"
                  @click="openTripFilterDialog = true"
                  v-bind="attrs"
                  v-on="on"
                >
                  <v-icon small>mdi-filter</v-icon>
                </v-btn>
              </template>
              <span>Trip Filters</span>
            </v-tooltip>

            <v-tooltip bottom>
              <template v-slot:activator="{ on, attrs }">
                <div v-bind="attrs" v-on="on">
                  <v-menu
                    transition="slide-y-transition"
                    bottom
                    right
                    left
                    offset-y
                  >
                    <template v-slot:activator="{ on, attrs }">
                      <v-btn
                        small
                        fab
                        depressed
                        color="primary"
                        class="ml-1 rounded"
                        v-bind="attrs"
                        v-on="on"
                      >
                        <v-icon>mdi-plus</v-icon>
                      </v-btn>
                    </template>
                    <v-list dense style="width: 250px">
                      <v-list-item
                        link
                        class="tile"
                        @click="createTrip()"
                        v-if="userPermissions.trip && userPermissions.trip.add"
                      >
                        <v-list-item-title> Create Trip </v-list-item-title>
                      </v-list-item>
                      <v-list-item
                        link
                        class="tile"
                        @click="openBulkUploadDialog = true"
                      >
                        <v-list-item-title>
                          Temperature Sheet Bulk Upload
                        </v-list-item-title>
                      </v-list-item>
                      <v-list-item
                        link
                        class="tile"
                        @click="openLoadSheetDownloadDialog = true"
                      >
                        <v-list-item-title> Picking Sheet </v-list-item-title>
                      </v-list-item>
                    </v-list>
                  </v-menu>
                </div>
              </template>
              <span>Create Trip</span>
            </v-tooltip>
          </v-col>
          <v-col
            cols="12"
            class="px-2 pb-2"
            v-if="appliedFilters && appliedFilters.length !== 0"
          >
            <v-chip
              small
              close
              dark
              class="mr-1 mb-1 text-capitalize background-black"
              v-for="(filter, index) in appliedFilters"
              :key="index"
              @click:close="removeFilter(filter.key)"
            >
              {{ filter.name }}
            </v-chip>
          </v-col>
          <v-col cols="12" class="d-flex px-2 pb-4" v-if="loaderProgress">
            <v-scroll-x-transition mode="out-in">
              <v-progress-linear
                color="primary"
                indeterminate
                rounded
                height="6"
              ></v-progress-linear>
            </v-scroll-x-transition>
          </v-col>
        </v-row>
      </v-col>
      <v-col
        ref="tripParent"
        cols="12"
        class="px-4 pb-4 mt-4 overflow-y-auto"
        @scroll="scrollControlTrip"
        :style="{ height: listContainerHeight }"
      >
        <div v-for="(trip, index) in Trips" :key="index">
          <TripTripdetailcard
            @selectTrip="get_trip_details(trip.id)"
            :trip="trip"
          />
        </div>
      </v-col>
    </v-row>
    <TripTripfilter
      ref="tripFilterDialog"
      @tripFilterChanged="tripFilterChanged"
      v-model="openTripFilterDialog"
    />
    <TripTripbulkupload v-model="openBulkUploadDialog" />
    <TripTriploadsheet v-model="openLoadSheetDownloadDialog" />
  </div>
</template>

<script>
import { makeInstance, encryptLocal } from "~/assets/js/encryptLocal";

export default {
  data() {
    return {
      containerHeight: null,
      openTripFilterDialog: false,
      openBulkUploadDialog: false,
      openLoadSheetDownloadDialog: false,
      sortingType: null,
      selectedTrips: [],
      loaderProgress: false,
      tripFilter: {},
      userPermissions: encryptLocal.getItem("permissions"),
      listContainerHeight: `${window.innerHeight - 200}px`,
    };
  },
  computed: {
    Trips() {
      return this.$store.state.trip.Trips;
    },
    appliedFilters() {
      return Object.keys(this.tripFilter).map((filter) => {
        return {
          name: filter.replace(/\_/g, " "),
          key: filter,
        };
      });
    },
  },
  methods: {
    createTrip() {
      this.$router.push("/trip/add/");
    },
    syncTripFilter(value, key) {
      let filters = localStorage.getItem("tripFilters");
      if (!filters) {
        filters = {};
      }
      if (typeof filters == typeof "string") {
        filters = JSON.parse(filters);
      }
      if (value !== null && value.length > 3) {
        filters[key] = value;
      } else if (value == null || value.length == 0) {
        delete filters[key];
      }
      localStorage.setItem("tripFilters", JSON.stringify(filters));
      if (value.length > 3 || value.length == 0 || value == null) {
        this.tripFilterChanged();
      }
    },
    tripFilterChanged() {
      let filters = localStorage.getItem("tripFilters");
      if (!filters) {
        filters = {};
      }
      if (typeof filters == typeof "string") {
        filters = JSON.parse(filters);
      }
      this.tripFilter = filters;
      this.get_trip_list(true);
    },
    removeFilter(key) {
      let filters = localStorage.getItem("tripFilters");
      filters = JSON.parse(filters);

      if (key === "start_date" || key === "end_date") {
        delete filters.start_date;
        delete filters.end_date;
      } else {
        delete filters[key];
      }

      this.tripFilter = filters;
      localStorage.setItem("tripFilters", JSON.stringify(filters));
      this.get_trip_list(true);
    },
    scrollControlTrip() {
      let elem = this.$refs.tripParent;
      if (elem == null) {
        return false;
      } else if (
        Math.ceil(elem.offsetHeight + elem.scrollTop) == elem.scrollHeight
      ) {
        this.get_trip_list(false);
      }
    },
    get_trip_list(reload) {
      if (
        reload ||
        this.$store.state.trip.tripTotalCount != this.Trips.length
      ) {
        this.loaderProgress = true;
        this.$store
          .dispatch("trip/GET_ALL_TRIPS", reload)
          .then((result) => {
            this.loaderProgress = false;
            this.refreshHeight();
          })
          .catch((err) => {
            this.loaderProgress = false;
          });
      }
    },
    get_trip_details(id) {
      this.$emit("toggleChart");
      this.$store
        .dispatch("trip/GET_TRIP_DETAILS", id)
        .then((response) => {
          this.$emit(
            "showTripDetails",
            true,
            response.trip_route,
            response.locations,
            response.driver_location,
            id
          );
        })
        .catch((err) => {
          this.$store.commit("TOGGLE_LOADER", false);
        });
    },
    refreshHeight() {
      setTimeout(() => {
        let rowHeight = document.getElementById(
          "tripListHeaderContainer"
        ).offsetHeight;

        if (typeof rowHeight == typeof 1) {
          this.listContainerHeight = `${
            window.innerHeight - (rowHeight + 80)
          }px`;
        }
      }, 100);
    },
  },
  mounted() {
    let filters = localStorage.getItem("tripFilters");
    if (!filters) {
      filters = {};
    }
    if (typeof filters == typeof "string") {
      filters = JSON.parse(filters);
    }
    this.tripFilter = filters;
    this.get_trip_list(true);
  },
  beforeCreate() {
    if (encryptLocal == null) {
      makeInstance(localStorage.getItem("user"));
    }
  },
};
</script>

<style lang="scss">
@import "~/assets/scss/variables.scss";
.tile {
  color: white !important;
}
.tile:hover {
  background: map-get($colors-custom, "solid", "primary") !important ;
  color: white !important;
}
.tile:hover .v-list-item__title {
  color: white !important;
}
.tile:active {
  background: map-get($colors-custom, "solid", "primary") !important ;
}
</style>