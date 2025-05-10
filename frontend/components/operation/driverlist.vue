<template>
  <div class="border-right-light_grey">
    <v-row no-gutters>
      <v-col cols="12" class="background-light_grey px-4 pt-4">
        <v-row no-gutters>
          <v-col cols="12" class="px-2 pt-2">
            <span class="text-h5 text-uppercase font-weight-bold text-grey">
              Operations
            </span>
          </v-col>
          <v-col cols="12" class="d-flex px-2 pt-2 pb-4">
            <v-text-field
              class="background-white"
              placeholder="Search here..."
              prepend-inner-icon="mdi-magnify"
              v-model="searchString"
              hide-details
              outlined
              dense
              clearable
            ></v-text-field>
          </v-col>
          <v-col cols="12" class="d-flex px-2 pb-4">
            <v-select
              ref="operationProjectFilter"
              class="background-white"
              placeholder="Select Project.."
              :items="projectList"
              v-model="selectedProjects"
              hide-details
              multiple
              outlined
              dense
              :menu-props="{ offsetX: true }"
            >
              <template v-slot:selection="{ item, index }">
                <span v-if="index === 0">{{ item.text }}</span>
                <span
                  v-if="index === 1 && $refs.operationProjectFilter"
                  class="grey--text text-caption"
                >
                  (+{{ selectedProjects.length - 1 }} others)
                </span>
              </template>
              <template v-slot:append-item>
                <v-list-item
                  class="
                    background-light_grey
                    px-1
                    position-sticky
                    d-flex
                    justify-end
                    stick-bottom
                  "
                >
                  <v-btn
                    small
                    depressed
                    color="primary"
                    @click="applyProjectFilter(true)"
                  >
                    Apply
                  </v-btn>
                </v-list-item>
              </template>
            </v-select>
          </v-col>

          <v-col cols="12" class="d-flex px-2 pb-4" v-if="showDriverLoader">
            <v-scroll-x-transition mode="out-in">
              <v-progress-linear
                color="primary"
                indeterminate
                rounded
                height="6"
              ></v-progress-linear>
            </v-scroll-x-transition>
          </v-col>

          <v-col cols="12">
            <v-tabs
              :show-arrows="true"
              fixed-tabs
              slider-color="primary"
              background-color="light_grey"
              class="px-2"
              active-class="primary-text"
              v-model="activeTab"
            >
              <v-tab small class="background-light_grey">
                <span>Working</span>
                <span>&nbsp;({{ onlineDrivers.length }})</span>
              </v-tab>
              <v-tab class="background-light_grey">
                <span>Others</span>
                <span>&nbsp;({{ offlineDrivers.length }})</span>
              </v-tab>
            </v-tabs>
          </v-col>
        </v-row>
      </v-col>
      <v-col cols="12" class="pb-4 mt-4">
        <v-tabs-items
          v-model="activeTab"
          class="px-4 overflow-y-auto"
          :style="{ height: tabHeight }"
        >
          <v-tab-item>
            <div v-for="(driver, index) in onlineDrivers" :key="index">
              <OperationDrivercard
                @selectDriver="changeSelectedDriver(driver)"
                @showChat="
                  getDriverChatData(
                    driver.id,
                    driver.driver_name,
                    driver.status
                  )
                "
                :driver="driver"
                :selectedDriver="selectedDriver"
                :showChatButton="true"
              />
            </div>
          </v-tab-item>
          <v-tab-item>
            <div v-for="(driver, index) in offlineDrivers" :key="index">
              <OperationDrivercard
                :driver="driver"
                :selectedDriver="selectedDriver"
                :showChatButton="false"
              />
            </div>
          </v-tab-item>
        </v-tabs-items>
      </v-col>
    </v-row>

    <div class="position-relative">
      <CommonChat v-model="openChatDialogBox" :driverDetails="driverDetails" />
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      filter: {},
      activeTab: "on-duty",
      searchString: null,
      openChatDialogBox: false,
      driverDetails: {},
      selectedProjects: [],
      driverListInterval: null,
    };
  },
  props: ["selectedDriver", "showDriverLoader"],
  computed: {
    tabHeight() {
      return `${window.innerHeight - 320}px`;
    },
    projectList() {
      return this.$store.getters["project/PROJECT_LIST_FOR_DROPDOWN"];
    },
    containerHeight() {
      if (this.$vuetify.breakpoint.xl) {
        return ((window.innerHeight / 100) * 85).toFixed() + "px";
      } else if (this.$vuetify.breakpoint.lg) {
        return ((window.innerHeight / 100) * 70).toFixed() + "px";
      } else if (this.$vuetify.breakpoint.md) {
        return ((window.innerHeight / 100) * 70).toFixed() + "px";
      }
    },
    onlineDrivers() {
      if (
        this.searchString != null &&
        this.searchString.length &&
        this.searchString.trim() != ""
      ) {
        return this.$store.state.operation.drivers_list.filter((driver) => {
          return (
            driver.driver_name
              .toLowerCase()
              .indexOf(this.searchString.toLowerCase()) > -1 &&
            driver.is_working
          );
        });
      } else {
        return this.$store.state.operation.drivers_list.filter((driver) => {
          return driver.is_working;
        });
      }
    },
    offlineDrivers() {
      if (
        this.searchString != null &&
        this.searchString.length &&
        this.searchString.trim() != ""
      ) {
        return this.$store.state.operation.drivers_list.filter((driver) => {
          return (
            driver.driver_name
              .toLowerCase()
              .indexOf(this.searchString.toLowerCase()) > -1 &&
            !driver.is_working
          );
        });
      } else {
        return this.$store.state.operation.drivers_list.filter((driver) => {
          return !driver.is_working;
        });
      }
    },
    workerInstance: {
      get() {
        return this.$store.state.user_notification.workerInstance;
      },
      set(value) {
        this.$store.commit("user_notification/SET_WORKER_INSTANCE", value);
      },
    },
  },
  methods: {
    setFilters() {
      if (this.selectedProjects.length > 0) {
        localStorage.setItem(
          "operations_projects_filter",
          this.selectedProjects.join()
        );
      } else {
        localStorage.removeItem("operations_projects_filter");
      }
    },
    refreshFilters() {
      this.selectedProjects =
        localStorage.getItem("operations_projects_filter") != null
          ? localStorage.getItem("operations_projects_filter").split(",")
          : [];
    },
    applyProjectFilter(loader) {
      this.setFilters();
      if (this.$refs.operationProjectFilter) {
        this.$refs.operationProjectFilter.blur();
      }
      if (this.selectedProjects.length > 0) {
        this.filter.projects = this.selectedProjects.join(",");
      } else {
        delete this.filter.projects;
      }

      this.$emit("getDriversList", this.filter, loader);
    },
    changeSelectedDriver(driver) {
      this.$emit("selectedDriverChanged", driver);
    },
    getDriverChatData(id, driverName, status) {
      this.$store
        .dispatch("operation/GET_CHAT_DATA", id)
        .then((response) => {
          this.openChatDialogBox = true;
          this.driverDetails = {
            id: id,
            driverName: driverName,
            status: status,
          };
        })
        .catch((error) => {
          this.$notifier.showMessage({
            content: "Couln't fetch data",
            color: "error",
          });
        });
    },
    getDriverStatusColor(status) {
      switch (status) {
        case "Off Duty":
          return "grey";
        case "On Duty":
          return "pgreen";
        case "Break":
          return "orange";
      }
    },
  },
  mounted() {
    this.refreshFilters();
    this.applyProjectFilter(true);
    this.driverListInterval = setInterval(() => {
      this.applyProjectFilter(false);
    }, 60000);
  },
  beforeDestroy() {
    clearInterval(this.driverListInterval);
  },
};
</script>

<style>
.stick-bottom {
  bottom: 0px;
}
.text-overflow-ellipsis {
  text-overflow: ellipsis;
}
</style>