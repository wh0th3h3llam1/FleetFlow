<template>
  <div
    class="pa-6"
    @scroll="reSetColumn()"
    style="height: 100%; width: 100%; overflow: scroll; position: absolute"
  >
    <v-row no-gutters class="pb-6">
      <v-col>
        <span class="text-h5 text-uppercase font-weight-bold">
          Customer Addresses
        </span>
      </v-col>
      <v-col
        cols="8"
        class="text-right"
        v-if="
          userPermissions.customeraddress && userPermissions.customeraddress.add
        "
      >
        <v-btn
          small
          depressed
          class="primary"
          @click="openCustomerAddressForm()"
        >
          <v-icon small class="mr-1">mdi-plus</v-icon>
          <span>Add Address</span>
        </v-btn>
        <v-btn
          depressed
          small
          class="primary"
          @click="customerAddressBulkUpload = true"
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
      <v-col cols="3">
        <v-text-field
          class="mr-3"
          color="light_black"
          prepend-inner-icon="mdi-magnify"
          label="Search addresses.."
          v-model="filter.search"
          hide-details="auto"
          outlined
          dense
          clearable
          @input="getCustomerAddresses()"
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
          hide-details
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
          @click="openCustomerFilterDialog = true"
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
          :column-defs="
            userPermissions.customeraddress &&
            userPermissions.customeraddress.change
              ? columnDefs
              : restrictedColumnDefs
          "
          :default-col-def="defaultColDef"
          :row-data="rowData"
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
    <CustomerCustomeraddressform
      v-model="customerAddressForm"
      :formType="formType"
    />

    <CommonDialogBulkUpload
      v-model="customerAddressBulkUpload"
      upload-to="Customer Addresses"
    />
    <CommonDialogAllprojectlistdialog
      parent="customers"
      v-model="showProjectListDialog"
    />
    <CustomerCustomeraddressfilter
      ref="customerFilterDialog"
      v-model="openCustomerFilterDialog"
      @customerFilterChanged="customerFilterChanged"
    />
  </div>
</template>

<script>
import { AgGridVue } from "ag-grid-vue";
import customerAddressEdit from "~/components/common/aggrid/buttons/customerAddressEdit.vue";
import tagChip from "~/components/common/aggrid/chip/customerAddressTagChip.vue";
import { encryptLocal } from "~/assets/js/encryptLocal";
import { downloadBlobData } from "~/assets/utils.js";

