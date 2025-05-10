<template>
  <div
    class="pa-6"
    @scroll="reSetColumn()"
    style="height: 100%; width: 100%; overflow: scroll; position: absolute"
  >
    <v-row no-gutters class="pb-6">
      <v-col cols="6">
        <span class="text-h5 text-uppercase font-weight-bold"> Vehicles </span>
      </v-col>
      <v-col
        cols="6"
        class="text-right"
        v-if="userPermissions.vehicle && userPermissions.vehicle.add"
      >
        <v-btn small depressed class="primary" @click="addTag()">
          <v-icon small class="mr-1">mdi-plus</v-icon>
          <span class="mr-2">Add Tag</span>
        </v-btn>

        <v-btn small depressed class="primary" @click="addVehicle()">
          <v-icon small class="mr-1">mdi-plus</v-icon>
          <span class="mr-2">Add Vehicle</span>
        </v-btn>
        <v-btn
          small
          depressed
          class="primary"
          @click="vehicleBulkUpload = true"
        >
          <v-icon small class="mr-1">mdi-arrow-up-bold</v-icon>
          <span>Bulk Upload</span>
        </v-btn>
        <v-btn
          small
          depressed
          class="primary"
          @click="showProjectListDialog = true"
        >
          <v-icon small class="mr-1">mdi-arrow-down-bold</v-icon>
          <span>Download All Data</span>
        </v-btn>
      </v-col>
    </v-row>

    <v-row no-gutters class="pb-2">
      <v-col cols="3" class="">
        <v-text-field
          class="mr-3"
          color="light_black"
          label="Search vehicles.."
          hide-details="auto"
          prepend-inner-icon="mdi-magnify"
          v-model="filter.search"
          outlined
          dense
          clearable
          @input="getAllVehicles()"
        ></v-text-field>
      </v-col>
      <v-col cols="3" class="d-flex justify-end align-center">
        <v-select
          class="mr-3"
          color="light_black"
          item-color="grey"
          single-line
          multiple
          outlined
          dense
          ref="select"
          hide-details="auto"
          :value="tableSelectedHeader"
          :items="headersToShow"
          label="Choose Columns to show"
          item-text="headerName"
          item-value="field"
          @change="changeHeadersToshow"
          :menu-props="{ offsetY: true }"
        >
          <template v-slot:selection="{ index }">
            <span class="text-body-2" v-if="index === 0">
              {{ tableSelectedHeader.length }} Column Selected
            </span>
          </template>
        </v-select>
      </v-col>
      <v-col cols="6" class="text-right">
        <v-btn
          depressed
          color="primary"
          class="rounded"
          @click="openVehicleFilterDialog = true"
        >
          <v-icon small class="mr-1">mdi-filter</v-icon>
          Filter
        </v-btn>
      </v-col>
    </v-row>
    <v-row no-gutters>
      <v-col cols="12" class="pt-4">
        <AgGridVue
          @grid-ready="gridReady"
          :grid-options="gridOptions"
          :column-defs="columnDefs"
          :default-col-def="defaultColDef"
          :row-data="allVehicles"
          :style="{ width: '100%', height: gridHeight }"
          class="ag-theme-material cf-table"
        >
        </AgGridVue>
      </v-col>
      <v-col cols="12" class="py-3 d-flex justify-end">
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
    <VehicleVehicleform v-model="openVehicleForm" :formType="formType" />
    <VehicleVehicletagform v-model="openVehicleTagFormDialog" />
    <CommonDialogBulkUpload v-model="vehicleBulkUpload" upload-to="Vehicles" />
    <CommonDialogAllprojectlistdialog
      parent="vehicles"
      v-model="showProjectListDialog"
    />
    <VehicleVehiclefilter
      ref="vehicleFilterDialog"
      v-model="openVehicleFilterDialog"
      @vehicleFilterChanged="vehicleFilterChanged"
    />
  </div>
</template>

<script>
import { makeInstance, encryptLocal } from "~/assets/js/encryptLocal";
import { AgGridVue } from "ag-grid-vue";
import vehicleEdit from "~/components/common/aggrid/buttons/vehicleEdit";
import vehileChip from "~/components/common/aggrid/chip/vehicleTagChip.vue";
import { downloadBlobData, toTitleCase } from "~/assets/utils.js";


