<template>
  <div class="pa-6">
    <v-row no-gutters class="pb-6">
      <v-col cols="6">
        <span class="text-h5 text-uppercase font-weight-bold"> Statuses </span>
      </v-col>
      <v-col cols="6" class="text-right">
        <v-btn small depressed class="primary" @click="addStatus()">
          <v-icon small class="mr-1">mdi-plus</v-icon>
          <span>Add Status</span>
        </v-btn>
      </v-col>
    </v-row>
    <v-row no-gutters class="pb-6">
      <v-col cols="3">
        <v-text-field
          color="light_black"
          prepend-inner-icon="mdi-magnify"
          clearable
          placeholder="Search here.."
          dense
          v-model="searching_status"
          @input="getStatusListSearching()"
          outlined
          hide-details
        ></v-text-field>
      </v-col>
    </v-row>
    <v-row no-gutters>
      <v-col cols="12" lg="5">
        <v-tabs
          v-model="statusTab"
          color="primary"
          primary
          slider-color="primary"
        >
          <v-tab> Order </v-tab>
          <!-- <v-tab> Trip </v-tab>
          <v-tab> Driver </v-tab>
          <v-tab> Vehicle </v-tab> -->
        </v-tabs>
      </v-col>

      <v-col cols="12" class="pt-4">
        <AgGridVue
          @grid-ready="gridReady"
          :grid-options="gridOptions"
          :column-defs="columnDefs"
          :default-col-def="defaultColDef"
          :row-data="
            statusTab === 0
              ? orderStatusList
              : statusTab === 1
              ? tripStatusList
              : statusTab === 2
              ? driverStatusList
              : statusTab === 3
              ? vehicleStatusList
              : []
          "
          :style="{ width: '100%', height: gridHeight }"
          class="ag-theme-material cf-table"
        >
        </AgGridVue>
      </v-col>
    </v-row>
    <StatusStatusform v-model="openStatusForm" :formType="formType" />
  </div>
</template>


<script>
import { AgGridVue } from "ag-grid-vue";
import statusButton from "~/components/common/aggrid/buttons/statusButton.vue";

export default {
  components: {
    AgGridVue,
    statusButton,
  },
  data() {
    return {
      formType: "add",
      defaultColDef: {
        lockPosition: true,
      },
      openStatusForm: false,
      statusTab: null,
      searching_status: null,
      columnDefs: [
        {
          headerName: "Status Name",
          pinned: "left",
          field: "name",
          width: 100,
        },
        {
          headerName: "Description",
          field: "description",
        },
        {
          headerName: "Status Type",
          field: "keyword",
          width: 50,
          cellRenderer: (params) => {
            return params.value == "successful"
              ? "Delivered"
              : params.value == "failed"
              ? "Returned"
              : params.value;
          },
        },
        {
          headerName: "Actions",
          width: 170,
          maxWidth: 170,
          field: "actions",
          pinned: "right",
          cellRendererFramework: "statusButton",
        },
      ],
      gridApi: null,
      columnApi: null,
      gridOptions: {
        onGridSizeChanged: () => {
          this.gridOptions.api.sizeColumnsToFit();
        },
        pagination: true,
        paginationPageSize: 20,
        headerHeight: 40,
        rowHeight: 40,
        suppressRowClickSelection: true,
        enableCellTextSelection: true,
      },
    };
  },
  computed: {
    gridHeight() {
      return `${window.innerHeight - 296}px`;
    },
    orderStatusList() {
      if (this.$store.state.status.statusList) {
        return this.$store.state.status.statusList.filter(
          (v) => v.status_category == "order"
        );
      } else {
        return [];
      }
    },
    driverStatusList() {
      if (this.$store.state.status.statusList) {
        return this.$store.state.status.statusList.filter(
          (v) => v.status_category == "driver"
        );
      } else {
        return [];
      }
    },
    tripStatusList() {
      if (this.$store.state.status.statusList) {
        return this.$store.state.status.statusList.filter(
          (v) => v.status_category == "trip"
        );
      } else {
        return [];
      }
    },
    vehicleStatusList() {
      if (this.$store.state.status.statusList) {
        return this.$store.state.status.statusList.filter(
          (v) => v.status_category == "vehicle"
        );
      } else {
        return [];
      }
    },
  },
  methods: {
    addStatus() {
      this.formType = "add";
      this.openStatusForm = true;
    },
    editStatus(id) {
      this.$store
        .dispatch("status/GET_STATUS_DETAIL", id)
        .then((response) => {
          this.formType = "edit";
          this.openStatusForm = true;
        })
        .catch((error) => {
          this.$notifier.showMessage({
            content: "Couln't fetch data",
            color: "error",
          });
        });
    },
    deleteStatus(id) {
      this.$store
        .dispatch("status/DELETE_STATUS", id)
        .then((response) => {
          this.$notifier.showMessage({
            content: "Status Deleted successfully",
            color: "error",
          });
        })
        .catch((error) => {
          this.$notifier.showMessage({
            content: "Couln't fetch data",
            color: "error",
          });
        });
    },
    gridReady(params) {
      this.gridApi = params.api;
      this.columnApi = params.columnApi;
    },
    getStatusListSearching() {
      this.gridOptions.api.setQuickFilter(this.searching_status);
    },
    getStatusList() {
      this.$store.dispatch("status/GET_ALL_STATUS");
    },
  },
  beforeMount() {
    this.getStatusList();
  },
};
</script>
