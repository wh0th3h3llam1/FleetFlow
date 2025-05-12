<template>
  <div
    class="pa-4"
    @scroll="reSetColumn()"
    style="height: 100%; width: 100%; overflow: scroll; position: absolute"
  >
    <v-col cols="12">
      <div
        @click="panel = !panel"
        class="background-primary white--text px-6 py-3"
      >
        <v-row>
          <v-col cols="6">
            <div>
              <v-fade-transition leave-absolute>
                <span v-if="panel && Object.keys(selectedReoprt).length !== 0">
                  Selected Report :- {{ selectedReoprt.title }}
                </span>
                <span v-else> Select Report Type </span>
              </v-fade-transition>
            </div>
          </v-col>
          <v-col cols="6" class="d-flex justify-end">
            <v-icon color="white" :class="panel ? `${rotatedIcon}` : ''">
              mdi-chevron-down
            </v-icon>
          </v-col>
        </v-row>
      </div>
      <v-expand-transition>
        <div
          class="d-flex flex-row background-light_grey pa-4"
          v-if="panel"
          style="overflow-x: scroll"
        >
          <v-card
            v-for="(item, i) in reportType"
            :key="i"
            :class="
              selectedReoprt.title == item.title
                ? 'on-hover float-left ma-2 pa-4 text-center primary text-white'
                : 'on-hover float-left ma-2 pa-4 text-center'
            "
            outlined
            tile
            width="9%"
            @click="updateReportType(item)"
          >
            <v-row class="pa-2" no-gutters>
              <v-col cols="12" class="d-flex justify-center">
                <v-icon
                  class="pb-2"
                  :color="
                    selectedReoprt.title == item.title ? 'white' : 'primary'
                  "
                  >{{ item.icon }}</v-icon
                >
              </v-col>
              <v-col cols="12" class="d-flex justify-center">
                <span class="text-caption"> {{ item.title }}</span>
              </v-col>
            </v-row>
          </v-card>
        </div>
      </v-expand-transition>

      <v-alert
        border="left"
        colored-border
        color="red"
        v-if="distinctErrors.length"
      >
        <v-list class="py-0">
          <v-list-item-content class="py-0">
            <v-list-item-title class="text-grey font-weight-medium"
              >Error(s):
            </v-list-item-title>
            <v-list-item-subtitle
              class="pl-4 pt-1 text-grey"
              v-for="(err, index) in distinctErrors"
              :key="index"
            >
              {{ err }}
            </v-list-item-subtitle>
          </v-list-item-content>
        </v-list>
      </v-alert>
    </v-col>
    <v-col cols="12">
      <v-card elevation="0" outlined class="py-5 px-4">
        <v-row>
          <v-col cols="12">
            <v-row class="px-5">
              <v-col cols="12">
                <span class="text-body-1 font-weight-bold">Filters</span>
              </v-col>
              <v-col cols="10">
                <v-row>
                  <v-col cols="2">
                    <v-menu
                      ref="menu"
                      v-model="menu"
                      :close-on-content-click="false"
                      :return-value.sync="filter.start_date"
                      transition="scale-transition"
                      :nudge-right="40"
                      offset-y
                      min-width="auto"
                    >
                      <template v-slot:activator="{ on, attrs }">
                        <v-text-field
                          v-model="filter.start_date"
                          label="Start Date*"
                          prepend-inner-icon="mdi-calendar"
                          readonly
                          outlined
                          dense
                          v-bind="attrs"
                          v-on="on"
                        ></v-text-field>
                      </template>
                      <v-date-picker
                        @change="dateValidator"
                        v-model="filter.start_date"
                        @click:date="$refs.menu.save(filter.start_date)"
                        :max="nowDate"
                        no-title
                        scrollable
                      >
                      </v-date-picker>
                    </v-menu>
                  </v-col>
                  <v-col cols="2">
                    <v-menu
                      ref="menu2"
                      v-model="menu2"
                      :close-on-content-click="false"
                      :return-value.sync="filter.end_date"
                      transition="scale-transition"
                      :nudge-right="40"
                      offset-y
                      min-width="auto"
                    >
                      <template v-slot:activator="{ on, attrs }">
                        <v-text-field
                          v-model="filter.end_date"
                          label="End Date*"
                          prepend-inner-icon="mdi-calendar"
                          readonly
                          dense
                          outlined
                          v-bind="attrs"
                          v-on="on"
                        ></v-text-field>
                      </template>
                      <v-date-picker
                        v-model="filter.end_date"
                        @change="dateValidator"
                        no-title
                        scrollable
                        @click:date="$refs.menu2.save(filter.end_date)"
                        :max="nowDate"
                      >
                      </v-date-picker>
                    </v-menu>
                  </v-col>
                  <v-col cols="2">
                    <multiselect
                      id="allProjects"
                      class="cf-multipe-select"
                      v-model="filter.project"
                      :options="allProjects"
                      :multiple="true"
                      placeholder="Select Project"
                      track-by="text"
                      :limit="1"
                      :limitText="(count) => `+ ${count}`"
                      label="text"
                      group-values="projects"
                      group-label="selectAll"
                      :group-select="true"
                      :close-on-select="false"
                      :showLabels="false"
                      tag-position="bottom"
                      @close="getDriverVehicleData"
                    >
                    </multiselect>
                  </v-col>
                  <!---------------------------- If report type is vehicle or driver ---------------------------->
                  <v-col
                    cols="2"
                    v-if="
                      selectedReoprt.category == 'driver' ||
                      selectedReoprt.category == 'vehicle'
                    "
                  >
                    <multiselect
                      :placeholder="
                        selectedReoprt.category == 'driver'
                          ? 'Select Driver'
                          : 'Select Vehicle'
                      "
                      class="cf-multipe-select"
                      v-model="filter.type"
                      :options="
                        selectedReoprt.category == 'driver'
                          ? allDrivers
                          : allVehicles
                      "
                      :multiple="true"
                      :track-by="
                        selectedReoprt.category == 'driver'
                          ? 'first_name'
                          : 'vehicle_plate_no'
                      "
                      :limit="1"
                      :limitText="(count) => `+ ${count}`"
                      :label="
                        selectedReoprt.category == 'driver'
                          ? 'first_name'
                          : 'vehicle_plate_no'
                      "
                      :group-values="
                        selectedReoprt.category == 'driver'
                          ? 'drivers'
                          : 'vehicles'
                      "
                      group-label="selectAll"
                      :group-select="true"
                      :close-on-select="false"
                      :showLabels="false"
                      tag-position="bottom"
                    >
                    </multiselect>

                    <!-- <v-select
                      dense
                      hide-details="auto"
                      outlined
                      :item-text="
                        selectedReoprt.category == 'driver'
                          ? 'first_name'
                          : 'vehicle_plate_no'
                      "
                      item-value="id"
                      v-model="filter.type"
                      :disabled="disabled"
                      multiple
                      clearable
                      :items="
                        selectedReoprt.category == 'driver'
                          ? allDrivers
                          : allVehicles
                      "
                      :label="
                        selectedReoprt.category == 'driver'
                          ? 'Select Driver'
                          : 'Select Vehicle'
                      "
                    >
                      <template v-slot:selection="{ item, index }">
                        <div v-if="selectedReoprt.category == 'driver'">
                          <span v-if="index === 0">{{ item.first_name }}</span>
                          <span
                            v-if="index === 1"
                            class="grey--text text-caption"
                          >
                            (+{{ filter.type.length - 1 }} others)
                          </span>
                        </div>
                        <div v-else>
                          <span v-if="index === 0">{{
                            item.vehicle_plate_no
                          }}</span>
                          <span
                            v-if="index === 1"
                            class="grey--text text-caption"
                          >
                            (+{{ filter.type.length - 1 }} others)
                          </span>
                        </div>
                      </template>
                    </v-select> -->
                  </v-col>
                  <!------------------------------------- If report type is order or trip ------------------------------------->
                  <v-col
                    cols="3"
                    v-if="
                      selectedReoprt.category == 'order' ||
                      selectedReoprt.category == 'trip'
                    "
                  >
                    <v-select
                      dense
                      hide-details="auto"
                      outlined
                      v-model="filter.status"
                      multiple
                      clearable
                      ref="select"
                      :items="
                        selectedReoprt.category == 'order'
                          ? orderStatus
                          : tripStatus
                      "
                      :label="
                        selectedReoprt.category == 'order'
                          ? 'Select Order Status'
                          : 'Select Trip Status'
                      "
                      :menu-props="{ offsetY: true }"
                    >
                      <template v-slot:selection="{ item, index }">
                        <v-chip v-if="index === 0" style="font-size:11px">
                          <span>{{ item.text }}</span>
                        </v-chip>
                        <span
                          v-if="index === 1"
                          class="grey--text text-caption"
                        >
                          (+{{ filter.status.length - 1 }} others)
                        </span>
                      </template>
                    </v-select>
                  </v-col>

                  <v-col cols="2" v-if="selectedReoprt.type == 'expense'">
                    <v-select
                      dense
                      hide-details="auto"
                      outlined
                      :disabled="disabled"
                      ref="expenses_Category"
                      clearable
                      v-model="filter.expenses"
                      :items="expenseCategory"
                      label="Driver Expense Category"
                    ></v-select>
                  </v-col>
                  <v-col cols="2" v-if="selectedReoprt.category == 'trip'">
                    <multiselect
                      placeholder="Select Trip Driver"
                      class="cf-multipe-select"
                      v-model="filter.driver"
                      :options="allDrivers"
                      :multiple="true"
                      track-by="first_name"
                      :limit="1"
                      :limitText="(count) => `+ ${count}`"
                      label="first_name"
                      group-values="drivers"
                      group-label="selectAll"
                      :group-select="true"
                      :close-on-select="false"
                      :showLabels="false"
                      tag-position="bottom"
                    >
                    </multiselect>
                  </v-col>
                  <v-col cols="2" v-if="selectedReoprt.category == 'trip'">
                    <multiselect
                      placeholder="Select Trip Vehicle"
                      class="cf-multipe-select"
                      v-model="filter.vehicle"
                      :options="allVehicles"
                      :multiple="true"
                      track-by="vehicle_plate_no"
                      :limit="1"
                      :limitText="(count) => `+ ${count}`"
                      label="vehicle_plate_no"
                      group-values="vehicles"
                      group-label="selectAll"
                      :group-select="true"
                      :close-on-select="false"
                      :showLabels="false"
                      tag-position="bottom"
                    >
                    </multiselect>
                  </v-col>
                </v-row>
              </v-col>
              <v-col cols="2" class="d-flex justify-end">
                <v-btn class="primary" @click="getReportData()">
                  Get report
                </v-btn>
              </v-col>
            </v-row>
          </v-col>
          <v-col cols="12" v-if="reportData.length">
            <v-row class="px-6">
              <v-col cols="8">
                <span class="font-weight-bold">{{ selectedReoprt.title }}</span>
              </v-col>
              <v-col cols="4" class="d-flex justify-end">
                <v-btn class="primary" @click="downloadReportData()">
                  <v-icon>mdi-file-download-outline</v-icon>
                  <span class="pl-2">Export</span>
                </v-btn>
              </v-col>
              <v-col cols="12">
                <AgGridVue
                  :grid-options="gridOptions"
                  :column-defs="Headers"
                  :row-data="reportData"
                  style="width: 100%; height: 550px"
                  class="ag-theme-material cf-table"
                >
                </AgGridVue>
              </v-col>
            </v-row>
          </v-col>
          <v-col
            v-if="firtsRequest && !reportData.length"
            cols="12"
            class="d-flex justify-center align-center"
            style="height: 42vh"
          >
            <span>Select Report type & filters</span>
          </v-col>
          <v-col
            v-if="!firtsRequest && !reportData.length"
            cols="12"
            class="d-flex justify-center align-center"
            style="height: 42vh"
          >
            <span>No data to show.</span>
          </v-col>
        </v-row>
      </v-card>
    </v-col>
  </div>