export default {
  components: {
    AgGridVue,
    customerAddressEdit,
    tagChip,
  },
  data() {
    return {
      showProjectListDialog: false,
      overlay: false,
      formType: "add",
      tableSelectedHeader: [
        "customer_code",
        "customer_name",
        "address",
        "contact_person",
        "contact_number",
        "project",
        "processing_time",
      ],
      customfilter: {},
      selectColumnDefs: [],
      customerAddressForm: false,
      customerAddressBulkUpload: false,
      selectedHeaders: 8,
      defaultColDef: {
        lockPosition: true,
      },
      restrictedColumnDefs: [
        {
          headerName: "Customer Code",
          pinned: "left",
          hide: false,
          field: "customer_code",
        },
        {
          headerName: "Customer Name",
          hide: false,
          field: "customer_name",
        },
        {
          headerName: "Address",
          hide: false,
          field: "address",
        },
        {
          headerName: "Contact Person",
          hide: false,
          field: "contact_person",
        },
        {
          headerName: "Contact number",
          hide: false,
          field: "contact_number",
        },
        {
          headerName: "Customer Type",
          hide: false,
          field: "customer_type",
        },
        {
          headerName: "Project",
          hide: false,
          field: "project",
        },
        {
          headerName: "Processing Time",
          hide: false,
          field: "processing_time",
        },
        {
          headerName: "Remarks",
          hide: false,
          field: "remarks",
        },
        {
          headerName: "Tags",
          field: "assigned_tags",
          hide:false,
          width: 500,
          cellRendererFramework: "tagChip",
        },
      ],
      columnDefs: [
        {
          headerName: "Customer Code",
          hide: false,
          pinned: "left",
          field: "customer_code",
        },
        {
          headerName: "Customer Name",
          hide: false,
          field: "customer_name",
        },
        {
          headerName: "Address",
          hide: false,
          field: "address",
        },
        {
          headerName: "Contact Person",
          hide: false,
          field: "contact_person",
        },
        {
          headerName: "Contact number",
          hide: false,
          field: "contact_number",
        },
        {
          headerName: "Customer Type",
          hide: false,
          field: "customer_type",
        },
        {
          headerName: "Project",
          hide: false,
          field: "project",
        },
        {
          headerName: "Processing Time",
          hide: false,
          field: "processing_time",
        },
        {
          headerName: "Remarks",
          hide: false,
          field: "remarks",
        },
        {
          headerName: "Tags",
          field: "assigned_tags",
          hide:false,
          width: 500,
          cellRendererFramework: "tagChip",
        },
        {
          headerName: "Actions",
          width: 170,
          maxWidth: 170,
          field: "actions",
          pinned: "right",
          hide: false,
          cellRendererFramework: "customerAddressEdit",
        },
      ],
      gridApi: null,
      columnApi: null,
      gridOptions: {
        onGridSizeChanged: () => {},
        headerHeight: 40,
        rowHeight: 40,
        rowSelection: "multiple",
        suppressRowClickSelection: true,
        suppressDragLeaveHidesColumns: true,
        enableCellTextSelection: true,
      },
      filter: {},
      itemsPerPage: 10,
      pageNo: 1,
      openCustomerFilterDialog: false,
      userPermissions: encryptLocal.getItem("permissions"),
    };
  },
  computed: {
    gridHeight() {
      return `${window.innerHeight - 296}px`;
    },
    rowData() {
      return this.$store.state.customer.customerAddress.customerAddress;
    },
    totalPages() {
      return Math.ceil(
        this.$store.state.customer.customerAddress.totalItems /
          this.itemsPerPage
      );
    },
    offset() {
      return this.itemsPerPage * (this.pageNo - 1);
    },
    headersToShow() {
      return this.columnDefs.filter((header) => header.field != "actions");
    },
  },
  watch: {
    rowData() {
      setTimeout(() => {
        this.autoSizeAll();
      }, 1500);
    },
  },
  methods: {
    autoSizeAll() {
      let allColumnIds = [];
      this.gridOptions.columnApi.getAllColumns().forEach(function (column) {
        if(column.colId != 'assigned_tags'){
          allColumnIds.push(column.colId);
        }
      });
      this.gridOptions.columnApi.autoSizeColumns(allColumnIds);
    },
    downloadAllCustomers(projects) {
      let params = {};
      if (projects && projects.length) {
        params.project__project_id = projects.toString();
      }
      this.$store
        .dispatch("customer/customerAddress/DOWNLOAD_ALL_CUSTOMERS", params)
        .then((result) => {
          downloadBlobData(result, "Customer Addresses.xls");
          this.$notifier.showMessage({
            content: "All Customer Data Downloaded",
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
    editCustomer(id) {
      this.$store.commit("customer/customerAddress/SET_EDIT_MODE", true);
      this.$store
        .dispatch("customer/customerAddress/GET_CUSTOMER_ADDRESS_DETAILS", id)
        .then(() => {
          this.formType = "edit";
          this.customerAddressForm = true;
        })
        .catch((err) => {
          this.$notifier.showMessage({ content: err.message, color: "error" });
        });
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

      this.tableSelectedHeader = e;
      localStorage.setItem("customer_columns", JSON.stringify(e));
    },
    gridReady(params) {
      this.gridApi = params.api;
      this.columnApi = params.columnApi;
      this.getSelectedColumn();
      this.setSelectedColumn();
    },
    openCustomerAddressForm() {
      this.formType = "add";
      this.$store.commit("customer/customerAddress/SET_EDIT_MODE", false);
      this.customerAddressForm = true;
    },
    getCustomerAddresses() {
      if (this.gridApi) {
        this.gridApi.showLoadingOverlay();
      }
      this.filter.limit = this.itemsPerPage;
      this.filter.offset = this.offset;
      this.$store
        .dispatch(
          "customer/customerAddress/GET_ALL_CUSTOMER_ADDRESS",
          {...this.filter, ...this.customfilter}
        )
        .then(() => {
          if (this.gridApi) {
            this.gridApi.hideOverlay();
          }
        })
        .catch(() => {
          if (this.gridApi) {
            this.gridApi.hideOverlay();
          }
        });
    },
    nextPage() {
      this.pageNo++;
      this.getCustomerAddresses();
    },
    prevPage() {
      this.pageNo--;
      this.getCustomerAddresses();
    },
    itemsPerPageChange(value) {
      this.pageNo = 1;
      this.itemsPerPage = value;
      this.getCustomerAddresses();
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
    },
    getSelectedColumn() {
      this.tableSelectedHeader =
        JSON.parse(localStorage.getItem("customer_columns")) != null
          ? JSON.parse(localStorage.getItem("customer_columns"))
          : this.tableSelectedHeader;
    },
    customerFilterChanged(){
      let filters = localStorage.getItem("customerFilters");
      if (!filters) {
        filters = {};
      }
      if (typeof filters == typeof "string") {
        filters = JSON.parse(filters);
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
      this.customfilter = filters
      this.pageNo = 1;
      this.getCustomerAddresses()
    }
  },
  mounted() {
    this.customerFilterChanged();
    this.getSelectedColumn();
  },
  beforeMount() {
    this.getSelectedColumn();
  },
};
</script>
