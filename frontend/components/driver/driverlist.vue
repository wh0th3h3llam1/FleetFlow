<template>
  <div
    class="pa-6"
    @scroll="reSetColumn()"
    style="height: 100%; width: 100%; overflow: scroll; position: absolute"
  >
    <v-row no-gutters class="pb-6">
      <v-col cols="6">
        <span class="text-h5 text-uppercase font-weight-bold"> Drivers </span>
      </v-col>
      <v-col
        v-if="userPermissions.driver && userPermissions.driver.add"
        cols="6"
        class="text-right"
      >
        <!-- NOte : this functionality used in future -->
        <v-btn small depressed class="primary d-none" @click="addTag()">
          <v-icon small class="mr-1">mdi-plus</v-icon>
          <span class="mr-2">Add Tag</span>
        </v-btn>
        <v-btn small depressed class="primary" @click="addDriver()">
          <v-icon small class="mr-1">mdi-plus</v-icon>
          <span class="mr-2">Add Driver</span>
        </v-btn>
        <v-btn small depressed class="primary" @click="driverBulkUpload = true">
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
          <span>Download All Driver Data</span>
        </v-btn>
      </v-col>
    </v-row>
    <v-row no-gutters class="pb-2">
      <v-col cols="3">
        <v-text-field
          class="mr-3"
          color="light_black"
          label="Search drivers.."
          hide-details="auto"
          prepend-inner-icon="mdi-magnify"
          v-model="filter.search"
          outlined
          dense
          clearable
          @input="searchDriver()"
        ></v-text-field>
      </v-col>
      <v-col cols="3" class="d-flex justify-end align-center">
        <v-select
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
              {{ selectedHeaders }} Column Selected
            </span>
          </template>
        </v-select>
      </v-col>
      <v-col cols="6" class="text-right">
        <v-btn
          depressed
          color="primary"
          class="rounded"
          @click="openDriverFilterDialog = true"
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
          :row-data="Drivers"
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
    <DriverDriverform v-model="openDriverFormDialog" :formType="formType" />
    <DriverDrivertagform v-model="openTagFormDialog" :formType="tagformType" />
    <CommonDialogBulkUpload v-model="driverBulkUpload" upload-to="Drivers" />
    <CommonDialogAllprojectlistdialog
      parent="drivers"
      v-model="showProjectListDialog"
    />
    <DriverDriverfilter 
      ref="driverFilterDialog"
      v-model="openDriverFilterDialog"
      @driverFilterChanged="driverFilterChanged"
    />
  </div>
</template>

<script>
import { AgGridVue } from "ag-grid-vue";
import driverButton from "~/components/common/aggrid/buttons/DriverButton.vue";
import driverChip from "~/components/common/aggrid/chip/driverTagChip.vue";
import { makeInstance, encryptLocal } from "~/assets/js/encryptLocal";
import { downloadBlobData } from "~/assets/utils.js";

