<template>
  <div class="pa-6">
    <v-row no-gutters class="pb-6">
      <v-col cols="6">
        <span class="text-h5 text-uppercase font-weight-bold">
          Plan My Trip
        </span>
      </v-col>
      <v-col cols="6" class="text-right">
        <v-btn
          depressed
          color="primary"
          class="rounded"
          @click="openTripPlanFilterDialog=true"
        >
          <v-icon small class="mr-1">mdi-filter</v-icon>
          Filter
        </v-btn>
      </v-col>
    </v-row>
    <v-row no-gutters class="pb-6">
      <v-col class="pb-6" cols="12" v-if="userPermissions.trip.add">
        <v-form ref="planTripForm" v-model="planTripForm">
          <v-row>
            <v-col cols="3">
              <v-text-field
                color="light_black"
                name="plan_name"
                v-model="tripDetail.plan_name"
                :rules="[
                  (v) =>
                    (!!v && v.trim().length > 0) || 'Plan Name is Required',
                ]"
                dense
                outlined
                hide-details="auto"
                label="Plan Name*"
                @input="'plan_name' in error ? (error['plan_name'] = []) : null"
                :error-messages="error.plan_name"
              >
              </v-text-field>
            </v-col>
            <v-col cols="2">
              <v-menu
                v-model="datepicker"
                :close-on-content-click="false"
                :nudge-right="40"
                transition="scale-transition"
                offset-y
                min-width="auto"
              >
                <template v-slot:activator="{ on, attrs }">
                  <v-text-field
                    color="light_black"
                    name="plan_date"
                    v-model="tripDetail.date"
                    outlined
                    dense
                    label="Plan Date"
                    hide-details="auto"
                    v-bind="attrs"
                    v-on="on"
                    :error-messages="error.plan_date"
                  ></v-text-field>
                </template>
                <v-date-picker
                  @change="validateField"
                  v-model="tripDetail.date"
                  @input="
                    datepicker = false;
                    error['plan_date'] = [];
                  "
                ></v-date-picker>
              </v-menu>
            </v-col>
            <v-col cols="3">
              <v-select
                ref="planTripProjectSelect"
                color="light_black"
                name="project"
                item-color="grey"
                :items="projectList"
                v-model="tripDetail.project"
                outlined
                dense
                hide-details="auto"
                label="Project*"
                :rules="[(v) => !!v || 'Project is Required']"
                @change="validateField"
                :menu-props="{ offsetY: true }"
                :error-messages="error.project"
              >
                <template v-slot:prepend-item>
                  <div
                    class="
                      pt-2
                      mt-n2
                      background-white
                      position-sticky
                      stick-top
                      full-width
                    "
                  >
                    <v-list-item>
                      <v-text-field
                        class="mb-2 pt-1"
                        v-model="projectSearchText"
                        placeholder="Search Projects..."
                        :disabled="projectList.length === 0"
                        clearable
                        hide-details
                        prepend-inner-icon="mdi-magnify"
                      ></v-text-field>
                    </v-list-item>
                    <v-divider class="mt-2"></v-divider>
                  </div>
                </template>
                <template v-slot:item="{ item }">
                  <v-list-item
                    ripple
                    @click="
                      $refs.planTripProjectSelect.setValue(item.value);
                      $refs.planTripProjectSelect.blur();
                    "
                    v-show="searchSelect(item.text, projectSearchText)"
                  >
                    <v-list-item-content>
                      <v-list-item-title>
                        {{ item.text }}
                      </v-list-item-title>
                    </v-list-item-content>
                  </v-list-item>
                </template>
              </v-select>
            </v-col>
            <v-col cols="3">
              <v-select
                ref="plantripFormDriversSelect"
                color="light_black"
                item-color="grey"
                :items="driverList"
                v-model="tripDetail.drivers"
                name="drivers"
                outlined
                multiple
                dense
                hide-details="auto"
                label="Driver"
                :menu-props="{ offsetY: true }"
                :error-messages="error.drivers"
              >
                <template v-slot:selection="{ item, index }">
                  <span v-if="tripDetail.drivers.length === 1">
                    {{ item.text }}
                  </span>
                  <span v-if="tripDetail.drivers.length > 1 && index === 0">
                    {{ tripDetail.drivers.length }} Drivers Selected
                  </span>
                </template>
                <template v-slot:prepend-item>
                  <div
                    class="
                      pt-2
                      mt-n2
                      background-white
                      position-sticky
                      stick-top
                      full-width
                    "
                  >
                    <v-list-item>
                      <v-text-field
                        class="mb-2 pt-1"
                        v-model="driverSearchText"
                        placeholder="Search Drivers..."
                        :disabled="driverList.length === 0"
                        clearable
                        hide-details
                        prepend-inner-icon="mdi-magnify"
                      ></v-text-field>
                    </v-list-item>
                    <v-list-item ripple @click="toggleSelectAll">
                      <v-list-item-action>
                        <v-icon color="grey">
                          {{ icon }}
                        </v-icon>
                      </v-list-item-action>
                      <v-list-item-content>
                        <v-list-item-title> Select All </v-list-item-title>
                      </v-list-item-content>
                    </v-list-item>
                    <v-divider class="mt-2"></v-divider>
                  </div>
                </template>
                <template v-slot:item="{ item }">
                  <v-list-item
                    ripple
                    @click="selectItem(item)"
                    v-show="searchSelect(item.text, driverSearchText)"
                  >
                    <v-list-item-action>
                      <v-checkbox
                        color="grey"
                        readonly
                        :input-value="
                          tripDetail.drivers.indexOf(item.value) > -1
                        "
                      ></v-checkbox>
                    </v-list-item-action>
                    <v-list-item-content>
                      <v-list-item-title>
                        {{ item.text }}
                      </v-list-item-title>
                    </v-list-item-content>
                  </v-list-item>
                </template>
              </v-select>
            </v-col>
            <v-col cols="1" class="d-flex justify-center align-center">
              <v-btn
                depressed
                :disabled="!planTripForm"
                class="primary"
                @click="planNewTrip"
              >
                Submit
              </v-btn>
            </v-col>
          </v-row>
        </v-form>
      </v-col>
      <v-col cols="8" class="py-2">
        <div v-if="!showOrderData">
          <span class="font-weight-bold text-subtitle-1"> Recent Plans </span>
        </div>
        <v-row v-else class="d-flex align-center">
          <v-col cols="2">
            <span class="font-weight-bold text-subtitle-1"> Order List </span>
          </v-col>
          <v-col cols="3"> </v-col>
        </v-row>
      </v-col>
      <v-col cols="4" class="d-flex justify-end py-2">
        <div class="d-flex">
          <v-text-field
            outlined
            dense
            class="mr-4"
            v-model="searchPlanString"
            placeholder="Search"
            clearable
            @input="getPlanList"
            hide-details
            v-show="!showOrderData"
            prepend-inner-icon="mdi-magnify"
          ></v-text-field>
          <v-btn
            class="primary mr-2"
            v-show="showOrderData"
            :disabled="
              (driverData && driverData.length == 0) ||
              (ZoneData && ZoneData.length == 0) ||
              (ordersData && ordersData.length == 0)
            "
            small
            @click="exportWarningOrders"
          >
            Export
          </v-btn>
        </div>

        <v-btn
          small
          depressed
          @click="
            showOrderData = !showOrderData;
            searchString = null;
          "
          class="primary"
          v-show="showOrderButton"
        >
          <span v-if="showOrderData">Show Recent Plans</span>
          <span v-else>Show Order List</span>
        </v-btn>
      </v-col>

      <v-col cols="12">
        <v-row>
          <v-col cols="9">
            <v-tabs v-if="showOrderData" v-model="currentTab">
              <v-tab>
                <span class="mr-1">Orders </span>
                <span v-if="ordersData"> ({{ ordersData.length }})</span>
              </v-tab>
              <v-tab> Drivers </v-tab>
              <v-tab v-show="zoneConstraint"> Zones </v-tab>
            </v-tabs>
          </v-col>
          <v-col cols="3" v-if="showOrderData" class="d-flex justify-end">
            <v-text-field
              class="my-3"
              outlined
              dense
              v-model="searchString"
              placeholder="Search"
              clearable
              hide-details
              prepend-inner-icon="mdi-magnify"
            ></v-text-field>
          </v-col>
        </v-row>
        <AgGridVue
          @grid-ready="gridReady"
          :grid-options="gridOptions"
          :column-defs="
            !showOrderData
              ? columnDefs
              : currentTab === 0
              ? orderColumnDefs
              : currentTab === 1
              ? driverColumnDefs
              : zoneColumnDefs
          "
          :context="context"
          :default-col-def="defaultColDef"
          :row-data="
            !showOrderData
              ? planedTripList
              : currentTab === 0
              ? ordersData
              : currentTab === 1
              ? driverData
              : currentTab === 2
              ? ZoneData
              : []
          "
          :style="{ width: '100%', height: gridHeight }"
          class="ag-theme-material mt-2 cf-table"
        >
        </AgGridVue>
      </v-col>
      <v-col cols="12" class="py-3 d-flex justify-end" v-if="!showOrderData">
        <CommonPagination
          :page-no="pageNo"
          :num-of-pages="totalPages"
          :page-size="itemsPerPage"
          @nextPage="nextPage"
          @prevPage="prevPage"
          @itemsPerPageChange="itemsPerPageChange"
        />
      </v-col>
    </v-row>
    <PlantripPlaninfo v-model="openFailedInfoDialog" :info="system_warnings" />
    <PlantripWarningsInfo v-model="openWarningInfoDialog" :info="warnings" />
    <PlantripTripplanfilter 
      ref="tripplanFilterDialog"
      v-model="openTripPlanFilterDialog"
      @tripplanFilterChanged="tripplanFilterChanged"
    />
  </div>