export default {
  components: {
    AgGridVue,
    vehicleEdit,
    vehileChip,
  },
  data() {
    return {
      showProjectListDialog: false,
      formType: "add",
      defaultColDef: {
        lockPosition: true,
      },
      filter: {},
      tableSelectedHeader: [
        "vehicle_plate_no",
        "tonnage_capacity",
        "cbm_capacity",
        "fuel_type",
        "project",
        "status",
      ],
      openVehicleTagFormDialog: false,
      openVehicleFilterDialog: false,
      customFilter: {},
      selectColumnDefs: [],
      openVehicleForm: false,
      vehicleBulkUpload: false,
      frameworkComponents: null,
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
      itemsPerPage: 10,
      pageNo: 1,
      userPermissions: encryptLocal.getItem("permissions"),
    };
  },
  computed: {
    gridHeight() {
      return `${window.innerHeight - 296}px`;
    },
    columnDefs() {
      let colDef = [
        {
          headerName: "Vehicle No. Plate",
          width: 170,
          field: "vehicle_plate_no",
        },
        {
          headerName: "Capacity",
          width: 170,
          field: "tonnage_capacity",
        },
        {
          headerName: "CBM capacity",
          width: 170,
          field: "cbm_capacity",
        },
        {
          headerName: "Fuel Type",
          width: 170,
          field: "fuel_type",
          cellRenderer: (params) => {
            return toTitleCase(params.value)
          },
        },
        {
          headerName: "Project",
          width: 170,
          field: "project",
        },
        {
          headerName: "Assigned Tags",
          field: "assigned_tags",
          hide:false,
          width: 350,
          cellRendererFramework: "vehileChip",
        },
        {
          headerName: "Status",
          width: 170,
          field: "status",
          cellRenderer: (params) => {
            return toTitleCase(params.value == "idle" ? "Active" : params.value)
          },
        },
      ];

      if (
        this.userPermissions.vehicle &&
        (this.userPermissions.vehicle.change ||
          this.userPermissions.vehicle.delete)
      ) {
        colDef.push({
          headerName: "Actions",
          width: 170,
          maxWidth: 170,
          minWidth: 170,
          field: "actions",
          pinned: "right",
          cellRendererFramework: "vehicleEdit",
        });
      }
      return colDef;
    },
    allVehicles() {
      return this.$store.state.vehicle.vehiclList;
    },
    totalPages() {
      return Math.ceil(
        this.$store.state.vehicle.totalItems / this.itemsPerPage
      );
    },
    offset() {
      return this.itemsPerPage * (this.pageNo - 1);
    },
    headersToShow() {
      return this.columnDefs.filter((header) => header.headerName != "Actions");
    },
  },
  methods: {
    addTag() {
      this.openVehicleTagFormDialog = true;
    },
    downloadAllVehicles(projects) {
      let params = {};
      if (projects && projects.length) {
        params.project__project_id = projects.toString();
      }
      this.$store
        .dispatch("vehicle/DOWNLOAD_ALL_VEHICLES", params)
        .then((result) => {
          downloadBlobData(result, "Vehicles.xls");
          this.$notifier.showMessage({
            content: "All Vehicles Data Downloaded",
            color: "success",
          });
          this.showProjectListDialog = false;
        })
        .catch((err) => {
          if (err.message) {
            this.$notifier.showMessage({
              content: err.message,
              color: "error",
            });
          } else {
            this.$notifier.showMessage({
              content: "Something went wrong!",
              color: "error",
            });
          }
        });
    },
    reSetColumn() {
      this.$refs.select.blur();
    },
    setSelectedColumn() {
      this.headersToShow.forEach((header) => {
        if (this.tableSelectedHeader.includes(header.field)) {
          this.columnApi.setColumnVisible(header.field, true);
        } else {
          this.columnApi.setColumnVisible(header.field, false);
        }
      });
      this.autoSizeAll();
    },
    autoSizeAll() {
      let allColumnIds = [];
      this.gridOptions.columnApi.getAllColumns().forEach(function (column) {
        allColumnIds.push(column.colId);
      });
      this.gridOptions.columnApi.autoSizeColumns(allColumnIds);
    },
    getSelectedColumn() {
      this.tableSelectedHeader =
        JSON.parse(localStorage.getItem("vehicle_columns")) != null
          ? JSON.parse(localStorage.getItem("vehicle_columns"))
          : this.tableSelectedHeader;
    },
    changeHeadersToshow(e) {
      this.headersToShow.forEach((header) => {
        if (e.indexOf(header.field) > -1 || e.length == 0) {
          this.columnApi.setColumnVisible(header.field, true);
        } else {
          this.columnApi.setColumnVisible(header.field, false);
        }
      });
      this.autoSizeAll();
      this.tableSelectedHeader = e;
      localStorage.setItem("vehicle_columns", JSON.stringify(e));
    },
    addVehicle() {
      this.formType = "add";
      this.openVehicleForm = true;
      this.$store.dispatch("customer/customerAddress/GET_TAG_LIST");
    },
    editVehicle(id) {
      this.$store
        .dispatch("vehicle/GET_VEHICLE_DETAILS", id)
        .then((data) => {
          this.formType = "edit";
          this.openVehicleForm = true;
        })
        .catch((err) => {
          this.$notifier.showMessage({
            content: "Couln't fetch data",
            color: "error",
          });
        });
    },
    gridReady(params) {
      this.gridApi = params.api;
      this.columnApi = params.columnApi;
      this.getSelectedColumn();
      this.setSelectedColumn();
    },
    get_all_projects() {
      this.$store.dispatch("project/GET_ALL_PROJECT_LIST");
    },
    getAllVehicles() {
      this.filter.limit = this.itemsPerPage;
      this.filter.offset = this.offset;
      this.$store.dispatch("vehicle/GET_ALL_VEHICLES", {...this.filter, ...this.customFilter});
    },
    nextPage() {
      this.pageNo++;
      this.getAllVehicles();
    },
    prevPage() {
      this.pageNo--;
      this.getAllVehicles();
    },
    itemsPerPageChange(value) {
      this.pageNo = 1;
      this.itemsPerPage = value;
      this.getAllVehicles();
    },
    vehicleFilterChanged() {
      let filters = localStorage.getItem("vehicleFilters");
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
      if(filters && "tags" in filters && Array.isArray(filters.tags)) {
        filters.tags = filters.tags.join(",");
      }
      if (filters && "ordering" in filters && "sorting" in filters) {
        if (filters.sorting == "descending") {
          filters.ordering = "-" + filters.ordering;
        }
      }
      this.customFilter = filters;
      this.pageNo = 1;
      this.getAllVehicles();
    },
  },
  mounted() {
    this.get_all_projects();
    this.vehicleFilterChanged();
    this.getSelectedColumn();
  },
  beforeCreate() {
    if (encryptLocal == null) {
      makeInstance(localStorage.getItem("user"));
    }
  },
  beforeMount() {
    this.getSelectedColumn();
  },
};
</script>
