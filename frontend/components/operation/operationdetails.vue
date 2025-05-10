<template>
  <div class="full-height">
    <v-row no-gutters class="px-4 pt-4">
      <v-col cols="6" class="px-4 pb-4">
        <span
          v-if="selectedDriver == null"
          class="font-weight-bold text-h6 text-uppercase text-grey"
        >
          Overview
        </span>
        <span v-else class="font-weight-bold text-h6 text-uppercase text-grey">
          {{ selectedDriver.driver_name }}
        </span>
      </v-col>
      <v-col cols="6" class="pb-4 d-flex justify-end">
        <v-btn
          small
          v-if="selectedDriver != null"
          class="elevation-0 ma-1 primary"
          @click="clearSelection"
        >
          <v-icon small class="mr-1"> mdi-map-marker-path </v-icon>
          <span>View All</span>
        </v-btn>
        <v-btn
          small
          class="elevation-0 ma-1 primary"
          @click="viewMap = !viewMap"
        >
          <v-icon v-if="!viewMap" small class="mr-1">
            mdi-map-marker-path
          </v-icon>
          <v-icon v-else small class="mr-1">mdi-table</v-icon>
          <span v-if="!viewMap">View map</span>
          <span v-else>View table</span>
        </v-btn>
      </v-col>
      <v-col class="bottom-devider-shadow" cols="12" v-if="!viewMap">
        <v-tabs
          :slider-color="getColor(activeTab)"
          v-model="activeTab"
          height="70"
        >
          <v-tab>
            <v-card class="elevation-0 background-transparent">
              <v-card-title
                class="font-weight-black text-md-h6 d-flex justify-center"
                :class="activeTab == 0 ? 'text-' + getColor(activeTab) : null"
                >{{ assignedOrders.length }}</v-card-title
              >
              <v-card-subtitle>Assigned</v-card-subtitle>
            </v-card>
          </v-tab>
          <v-tab>
            <v-card class="elevation-0 background-transparent">
              <v-card-title
                class="font-weight-black text-md-h6 d-flex justify-center"
                :class="activeTab == 1 ? 'text-' + getColor(activeTab) : null"
                >{{ pickedupOrders.length }}</v-card-title
              >
              <v-card-subtitle>Shipped</v-card-subtitle>
            </v-card>
          </v-tab>
          <v-tab>
            <v-card class="elevation-0 background-transparent">
              <v-card-title
                class="font-weight-black text-md-h6 d-flex justify-center"
                :class="activeTab == 2 ? 'text-' + getColor(activeTab) : null"
                >{{ partiallyDeliveredOrders.length }}</v-card-title
              >
              <v-card-subtitle>Partially Delivered</v-card-subtitle>
            </v-card>
          </v-tab>
          <v-tab>
            <v-card class="elevation-0 background-transparent">
              <v-card-title
                class="font-weight-black text-md-h6 d-flex justify-center"
                :class="activeTab == 3 ? 'text-' + getColor(activeTab) : null"
                >{{ successfulOrders.length }}</v-card-title
              >
              <v-card-subtitle>Delivered</v-card-subtitle>
            </v-card>
          </v-tab>
          <v-tab>
            <v-card class="elevation-0 background-transparent">
              <v-card-title
                class="font-weight-black text-md-h6 d-flex justify-center"
                :class="activeTab == 4 ? 'text-' + getColor(activeTab) : null"
                >{{ failedOrders.length }}</v-card-title
              >
              <v-card-subtitle>Returned</v-card-subtitle>
            </v-card>
          </v-tab>
        </v-tabs>
      </v-col>
      <v-col cols="12" v-if="viewMap && selectedDriver !== null">
        <v-row no-gutters class="px-2 pb-4">
          <v-col cols="4" class="pr-2">
            <div
              class="
                border-x-light_grey
                border-y-light_grey
                full-width
                background-white
                rounded-lg
              "
            >
              <div
                class="
                  pa-2
                  background-light_grey
                  d-flex
                  justify-center
                  rounded-t-lg
                "
              >
                <span class="text-lg-body-2 font-weight-bold">
                  Driver Details
                </span>
              </div>
              <div class="pa-2">
                <v-row no-gutters>
                  <v-col cols="6" class="text-caption"> Contact Number </v-col>
                  <v-col cols="6" class="text-caption d-flex justify-end">
                    <b>{{ selectedDriver.contact_number }}</b>
                  </v-col>
                </v-row>
                <v-row no-gutters v-if="selectedDriversTripDetails">
                  <v-col cols="6" class="text-caption"> Trip Status </v-col>
                  <v-col cols="6" class="text-caption d-flex justify-end">
                    <b>{{ selectedDriversTripDetails.status }}</b>
                  </v-col>
                </v-row>
                <v-row no-gutters v-if="selectedDriversTripDetails">
                  <v-col cols="6" class="text-caption"> Trip Date </v-col>
                  <v-col cols="6" class="text-caption d-flex justify-end">
                    <b>{{ selectedDriversTripDetails.trip_date }}</b>
                  </v-col>
                </v-row>
                <v-row no-gutters>
                  <v-col cols="6" class="text-caption"> Vehicle </v-col>
                  <v-col cols="6" class="text-caption d-flex justify-end">
                    <b>{{ selectedDriver.vehicle }}</b>
                  </v-col>
                </v-row>
              </div>
            </div>
          </v-col>
          <v-col
            cols="4"
            class="px-2"
            v-if="
              selectedDriversTripDetails &&
              selectedDriversTripDetails.order_count
            "
          >
            <div
              class="
                border-x-light_grey
                border-y-light_grey
                full-width
                background-white
                rounded-lg
              "
            >
              <div
                class="
                  pa-2
                  background-light_grey
                  d-flex
                  justify-center
                  rounded-t-lg
                "
              >
                <span class="text-lg-body-2 font-weight-bold">
                  Order Statistics
                </span>
              </div>
              <div class="pa-2">
                <v-row no-gutters>
                  <v-col cols="9" class="text-caption"> Total Orders </v-col>
                  <v-col cols="3" class="text-caption d-flex justify-end">
                    <b>{{ selectedDriversTripDetails.order_count.total }}</b>
                  </v-col>
                </v-row>
                <v-row no-gutters>
                  <v-col cols="9" class="text-caption">
                    Delivered Orders
                  </v-col>
                  <v-col cols="3" class="text-caption d-flex justify-end">
                    <b>{{
                      selectedDriversTripDetails.order_count.successful
                    }}</b>
                  </v-col>
                </v-row>
                <v-row no-gutters>
                  <v-col cols="9" class="text-caption">
                    Partially Delivered
                  </v-col>
                  <v-col cols="3" class="text-caption d-flex justify-end">
                    <b>{{
                      selectedDriversTripDetails.order_count.partially_delivered
                    }}</b>
                  </v-col>
                </v-row>
                <v-row no-gutters>
                  <v-col cols="9" class="text-caption"> Returned Orders </v-col>
                  <v-col cols="3" class="text-caption d-flex justify-end">
                    <b>{{ selectedDriversTripDetails.order_count.failed }}</b>
                  </v-col>
                </v-row>
                <v-row no-gutters>
                  <v-col cols="9" class="text-caption">
                    Unattempted Orders
                  </v-col>
                  <v-col cols="3" class="text-caption d-flex justify-end">
                    <b>{{
                      selectedDriversTripDetails.order_count.unattempted
                    }}</b>
                  </v-col>
                </v-row>
              </div>
            </div>
          </v-col>
          <v-col
            cols="4"
            class="pl-2"
            v-if="
              selectedDriversTripDetails &&
              selectedDriversTripDetails.partitions
            "
          >
            <div
              class="
                border-x-light_grey
                border-y-light_grey
                full-width
                background-white
                rounded-lg
              "
            >
              <div
                class="
                  pa-2
                  background-light_grey
                  d-flex
                  justify-center
                  rounded-t-lg
                "
              >
                <span class="text-lg-body-2 font-weight-bold">
                  Vehicle Statistics
                </span>
              </div>
              <div class="pa-2">
                <v-row no-gutters>
                  <v-col cols="7" class="text-caption d-flex align-center">
                    <v-icon color="light_orange" small
                      >mdi-white-balance-sunny</v-icon
                    >
                    <span>&nbsp;Dry</span>
                  </v-col>
                  <v-col cols="5" class="text-caption d-flex justify-end">
                    <b>{{ selectedDriversTripDetails.partitions.dry }}%</b>
                  </v-col>
                </v-row>
                <v-row no-gutters>
                  <v-col cols="7" class="text-caption d-flex align-center">
                    <v-icon color="light_red" small>mdi-ice-pop</v-icon>
                    <span>&nbsp;Chilled</span>
                  </v-col>
                  <v-col cols="5" class="text-caption d-flex justify-end">
                    <b>{{ selectedDriversTripDetails.partitions.chilled }}%</b>
                  </v-col>
                </v-row>
                <v-row no-gutters>
                  <v-col cols="7" class="text-caption d-flex align-center">
                    <v-icon color="blue" small>mdi-snowflake</v-icon>
                    <span>&nbsp;Frozen</span>
                  </v-col>
                  <v-col cols="5" class="text-caption d-flex justify-end">
                    <b>{{ selectedDriversTripDetails.partitions.chilled }}%</b>
                  </v-col>
                </v-row>
                <v-row no-gutters>
                  <v-col cols="7" class="text-caption d-flex align-center">
                    <v-icon color="grey" small
                      >mdi-checkbox-blank-off-outline</v-icon
                    >
                    <span>&nbsp;Unused</span>
                  </v-col>
                  <v-col cols="5" class="text-caption d-flex justify-end">
                    <b>{{ selectedDriversTripDetails.partitions.unused }}%</b>
                  </v-col>
                </v-row>
              </div>
            </div>
          </v-col>
        </v-row>
      </v-col>
      <v-col cols="4" class="pl-3 pt-4 pb-2" v-show="!viewMap">
        <v-text-field
          prepend-inner-icon="mdi-magnify"
          label="Search Orders.."
          hide-details="auto"
          v-model="search"
          outlined
          dense
          clearable
        ></v-text-field>
      </v-col>
      <v-col cols="4" class="px-3 pt-4 pb-2" v-show="!viewMap">
        <v-select
          single-line
          multiple
          outlined
          dense
          ref="select"
          hide-details="auto"
          :value="tableSelectedHeader"
          :items="headersToShow"
          :animateRows="true"
          label="Choose Columns to show"
          item-text="headerName"
          item-value="field"
          @change="changeHeadersToshow"
          :menu-props="{ offsetY: true }"
        >
          <template v-slot:selection="{ index }">
            <span v-if="index === 0">
              {{ selectedHeaders }} Column Selected
            </span>
          </template>
        </v-select>
      </v-col>
      <v-col cols="12" class="pa-3" v-show="!viewMap">
        <AgGridVue
          @grid-ready="gridReady"
          :context="context"
          :grid-options="gridOptions"
          :column-defs="columnDefs"
          :default-col-def="defaultColDef"
          :row-data="
            activeTab == 0
              ? assignedOrders
              : activeTab == 1
              ? pickedupOrders
              : activeTab == 2
              ? partiallyDeliveredOrders
              : activeTab == 3
              ? successfulOrders
              : activeTab == 4
              ? failedOrders
              : []
          "
          :style="{ width: '100%', height: gridHeight }"
          class="ag-theme-material"
        >
        </AgGridVue>
      </v-col>
    </v-row>
    <v-row no-gutters>
      <v-col cols="12" v-show="viewMap" class="position-relative">
        <CommonGmap
          mapWidth="100%"
          :mapHeight="mapHeight"
          ref="operationsViewTrip"
          :clusterMarkers="true"
          @selectDriver="selectDriver"
        />
        <CommonMapinfo :legends="legends" />
      </v-col>
    </v-row>
    <OperationOrdedetailsdialog v-model="showOrderDetails" />
  </div>
