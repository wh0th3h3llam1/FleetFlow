<template>
  <v-dialog
    v-model="tripOrdersListDialog"
    persistent
    scrollable
    max-width="90%"
    transition="dialog-bottom-transition"
    @keydown.esc="closeDialog()"
  >
    <v-card class="pa-6">
      <v-card-title>
        <span
          class="
            text-lg-subtitle-1 text-xl-h6 text-uppercase
            font-weight-black
            primary--text
          "
          >Trip's Orders List</span
        >
        <v-spacer />
        <v-btn
          depressed
          text
          small
          icon
          class="primary-text mt-n2"
          @click="closeDialog()"
        >
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>
      <v-card-text>
        <v-row class="pt-3 pb-6">
          <v-col cols="8"> </v-col>
          <v-col cols="4">
            <v-text-field
              outlined
              hide-details
              dense
              label="Search Orders Here.."
              v-model="search"
              @input="getOrderListSearching()"
            ></v-text-field>
          </v-col>
        </v-row>
        <AgGridVue
          @grid-ready="gridReady"
          :grid-options="gridOptions"
          :column-defs="columnDefs"
          :row-data="tripOrdersList"
          style="width: 100%; height: 350px"
          class="ag-theme-material cf-table"
        >
        </AgGridVue>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
import { AgGridVue } from "ag-grid-vue";

export default {
  props: {
    value: Boolean,
  },
  components: {
    AgGridVue,
  },
  data() {
    return {
      search: "",
      gridApi: null,
      columnApi: null,
      gridOptions: {
        onGridSizeChanged: () => {},
        headerHeight: 40,
        rowHeight: 40,
        rowSelection: "multiple",
        suppressRowClickSelection: true,
        enableCellTextSelection: true,
      },
    };
  },
  watch: {
    tripOrdersListDialog(val) {
      if (val) {
        setTimeout(() => {
          this.autoSizeAll();
        }, 1000);
      }
    },
  },
  computed: {
    columnDefs() {
      if (this.$store.state.trip.currentTrip.status == "scheduled") {
        return [
          {
            headerName: "Reference Number",
            headerTooltip: "Reference Number",
            field: "reference_number",
          },
          {
            headerName: "Customer Name",
            field: "customer_name",
          },
          {
            headerName: "Customer Contact No.",
            field: "contact_number",
          },
          {
            headerName: "Invoice number",
            field: "invoice_number",
          },
          {
            headerName: "Order Status",
            field: "status",
          },
          {
            headerName: "Dry",
            field: "total_dry_items",
          },
          {
            headerName: "Frozen",
            field: "total_frozen_items",
          },
          {
            headerName: "Chilled",
            field: "total_chilled_items",
          },
          {
            headerName: "Total Items",
            field: "no_of_items",
          },
          {
            headerName: "Planned processing time",
            field: "planned_processing_time",
          },
        ];
      } else {
        return [
          {
            headerName: "Reference Number",
            headerTooltip: "Reference Number",
            field: "reference_number",
          },
          {
            headerName: "Customer Name",
            headerTooltip: "Customer Name",
            field: "customer_name",
          },
          {
            headerName: "Customer Contact No.",
            headerTooltip: "Customer Contact No.",
            field: "contact_number",
          },
          {
            headerName: "Invoice number",
            headerTooltip: "Invoice number",
            field: "invoice_number",
          },
          {
            headerName: "Order Status",
            headerTooltip: "Order Status",
            field: "status",
            getQuickFilterText: (params) => {
              if (params.value == "failed") {
                return "Returned";
              } else if (params.value == "partially_delivered") {
                return "Partially Delivered";
              } else if (params.value == "successful") {
                return "Delivered";
              } else if (params.value == "assigned") {
                return "Assigned";
              } else if (params.value == "pickedup") {
                return "Shipped";
              } else {
                return params.value;
              }
            },
            cellRenderer: (params) => {
              if (params.value == "failed") {
                return "Returned";
              } else if (params.value == "partially_delivered") {
                return "Partially Delivered";
              } else if (params.value == "successful") {
                return "Delivered";
              } else if (params.value == "assigned") {
                return "Assigned";
              } else if (params.value == "pickedup") {
                return "Shipped";
              } else {
                return params.value;
              }
            },
          },
          {
            headerName: "Dry",
            headerTooltip: "Dry",
            field: "total_dry_items",
          },
          {
            headerName: "Frozen",
            headerTooltip: "Frozen",
            field: "total_frozen_items",
          },
          {
            headerName: "Chilled",
            headerTooltip: "Chilled",
            field: "total_chilled_items",
          },
          {
            headerName: "Total Items",
            headerTooltip: "Total Items",
            field: "no_of_items",
          },
          {
            headerName: "Delivered Item",
            headerTooltip: "Delivered Item",
            field: "total_delivered_items",
            cellRenderer: (params) => {
              if(params.data.status == 'pickedup' ){
                return "";
              }  else {
                return params.value;
              }
            },
          },
          {
            headerName: "Planned processing time",
            headerTooltip: "Planned processing time",
            field: "planned_processing_time",
          },
        ];
      }
    },
    tripOrdersListDialog: {
      get() {
        return this.value;
      },
      set(value) {
        this.$emit("input", value);
      },
    },
    tripOrdersList() {
      return this.$store.state.trip.currentTrip["trip_orders"];
    },
  },
  methods: {
    getOrderListSearching() {
      this.gridOptions.api.setQuickFilter(this.search);
    },
    autoSizeAll() {
      let allColumnIds = [];
      this.gridOptions.columnApi.getAllColumns().forEach(function (column) {
        allColumnIds.push(column.colId);
      });
      this.gridOptions.columnApi.autoSizeColumns(allColumnIds);
    },
    gridReady(params) {
      this.gridApi = params.api;
      this.columnApi = params.columnApi;
    },
    closeDialog() {
      this.tripOrdersListDialog = false;
    },
  },
};
</script>