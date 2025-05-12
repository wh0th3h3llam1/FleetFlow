<template>
  <v-dialog
    v-model="orderItemListDialog"
    persistent
    scrollable
    max-width="70%"
    @keydown.esc="closeDialog()"
  >
    <v-card class="pa-6">
      <v-card-title class="mb-4">
        <span
          class="
            text-lg-subtitle-1 text-xl-h6 text-uppercase
            font-weight-black
            primary--text
          "
          >Order Item List</span
        >
        <v-spacer />
        <v-btn
          depressed
          text
          small
          icon
          class="primary-text"
          @click="closeDialog()"
        >
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="8"> </v-col>
          <v-col cols="4" class="mt-0 mb-4 pt-5">
            <v-text-field
              outlined
              hide-details
              dense
              label="Search Items Here.."
              v-model="search"
            ></v-text-field>
          </v-col>
        </v-row>
        <AgGridVue
          @grid-ready="gridReady"
          :grid-options="gridOptions"
          :column-defs="columnDefs"
          :default-col-def="defaultColDef"
          :row-data="orderItemList"
          style="width: 100%; height: 450px"
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
      defaultColDef: {
        lockPosition: true,
      },
      gridApi: null,
      columnApi: null,
      gridOptions: {
        onGridSizeChanged: () => {
          this.gridOptions.api.sizeColumnsToFit();
        },
        headerHeight: 40,
        rowHeight: 40,
        rowSelection: "multiple",
        suppressRowClickSelection: true,
        suppressDragLeaveHidesColumns: true,
        enableCellTextSelection: true,
      },
    };
  },
  computed: {
    orderItemListDialog: {
      get() {
        return this.value;
      },
      set(value) {
        this.$emit("input", value);
      },
    },
    orderItemList() {
      if (this.search.length > 0) {
        return this.$store.state.order.orderDetailStore.orderItems.filter(
          (item) => {
            return item.item.toLowerCase().indexOf(this.search) > -1;
          }
        );
      } else {
        return this.$store.state.order.orderDetailStore.orderItems;
      }
    },
    columnDefs() {
      if (
        this.$store.state.order.orderDetailStore.order.status ==
          "partially_delivered" ||
        this.$store.state.order.orderDetailStore.order.status == "failed" ||
        this.$store.state.order.orderDetailStore.order.status == "successful"
      ) {
        return [
          {
            headerName: "Item",
            width: 170,
            field: "item",
          },
          {
            headerName: "Storage Type",
            width: 60,
            field: "storage_type",
          },
          {
            headerName: "Unit",
            width: 60,
            field: "item_unit",
          },
          {
            headerName: "Total delivered Item ",
            width: 60,
            field: "delivered_quantity",
          },
          {
            headerName: "Total Quantity",
            width: 60,
            field: "original_quantity",
          },
        ];
      } else {
        return [
          {
            headerName: "Item",
            width: 170,
            field: "item",
          },
          {
            headerName: "Storage Type",
            width: 60,
            field: "storage_type",
          },
          {
            headerName: "Unit",
            width: 60,
            field: "item_unit",
          },
          {
            headerName: "Total Quantity ",
            width: 60,
            field: "original_quantity",
          },
        ];
      }
    },
  },
  methods: {
    gridReady(params) {
      this.gridApi = params.api;
      this.columnApi = params.columnApi;
    },
    closeDialog() {
      this.orderItemListDialog = false;
    },
  },
  beforeDestroy() {
    this.$store.commit("order/orderDetailStore/SET_ORDER_ITEM_DETAILS", []);
  },
};
</script>