</template>

<script>
import {
  WarehouseIcon,
  OrderAssignedIcon,
  OrderUnassignedIcon,
  OrderPickupIcon,
  OrderSuccessfulIcon,
  OrderFailedIcon,
  OrderCancelledIcon,
  OrderEnrouteIcon,
} from "~/static/mapIcons/icons";

import { AgGridVue } from "ag-grid-vue";
import operationViewButton from "~/components/common/aggrid/buttons/orderOperationButton";

export default {
  components: {
    AgGridVue,
    operationViewButton,
  },
  props: {
    selected_driver: {
      required: false,
      default: null,
    },
  },
  data() {
    return {
      context: { parentComponent: this },
      legends: [
        { text: "Warehouse", marker: WarehouseIcon },
        { text: "Unassigned", marker: OrderUnassignedIcon },
        { text: "Assigned", marker: OrderAssignedIcon },
        { text: "Shipped", marker: OrderPickupIcon },
        { text: "Delivered", marker: OrderSuccessfulIcon },
        { text: "Returned", marker: OrderFailedIcon },
        { text: "Cancelled", marker: OrderCancelledIcon },
        { text: "Partially Delivered", marker: OrderEnrouteIcon },
      ],
      search: null,
      filter: {},
      defaultColDef: {
        lockPosition: true,
      },
      tableSelectedHeader: [
        "reference_number",
        "address",
        "driver_name",
        "contact_number",
        "customer_name",
        "no_of_items",
        "order_type",
        "project_name",
        "updated_on",
        "status_keyword",
      ],
      viewMap: true,
      selectColumnDefs: [],
      gridApi: null,
      selectedHeaders: 11,
      columnApi: null,
      activeTab: 0,
      gridOptions: {
        pagination: true,
        paginationPageSize: 20,
        headerHeight: 40,
        rowHeight: 40,
        suppressRowClickSelection: true,
        suppressDragLeaveHidesColumns: true,
        enableCellTextSelection: true,
      },
      showOrderDetails: false,
    };
  },
  computed: {
    mapHeight() {
      if (this.selected_driver) {
        return `${window.innerHeight - 282}px`;
      } else {
        return `${window.innerHeight - 132}px`;
      }
    },
    gridHeight() {
      return `${window.innerHeight - 290}px`;
    },
    headersToShow() {
      return this.columnDefs.filter((header) => header.field != "action");
    },
    selectedDriversTripDetails() {
      return this.$store.state.operation.selectedDriversTripDetails;
    },
    selectedDriver: {
      get() {
        return this.selected_driver;
      },
      set(value) {
        this.$emit("selectedDriverChanged", value);
      },
    },
    allOrders() {
      if (this.search && this.search.trim().length > 0) {
        return this.$store.state.operation.orders.filter((order) => {
          return (
            (order.driver_name &&
              order.driver_name
                .toLowerCase()
                .indexOf(this.search.toLowerCase()) > -1) ||
            (order.contact_person &&
              order.contact_person
                .toLowerCase()
                .indexOf(this.search.toLowerCase()) > -1) ||
            (order.customer_name &&
              order.customer_name
                .toLowerCase()
                .indexOf(this.search.toLowerCase()) > -1) ||
            (order.address &&
              order.address.toLowerCase().indexOf(this.search.toLowerCase()) >
                -1) ||
            (order.project_name &&
              order.project_name
                .toLowerCase()
                .indexOf(this.search.toLowerCase()) > -1) ||
            (order.reference_number &&
              order.reference_number
                .toLowerCase()
                .indexOf(this.search.toLowerCase()) > -1)
          );
        });
      } else {
        return this.$store.state.operation.orders;
      }
    },
    assignedOrders() {
      return this.allOrders.filter((order) => {
        return order.status.toLowerCase().replace(/\ /g, "_") == "assigned";
      });
    },
    partiallyDeliveredOrders() {
      return this.allOrders.filter((order) => {
        return (
          order.status.toLowerCase().replace(/\ /g, "_") ==
          "partially_delivered"
        );
      });
    },
    pickedupOrders() {
      return this.allOrders.filter((order) => {
        return order.status.toLowerCase().replace(/\ /g, "_") == "pickedup";
      });
    },
    successfulOrders() {
      return this.allOrders.filter((order) => {
        return order.status.toLowerCase().replace(/\ /g, "_") == "successful";
      });
    },
    failedOrders() {
      return this.allOrders.filter((order) => {
        return order.status.toLowerCase().replace(/\ /g, "_") == "failed";
      });
    },
    height() {
      return ((window.innerHeight / 100) * 60).toFixed() + "px";
    },
    columnDefs() {
      const headers = [
        {
          headerName: "Action",
          field: "action",
          cellRendererFramework: "operationViewButton",
          width: 90,
          pinned: "left",
        },
        {
          headerName: "Order Reference",
          field: "reference_number",
          width: 170,
          sortable: true,
        },
        {
          headerName: "No. Of Items",
          field: "no_of_items",
        },
        {
          headerName: "Order Type",
          field: "order_type",
          width: 140,
          sortable: true,
        },
        {
          headerName: "Address",
          field: "address",
          width: 135,
          sortable: true,
        },
        {
          headerName: "Driver Name",
          field: "driver_name",
        },
        {
          headerName: "Contact Number",
          field: "contact_number",
          width: 175,
          sortable: true,
        },
        {
          headerName: "Customer",
          field: "customer_name",
          width: 175,
          sortable: true,
        },
        {
          headerName: "Project",
          field: "project_name",
        },
        {
          headerName: "Updated On",
          field: "updated_on",
        },
      ];
      if (this.activeTab == 2 || this.activeTab == 4) {
        headers.push({
          headerName: "Status Keyword",
          field: "status_keyword",
        });
      }

      return headers;
    },
  },
  methods: {
    changeHeadersToshow(e) {
      this.headersToShow.forEach((header) => {
        if (e.indexOf(header.field) > -1 || e.length == 0) {
          this.columnApi.setColumnVisible(header.field, true);
          this.selectedHeaders = e.length;
        } else {
          this.columnApi.setColumnVisible(header.field, false);
        }
      });
      this.tableSelectedHeader = e;
      localStorage.setItem("operation_columns", JSON.stringify(e));
    },
    getSelectedColumn() {
      this.tableSelectedHeader =
        JSON.parse(localStorage.getItem("operation_columns")) != null
          ? JSON.parse(localStorage.getItem("operation_columns"))
          : this.tableSelectedHeader;
    },
    clearSelection() {
      this.selectedDriver = null;
    },
    get_order_details(id) {
      this.$store
        .dispatch("order/orderDetailStore/GET_ORDER_DETAILS", id)
        .then((result) => {
          this.showOrderDetails = true;
        })
        .catch((err) => {});
    },
    selectDriver(driver) {
      this.selectedDriver = driver;
    },
    setMapData(mapData, mapFor) {
      if (mapData !== null) {
        let interval = setInterval(() => {
          if (this.$refs.operationsViewTrip) {
            clearInterval(interval);

            if (mapFor == "drivers") {
              this.$refs.operationsViewTrip.clearMarker();
              this.$refs.operationsViewTrip.clearGeoJson();
              this.$refs.operationsViewTrip.initMap();
              this.$refs.operationsViewTrip.loadDrivers(mapData);
            } else {
              this.$refs.operationsViewTrip.clearMarker();
              this.$refs.operationsViewTrip.clearGeoJson();
              this.$refs.operationsViewTrip.initMap();
              this.$refs.operationsViewTrip.loadRoutes(
                mapData.trip_route,
                mapData.order_details,
                mapData.warehouse_details,
                this.selectedDriver
              );
            }
          }
        }, 100);
      } else {
        this.$refs.operationsViewTrip.clearMarker();
        this.$refs.operationsViewTrip.clearGeoJson();
        this.$refs.operationsViewTrip.initMap();
      }
    },
    gridReady(params) {
      this.gridApi = params.api;
      this.columnApi = params.columnApi;
      this.getSelectedColumn();
      this.setSelectedColumn();
    },
    getColor(status) {
      switch (status) {
        case 0:
          return "assigned";
        case 1:
          return "pickedup";
        case 2:
          return "partially_delivered";
        case 3:
          return "successful";
        case 4:
          return "failed";

        default:
          return "primary";
      }
    },
    setSelectedColumn() {
      this.headersToShow.forEach((header) => {
        if (this.tableSelectedHeader.includes(header.field)) {
          this.columnApi.setColumnVisible(header.field, true);
        } else {
          this.columnApi.setColumnVisible(header.field, false);
        }
      });
      this.selectedHeaders = this.tableSelectedHeader.length;
      this.gridOptions.api.sizeColumnsToFit();
    },
  },
  mounted() {
    this.getSelectedColumn();
  },
};
</script>

<style>
</style>