</template>

<script>
import { AgGridVue } from "ag-grid-vue";
import ZoneButton from "~/components/common/aggrid/buttons/ZoneButton.vue";
import Multiselect from "vue-multiselect";
import XLSX from "xlsx";
import { downloadBlobData } from "~/assets/utils";

export default {
  components: {
    AgGridVue,
    ZoneButton,
    Multiselect,
  },
  data() {
    return {
      firtsRequest: true,
      type: [],
      distinctErrors: [],
      rotatedIcon: "mdi-rotate-180",
      reportTypes: [
        {
          title: "Driver Expense Report",
          value: "driverEXPENSE",
          category: "driver",
          type: "expense",
          url: "/api/v1/driver_reports/driver_expense/",
          icon: "mdi-currency-usd",
        },
        {
          title: "Driver Attendance Report",
          value: "driverATTENDANCE",
          category: "driver",
          url: "/api/v1/driver_reports/driver_attandance/",
          icon: "mdi-account-check-outline",
        },
        {
          title: "Driver Kms Report",
          value: "driverKMS",
          category: "driver",
          icon: "mdi-map-marker-distance",
        },
        {
          title: "Driver Order Delivery Report",
          value: "orderDELIVERY",
          category: "driver",
          url: "/api/v1/driver_reports/driver_order_delivery/",
          icon: "mdi-archive-outline",
        },
        {
          title: "Driver Trips Report",
          value: "trip",
          category: "driver",
          url: "/api/v1/driver_reports/driver_trips/",
          icon: "mdi-archive-outline",
        },
        {
          title: "Fleet Utilization",
          value: "vehicleUTI",
          url: "/api/v1/vehicle_reports/vehicle_utilization/",
          category: "vehicle",
          icon: "mdi-truck-check",
        },
        {
          title: "Vehicle Total Odometer reading Report",
          category: "vehicle",
          url: "/api/v1/vehicle_reports/vehicle_total_mileage/",
          value: "vehicleMILAGE",
          icon: "mdi-truck-fast",
        },
        {
          title: "Daily Vehicle Kms Report",
          category: "vehicle",
          value: "vehicleKMS",
          url: "/api/v1/vehicle_reports/vehicle_daily_km_rum/",
          icon: "mdi-map-marker-distance",
        },
        {
          title: "Vehicle Trip Report",
          value: "trip",
          url: "/api/v1/vehicle_reports/vehicle_trips/",
          category: "vehicle",
          icon: "mdi-bus-clock",
        },
        {
          title: "Vehicle Order Delivery Report",
          value: "order",
          url: "/api/v1/vehicle_reports/vehicle_order_delivery/",
          category: "vehicle",
          icon: "mdi-archive",
        },
        {
          title: "Orders Report",
          value: "order",
          url: "/api/v1/order_reports/orders/",
          category: "order",
          icon: "mdi-archive",
        },
        {
          title: "Trips Report",
          value: "trip",
          url: "/api/v1/trip_reports/trips/",
          category: "trip",
          icon: "mdi-archive",
        },
      ],
      expenseCategory: [
        {
          text: "Fuel Receipt",
          value: "FuelFillReceipt",
        },
        {
          text: "Toll Receipt",
          value: "TollReceipt",
        },
        {
          text: "Parking Tickets",
          value: "ParkingTickets",
        },
        {
          text: "Other Receipt",
          value: "OtherReceipt",
        },
      ],
      panel: true,
      selectedReoprt: {},
      filter: {
        start_date: null,
        end_date: null,
      },
      disabled: true,
      menu: false,
      menu2: false,
      tripDate: false,
      gridApi: null,
      columnApi: null,
      gridOptions: {
        onGridSizeChanged: () => {
          this.gridOptions.api.sizeColumnsToFit();
        },
        headerHeight: 40,
        rowHeight: 40,
        rowSelection: "multiple",
        pagination: true,
        paginationPageSize: 20,
        suppressRowClickSelection: true,
        suppressDragLeaveHidesColumns: true,
        enableCellTextSelection: true,
      },
      orderStatus: [
        {
          text: "Unassigned",
          value: "unassigned",
        },
        {
          text: "Assigned",
          value: "assigned",
        },
        {
          text: "Shipped",
          value: "pickedup",
        },
        {
          text: "Partially Delivered",
          value: "partially_delivered",
        },
        {
          text: "Delivered",
          value: "successful",
        },
        {
          text: "Returned",
          value: "failed",
        },
        {
          text: "Cancelled",
          value: "cancelled",
        },
      ],
      tripStatus: [
        {
          text: "Scheduled",
          value: "scheduled",
        },
        {
          text: "Active",
          value: "active",
        },
        {
          text: "Paused",
          value: "paused",
        },
        {
          text: "Completed",
          value: "completed",
        },
      ],
      nowDate: new Date().toISOString().slice(0, 10),
    };
  },
  computed: {
    allProjects() {
      return [
        {
          selectAll: "Select All Projects",
          projects: this.$store.getters["project/PROJECT_LIST_FOR_DROPDOWN"],
        },
      ];
    },
    reportType() {
      return this.reportTypes.filter((v) => {
        if (v.url) {
          return v;
        }
      });
    },
    allDrivers() {
      return [
        {
          selectAll: "Select All Drivers",
          drivers: this.$store.state.reports.allDrivers,
        },
      ];
    },
    allVehicles() {
      return [
        {
          selectAll: "Select All Vehicles",
          vehicles: this.$store.state.reports.allVehicles,
        },
      ];
    },
    reportData() {
      return this.$store.getters["reports/GET_REPORT_DATA"];
    },
    Headers() {
      return this.$store.getters["reports/GET_HEADERS"];
    },
  },
  methods: {
    reSetColumn() {
      if (this.$refs.select) {
        this.$refs.select.blur();
      }
      if (this.$refs.expenses_Category) {
        this.$refs.expenses_Category.blur();
      }
    },
    autoSizeAll() {
      let timer = setTimeout(() => {
        let allColumnIds = [];
        this.gridOptions.columnApi.getAllColumns().forEach(function (column) {
          allColumnIds.push(column.colId);
        });
        this.gridOptions.columnApi.autoSizeColumns(allColumnIds);
      }, 1000);
    },
    updateReportType(reportType) {
      this.$nextTick(() => {
        this.filter = {
          start_date: null,
          end_date: null,
        };
        this.selectedReoprt = reportType;
        this.$store.commit("reports/EMPTY_REPORT_DATA");
        this.$store.commit("reports/EMPTY_VEHICLE_DATA");
        this.$store.commit("reports/EMPTY_DRIVER_DATA");
      });
    },
    dateValidator() {
      if (
        this.filter.start_date &&
        this.filter.end_date &&
        this.filter.start_date > this.filter.end_date
      ) {
        let _ = this.filter.end_date;
        this.filter.end_date = this.filter.start_date;
        this.filter.start_date = _;
      }
    },
    getDriverVehicleData(value) {
      if (
        Object.keys(this.selectedReoprt) === 0 &&
        this.selectedReoprt.constructor === Object &&
        this.selectedReoprt == null &&
        this.selectedReoprt != "order"
      ) {
        this.$notifier.showMessage({
          content: "Please select Report type first",
          color: "error",
        });
        this.filter.project = [];
      } else {
        let params = {};
        if (this.filter.project && this.filter.project.length != 0) {
          this.disabled = true;
          params.project__project_id = this.filter.project
            .map((project) => {
              return project.value;
            })
            .toString();
          if (
            this.selectedReoprt.category == "driver" ||
            this.selectedReoprt.category == "trip"
          ) {
            this.$store
              .dispatch("reports/GET_ALL_DRIVERS", params)
              .then((result) => {
                this.disabled = false;
              })
              .catch((err) => {
                if (err.message) {
                  this.$notifier.showMessage({
                    content: err.message,
                    color: "error",
                  });
                } else {
                  this.$notifier.showMessage({
                    content: "Error Fetching data!",
                    color: "error",
                  });
                }
              });
          }
          if (
            this.selectedReoprt.category == "vehicle" ||
            this.selectedReoprt.category == "trip"
          ) {
            this.disabled = true;
            params.project_id = this.filter.project
              .map((project) => {
                return project.value;
              })
              .toString();
            this.$store
              .dispatch("reports/GET_ALL_VEHICLES", params)
              .then((result) => {
                this.disabled = false;
              })
              .catch((err) => {
                if (err.message) {
                  this.$notifier.showMessage({
                    content: err.message,
                    color: "error",
                  });
                } else {
                  this.$notifier.showMessage({
                    content: "Error Fetching data!",
                    color: "error",
                  });
                }
              });
          }
        }
      }
    },
    generateFilters() {
      let filters = {};
      for (const key in this.filter) {
        if (
          this.filter[key] == null ||
          this.filter[key] == undefined ||
          (typeof this.filter[key] == typeof "" &&
            this.filter[key].trim() == "")
        ) {
          delete this.filter[key];
        } else {
          if (Array.isArray(this.filter[key])) {
            if (this.filter[key].length) {
              if (key == "type" || key == "driver" || key == "vehicle") {
                let _ = this.filter[key]
                  .map((obj) => {
                    return obj.id;
                  })
                  .toString();
                delete filters.type;
                if (this.selectedReoprt.category == "driver" && key == "type") {
                  filters.driver = _;
                  filters.vehicle ? delete filters.vehicle : false;
                } else if (
                  this.selectedReoprt.category == "vehicle" &&
                  key == "type"
                ) {
                  filters.vehicle = _;
                  filters.driver ? delete filters.driver : false;
                } else {
                  filters[key] = _;
                }
              } else if (key == "project") {
                filters.project_id = this.filter[key]
                  .map((project) => {
                    return project.value;
                  })
                  .toString();
              } else {
                filters[key] = this.filter[key].toString();
              }
            } else {
              delete this.filter[key];
            }
          } else {
            filters[key] = this.filter[key];
          }
          delete filters.type;
        }
      }
      return filters;
    },
    getReportData() {
      if (
        this.filter.start_date &&
        this.filter.end_date &&
        Object.keys(this.selectedReoprt).length !== 0
      ) {
        let filters = this.generateFilters();
        this.$store
          .dispatch("reports/GET_REPORT_DATA", {
            url: this.selectedReoprt.url,
            params: filters,
          })
          .then((result) => {
            this.firtsRequest = false;
            this.panel = false;
            if (
              this.selectedReoprt.category == "order" ||
              this.selectedReoprt.category == "trip"
            ) {
              this.autoSizeAll();
            }
          })
          .catch((err) => {
            if (err.status == 500) {
              this.$notifier.showMessage({
                content: "Error Fetching Data",
                color: "error",
              });
            }
          });
      } else {
        this.$notifier.showMessage({
          content: "Select Dates & Report type first!",
        });
      }
    },
    downloadReportData() {
      if (
        this.$store.state.reports.reportData &&
        this.$store.state.reports.reportData.length
      ) {
        let excelData = XLSX.utils.aoa_to_sheet(
          this.$store.state.reports.reportData
        );
        var wb = XLSX.utils.book_new();
        wb.Props = {
          Title: this.selectedReoprt.title,
          CreatedDate: new Date(),
        };

        wb.SheetNames.push(`Sheet 1`);

        wb.Sheets[`Sheet 1`] = excelData;

        var wbout = XLSX.write(wb, { bookType: "xls", type: "binary" });

        let blob = new Blob([this.s2ab(wbout)], {
          type: "application/octet-stream",
        });
        downloadBlobData(blob, this.selectedReoprt.title);
      }
    },
    s2ab(s) {
      var buf = new ArrayBuffer(s.length);
      var view = new Uint8Array(buf);
      for (var i = 0; i < s.length; i++) view[i] = s.charCodeAt(i) & 0xff;
      return buf;
    },
  },
  mounted() {
    this.projectMounted = true;
  },
  beforeDestroy() {
    this.$store.commit("reports/EMPTY_REPORT_DATA");
    this.$store.commit("reports/EMPTY_VEHICLE_DATA");
    this.$store.commit("reports/EMPTY_DRIVER_DATA");
  },
};
</script>

<style lang="scss" scoped>
.on-hover {
  &:hover {
    box-shadow: 2px 2px 10px -5px rgb(0 0 0 / 20%);
  }
}
</style>