</template>


<script>
import XLSX from "xlsx";
import { toCapitalize } from "~/assets/utils";
import { AgGridVue } from "ag-grid-vue";
import planedTripButton from "~/components/common/aggrid/buttons/planedTripButton.vue";
import PlanningTripButton from "~/components/common/aggrid/buttons/planningTripButton.vue";
import { makeInstance, encryptLocal } from "~/assets/js/encryptLocal";
import { toTitleCase } from "~/assets/utils.js";

export default {
  props: {
    value: Boolean,
  },
  components: {
    AgGridVue,
    planedTripButton,
    PlanningTripButton,
  },
  data() {
    return {
      openFailedInfoDialog: false,
      openWarningInfoDialog: false,
      openTripPlanFilterDialog: false,
      customFilter: {},
      zoneConstraint: false,
      system_warnings: {},
      warnings: {},
      currentTab: 0,
      context: null,
      driverData: [],
      ZoneData: [],
      ordersData: [],
      interval: null,
      searchPlanString: "",
      searchString: "",
      showOrderData: false,
      showOrderButton : false,
      error: {},
      defaultColDef: {
        lockPosition: true,
      },
      driverSearchText: null,
      projectSearchText: null,
      planTripForm: false,
      datepicker: false,
      gridApi: null,
      columnApi: null,
      tripDetail: {
        date: new Date().toISOString().substr(0, 10),
        plan_name: null,
        project: null,
        drivers: [],
      },
      gridOptions: {
        headerHeight: 40,
        rowHeight: 40,
        suppressRowClickSelection: true,
        suppressDragLeaveHidesColumns: true,
        enableCellTextSelection: true,
      },
      columnDefs: [
        {
          headerName: "Plan Name",
          field: "plan_name",
          width: 300,
          pinned: "left",
        },
        {
          headerName: "Date",
          field: "plan_date",
        },
        {
          headerName: "Project",
          field: "project_name",
        },
        {
          headerName: "Status",
          field: "status",
          cellRenderer: (params) => {
            return toTitleCase(params.value);
          },
        },
        {
          headerName: "Progress",
          field: "progress",
          cellRenderer: (param) => {
            if (param.value > -1) {
              return param.value + "%";
            }
          },
        },
        {
          headerName: "Total Order",
          field: "orders_count",
          cellRenderer: (param) => {
            if (param.data.status == "PENDING") {
              return "N/A";
            } else {
              return param.value;
            }
          },
        },
        {
          headerName: "Total Distance",
          field: "distance",
          cellRenderer: (param) => {
            if (param.data.status !== "COMPLETED") {
              return "N/A";
            } else {
              return param.value / 1000 + " km";
            }
          },
        },
        {
          headerName: "Total Trips",
          field: "trips_count",
          cellRenderer: (param) => {
            if (param.data.status !== "COMPLETED") {
              return "N/A";
            } else {
              return param.value;
            }
          },
        },
        {
          headerName: "Actions",
          field: "id",
          width: 300,
          pinned: "right",
          cellRendererFramework: "planedTripButton",
        },
      ],
      orderColumnDefs: [
        {
          headerName: "Reference Number",
          pinned: "left",
          field: "reference_number",
        },
        {
          headerName: "Customer Code",
          field: "customer_code",
          width: 200,
        },
        {
          headerName: "Customer Name",
          field: "customer_name",
          width: 400,
        },
        {
          headerName: "Address",
          field: "address",
        },
        {
          headerName: "Customer Contact No.",
          field: "contact_number",
        },
        {
          headerName: "No. Of Items",
          field: "no_of_items",
          width: 130,
        },
        {
          headerName: "Planned processing time",
          field: "planned_processing_time",
        },
        {
          headerName: "Order Date",
          field: "execution_date",
        },
        {
          headerName: "Action",
          field: "action",
          pinned: "right",
          cellRendererFramework: "PlanningTripButton",
        },
      ],
      driverColumnDefs: [
        {
          headerName: "Driver Name",
          field: "driver_name",
          pinned: "left",
        },
        {
          headerName: "Vehicle",
          field: "vehicle",
        },
        {
          headerName: "Contact Number",
          field: "contact_number",
        },
        {
          headerName: "Shift Start",
          field: "shift_start",
        },
        {
          headerName: "Shift End",
          field: "shift_end",
        },
        {
          headerName: "Zone",
          field: "zone",
        },
        {
          headerName: "Action",
          width: 200,
          pinned: "right",
          field: "action",
          cellRendererFramework: "PlanningTripButton",
        },
      ],
      zoneColumnDefs: [
        {
          headerName: "Zone Name",
          field: "zone_name",
          pinned: "left",
        },
        {
          headerName: "Zone Shift Start",
          field: "zone_details.zone_shift_start",
        },
        {
          headerName: "Zone Shift End",
          field: "zone_details.zone_shift_end",
        },
        {
          headerName: "Driver Count",
          field: "zone_details.driver_count",
        },
        {
          headerName: "Order Count",
          field: "zone_details.order_count",
        },
        {
          headerName: "Action",
          width: 200,
          pinned: "right",
          field: "action",
          cellRendererFramework: "PlanningTripButton",
        },
      ],
      filter: {},
      itemsPerPage: 10,
      pageNo: 1,
      userPermissions: encryptLocal.getItem("permissions"),
      ordersMismatchWithDriverZone: [],
    };
  },
  watch: {
    showOrderData(val) {
      if (val) {
        setTimeout(() => {
          this.autoSizeAll();
        }, 1000);
      }
    },
    searchString(str) {
      this.gridApi.setQuickFilter(str);
    },
    currentTab() {
      if (this.currentTab == 1 || this.currentTab == 2) {
        setTimeout(() => {
          this.gridOptions.api.sizeColumnsToFit();
        }, 50);
      } else {
        setTimeout(() => {
          this.autoSizeAll();
        }, 1000);
      }
    },
  },
  computed: {
    gridHeight() {
      return `${window.innerHeight - 364}px`;
    },
    projectList() {
      return this.$store.getters["project/PROJECT_LIST_FOR_FILTER"];
    },
    planedTripList() {
      return this.$store.state.trip_creation.recentlyPlannedTrips;
    },
    driverList() {
      return this.$store.state.trip_creation.unassignedDriverList.map(
        (driver) => {
          return {
            text: driver.first_name,
            value: driver.id,
          };
        }
      );
    },
    checkedAll() {
      return this.tripDetail.drivers.length === this.driverList.length;
    },
    checkedSome() {
      return this.tripDetail.drivers.length > 0 && !this.checkedAll;
    },
    icon() {
      if (this.checkedAll) return "mdi-checkbox-marked";
      if (this.checkedSome) return "mdi-minus-box";
      return "mdi-checkbox-blank-outline";
    },
    offset() {
      return this.itemsPerPage * (this.pageNo - 1);
    },
    totalPages() {
      return Math.ceil(
        this.$store.state.trip_creation.totalItems / this.itemsPerPage
      );
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
    exportWarningOrders() {
      let orders = this.ordersData
        .filter((order) => order.warnings && order.warnings.length != 0)
        .map((order) => {
          return {
            reference_number: order.reference_number,
            reasons: order.warnings.toString(),
          };
        });
      let drivers = this.driverData
        .filter((driver) => driver.warnings && driver.warnings.length != 0)
        .map((driver) => {
          return {
            driver_name: driver.driver_name,
            reasons: driver.warnings.toString(),
          };
        });
      let zones = this.ZoneData.filter(
        (zone) =>
          zone.zone_details &&
          zone.zone_details.warnings &&
          zone.zone_details.warnings.length != 0
      ).map((zone) => {
        return {
          zone_name: zone.reference_number,
          reasons: zone.zone_details.warnings.toString(),
        };
      });
      this.downlaodTripSheet({
        orders: orders,
        drivers: drivers,
        zones: zones,
      });
    },
    formatHeaders(data) {
      return data.map((e, i) => {
        let obj = {};
        Object.keys(e).forEach((header, j) => {
          let h = header.replace(/\_/g, " ");
          obj[toCapitalize(h)] = e[header];
        });
        return obj;
      });
    },
    downlaodTripSheet(warningList) {
      const orders_data = XLSX.utils.json_to_sheet(
        this.formatHeaders(warningList.orders)
      );
      const drivers_data = XLSX.utils.json_to_sheet(
        this.formatHeaders(warningList.drivers)
      );
      const zones_data = XLSX.utils.json_to_sheet(
        this.formatHeaders(warningList.zones)
      );
      const wb = XLSX.utils.book_new();
      wb.Props = {
        Title: "Warning Sheet excel file",
        Subject: "Warning Sheet Excel",
        Author: "chefme",
        CreatedDate: new Date(),
      };

      XLSX.utils.book_append_sheet(wb, orders_data, "Orders");
      XLSX.utils.book_append_sheet(wb, drivers_data, "Drivers");
      XLSX.utils.book_append_sheet(wb, zones_data, "Zones");
      XLSX.writeFile(wb, "order-driver-zone-warnings.xlsx");
    },
    autoSizeAll() {
      let allColumnIds = [];
      this.gridOptions.columnApi.getAllColumns().forEach(function (column) {
        allColumnIds.push(column.colId);
      });
      this.gridOptions.columnApi.autoSizeColumns(allColumnIds);
    },
    openWarningDialog(data) {
      this.warnings = data;
      this.openWarningInfoDialog = true;
    },
    openPlanInformationDialog() {
      this.openFailedInfoDialog = true;
    },
    deleteRecentPlans(id) {
      this.$store
        .dispatch("trip_creation/DELETE_PLANED_TRIP", id)
        .then((result) => {
          this.$notifier.showMessage({
            content: "Plan Deleted successfully",
            color: "success",
          });
        })
        .catch((err) => {
          this.$notifier.showMessage({
            content: "Plan not delete",
            color: "error",
          });
        });
    },
    itemsPerPageChange(value) {
      this.pageNo = 1;
      this.itemsPerPage = value;
      this.getAllPlanTripsData();
    },
    nextPage() {
      this.pageNo++;
      this.getAllPlanTripsData();
    },
    prevPage() {
      this.pageNo--;
      this.getAllPlanTripsData();
    },
    gridReady(params) {
      this.gridApi = params.api;
      this.columnApi = params.columnApi;
    },
    selectItem(item) {
      if (this.tripDetail.drivers.indexOf(item.value) > -1) {
        this.tripDetail.drivers.splice(
          this.tripDetail.drivers.indexOf(item.value),
          1
        );
      } else {
        this.tripDetail.drivers.push(item.value);
      }
    },
    searchSelect(textToMatch, searchString) {
      if (searchString == null || searchString.trim().length == 0) {
        return true;
      } else {
        return textToMatch.toLowerCase().indexOf(searchString.toLowerCase()) > -1;
      }
    },
    validateField(e) {
      this.error["project"] = [];

      if (this.tripDetail.date && this.tripDetail.project) {
        this.showOrderData = false;
        let driverParams = {
          project__id: this.tripDetail.project,
          limit: "all",
          is_active: true,
        };
        let orderParams = {
          project_id: this.tripDetail.project,
          date: this.tripDetail.date,
        };

        this.$store
          .dispatch("trip_creation/GET_UNASSIGNED_DRIVERS", driverParams)
          .then(() => {
            this.$store
              .dispatch(
                "trip_creation/GET_UNASSIGNED_ORDER_FOR_PLAN_TRIP",
                orderParams
              )
              .then((data) => {
                this.ordersMismatchWithDriverZone =
                  data.orders_mismatch_with_driver_zone;
                this.ordersData = data.orders;
                this.driverData = data.drivers;
                this.ZoneData = data.zones;
                this.showOrderData = true;
                this.zoneConstraint = data.zone_constraint;
                this.showOrderButton = true;

                setTimeout(() => {
                  this.gridApi.sizeColumnsToFit();
                }, 500);

                if (this.ordersMismatchWithDriverZone.length > 0) {
                  this.getProjectDetails(this.tripDetail.project);
                }
              });
          });
      }
    },
    clearForm() {
      this.tripDetail = {
        date: new Date().toISOString().substr(0, 10),
        plan_name: null,
        project: null,
        drivers: [],
      };
      this.driverData = [];
      this.ZoneData = [];
      this.ordersData = [];
      this.showOrderData = false;
      this.showOrderButton = false;
      this.$refs.planTripForm.reset();
    },
    planNewTrip() {
      let details = {
        plan_name: this.tripDetail.plan_name,
        plan_date: this.tripDetail.date,
        selected_drivers: this.tripDetail.drivers.join(","),
        project: this.tripDetail.project,
      };
      this.$store
        .dispatch("trip_creation/PLAN_NEW_TRIP", details)
        .then((res) => {
          this.getAllPlanTripsData();
          this.clearForm();
        })
        .catch((err) => {
          this.error = err.data;
        });
    },
    getPlanList() {
      this.filter.limit = this.itemsPerPage;
      this.filter.offset = this.offset;
      this.filter.search = this.searchPlanString;
      this.$store.dispatch("trip_creation/GET_ALL_TRIP_PLANS", this.filter);
    },
    getAllPlanTripsData() {
      this.filter.limit = this.itemsPerPage;
      this.filter.offset = this.offset;
      this.$store.dispatch("trip_creation/GET_ALL_TRIP_PLANS", {...this.filter, ...this.customFilter});
    },
    toggleSelectAll() {
      this.$nextTick(() => {
        if (this.checkedAll) {
          this.tripDetail.drivers = [];
        } else {
          this.tripDetail.drivers = this.driverList
            .map((driver) => {
              return driver.value;
            })
            .slice();
        }
      });
    },
    workerTripPlanHandler() {
      if (this.workerInstance) {
        const url = `${this.$axios.defaults.baseURL}api/v1/trip_plan/`;
        this.workerInstance.postMessage({
          event: "get_trip_plan_list",
          token: localStorage.getItem("user"),
          url: url,
          params: {...this.filter, ...this.customFilter},
        });
        let self = this;
        this.workerInstance.onmessage = function (e) {
          if (e.data && e.data.event == "set_trip_plan_list") {
            self.$store.commit(
              "trip_creation/SET_RECENTLY_PLANNED_TRIPS",
              e.data.trip_plan_list
            );
          }
        };
      }
    },
    getProjectDetails(id) {
      this.$store
        .dispatch("project/GET_PROJECT_DETAILS", id)
        .then((result) => {
          this.$refs.projectForm.loadServisableArea(
            result.serviceable_area.coordinates
          );
        })
        .catch((err) => {
          // this.$notifier.showMessage({
          //   content: "Couln't fetch data",
          //   color: "error",
          // });
        });
    },
    tripplanFilterChanged() {
      let filters = localStorage.getItem("tripplanFilters");
      if (!filters) {
        filters = {};
      }
      if (typeof filters == typeof "string") {
        filters = JSON.parse(filters);
      }
      if(filters && "status" in filters && Array.isArray(filters.status)) {
        filters.status = filters.status.join(",");
      }
      if(filters && "project" in filters && Array.isArray(filters.project)) {
        filters.project = filters.project.join(",");
      }
      if(filters && "ordering" in filters && "sorting" in filters) {
        if(filters.sorting == "descending"){
          filters.ordering = "-" + filters.ordering
        }
      }
      this.customFilter = filters
      this.pageNo = 1;
      this.getAllPlanTripsData();
    },
  },
  beforeMount() {
    this.getAllPlanTripsData();
    if (encryptLocal == null) {
      makeInstance(localStorage.getItem("user"));
    }
  },
  mounted() {
    this.context = {
      parentComponent: this,
    };
    if (process.browser) {
      this.interval = setInterval(() => {
        if (!this.filter.search) {
          delete this.filter["search"];
        }
        if (this.workerInstance) {
          this.workerTripPlanHandler();
        }
      }, 30000);
    }
    this.tripplanFilterChanged();
  },
  beforeDestroy() {
    clearInterval(this.interval);
    this.searchString = "";
    this.$store.commit("trip_creation/EMPTY_ALL_FIELDS");
  },
};
</script>

<style lang="scss" scoped>
.stick-top {
  top: 0px !important;
  z-index: 1;
}
</style>