export default {
  components: {
    AgGridVue,
    driverButton,
    driverChip,
  },
  data() {
    return {
      showProjectListDialog: false,
      filter: {},
      customFilter: {},
      formType: "add",
      tagformType: "add",
      itemsPerPage: 10,
      pageNo: 1,
      defaultColDef: {
        lockPosition: true,
      },
      tableSelectedHeader: [
        "first_name",
        "last_name",
        "username",
        "contact_number",
        "project",
        "zone",
        "status",
        "vehicle",
        "shift_start",
        "shift_end",
      ],
      selectColumnDefs: [],
      selectedHeaders: 10,
      frameworkComponents: null,
      driverBulkUpload: false,
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
      // other variables
      loaderProgress: false,
      openDriverFilterDialog: false,
      openDriverFormDialog: false,
      openTagFormDialog: false,
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
          headerName: "First name",
          field: "first_name",
        },
        {
          headerName: "Last name",
          field: "last_name",
        },
        {
          headerName: "Username",
          field: "username",
        },
        {
          headerName: "Contact Number",
          field: "contact_number",
        },
        {
          headerName: "Project",
          field: "project",
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
          headerName: "Vehicle Number",
          field: "vehicle",
        },
        {
          headerName: "Nationality",
          field: "nationality",
        },
        {
          headerName: "License Number",
          field: "license_number",
        },
        //  NOte : this functionality used in future
        // {
        //   headerName: "Assigned Tags",
        //   field: "assigned_tags",
        //   cellRendererFramework: "driverChip",
        // },
        {
          headerName: "Duty Status",
          field: "status",
          cellRenderer: (params) => {
            return params.value.replace("_", " ").toUpperCase();
          },
        },
      ];

      if (
        this.userPermissions.driver &&
        (this.userPermissions.driver.change ||
          this.userPermissions.driver.delete)
      ) {
        colDef.push({
          headerName: "Actions",
          width: 170,
          field: "actions",
          pinned: "right",
          cellRendererFramework: "driverButton",
        });
      }
      return colDef;
    },
    Drivers() {
      return this.$store.state.driver.drivers;
    },
    driverFilter() {
      return this.$store.state.driver.driverFilters;
    },
    totalPages() {
      return Math.ceil(this.$store.state.driver.totalItems / this.itemsPerPage);
    },
    offset() {
      return this.itemsPerPage * (this.pageNo - 1);
    },
    headersToShow() {
      return this.columnDefs.filter((header) => header.headerName != "Actions");
    },
  },
  methods: {
    downloadAllDrivers(projects) {
      let params = {};
      if (projects && projects.length) {
        params.project__project_id = projects.toString();
      }
      this.$store
        .dispatch("driver/DOWNLOAD_ALL_DRIVERS", params)
        .then((result) => {
          downloadBlobData(result, "Drivers.xls");
          this.$notifier.showMessage({
            content: "All Driver Data Downloaded",
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
      this.selectedHeaders = this.tableSelectedHeader.length;
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
        JSON.parse(localStorage.getItem("drivers_columns")) != null
          ? JSON.parse(localStorage.getItem("drivers_columns"))
          : this.tableSelectedHeader;
    },
    changeHeadersToshow(e) {
      this.headersToShow.forEach((header) => {
        if (e.indexOf(header.field) > -1 || e.length == 0) {
          this.columnApi.setColumnVisible(header.field, true);
          this.selectedHeaders = e.length;
        } else {
          this.columnApi.setColumnVisible(header.field, false);
        }
      });
      this.autoSizeAll();
      this.selectColumnDefs = e;
      localStorage.setItem("drivers_columns", JSON.stringify(e));
    },
    addTag() {
      this.tagformType = "add";
      this.openTagFormDialog = true;
    },
    addDriver() {
      this.formType = "add";
      this.openDriverFormDialog = true;
      this.$store.dispatch("customer/customerAddress/GET_TAG_LIST");
    },
    editDriver(id) {
      this.$store
        .dispatch("driver/GET_DRIVER_DETAILS", id)
        .then((result) => {
          this.formType = "edit";
          this.$store.dispatch(
            "driver/GET_VEHICLE_LIST_FOR_FORM",
            result.project
          );
          this.$store
            .dispatch("driver/GET_ZONE_LIST_FOR_FORM", result.project)
            .then(() => {
              this.openDriverFormDialog = true;
            });
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
    coloredDriverStatus(status) {
      if (status == "off_duty") {
        return "black";
      } else {
        return "pgreen";
      }
    },
    searchDriver() {
      this.pageNo = 1;
      this.get_drivers_list();
    },
    get_drivers_list() {
      this.filter.limit = this.itemsPerPage;
      this.filter.offset = this.offset;
      this.loaderProgress = true;
      this.$store
        .dispatch("driver/GET_ALL_DRIVERS", {...this.filter, ...this.customFilter})
        .then((result) => {
          this.loaderProgress = false;
        })
        .catch((err) => {
          this.loaderProgress = false;
        });
    },
    nextPage() {
      this.pageNo++;
      this.get_drivers_list();
    },
    prevPage() {
      this.pageNo--;
      this.get_drivers_list();
    },
    itemsPerPageChange(value) {
      this.pageNo = 1;
      this.itemsPerPage = value;
      this.get_drivers_list();
    },
    driverFilterChanged() {
      let filters = localStorage.getItem("driverFilters");
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
      if (filters && "ordering" in filters && "sorting" in filters) {
        if (filters.sorting == "descending") {
          filters.ordering = "-" + filters.ordering;
        }
      }
      this.customFilter = filters
      this.pageNo = 1;
      this.get_drivers_list();
    },
  },
  mounted() {
    if (process.browser) {
      if (this.$vuetify.breakpoint.xl) {
        this.containerHeight =
          ((window.innerHeight / 100) * 75).toFixed() + "px";
      } else if (this.$vuetify.breakpoint.lg) {
        this.containerHeight =
          ((window.innerHeight / 100) * 65).toFixed() + "px";
      }
    }
    this.driverFilterChanged();
    this.getSelectedColumn();
    this.$store.dispatch("vehicle/GET_ALL_VEHICLES");
    this.$store.dispatch("zone/GET_ALL_ZONES");
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

<style>
</style>