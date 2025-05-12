<template>
  <div
    class="pa-6"
    @scroll="reSetColumn()"
    style="height: 100%; width: 100%; overflow: scroll; position: absolute"
  >
    <v-row no-gutters class="pb-6">
      <v-col cols="6">
        <span class="text-h5 text-uppercase font-weight-bold">
          Item Master
        </span>
      </v-col>
      <v-col cols="6" class="text-right">
        <v-btn
          small
          depressed
          class="primary"
          v-if="userPermissions.itemmaster && userPermissions.itemmaster.add"
          @click="addItem()"
        >
          <v-icon small class="mr-1">mdi-plus</v-icon>
          <span>Add Item</span>
        </v-btn>
        <v-btn
          small
          depressed
          class="primary"
          v-if="userPermissions.itemmaster && userPermissions.itemmaster.add"
          @click="itemListBulkUpload = true"
        >
          <v-icon small class="mr-1">mdi-arrow-up-bold</v-icon>
          <span>Bulk Upload</span>
        </v-btn>

        <v-btn small depressed class="primary" @click="downloadAllItems">
          <v-icon small class="mr-1">mdi-arrow-down-bold</v-icon>
          <span>Download All Items</span>
        </v-btn>
      </v-col>
    </v-row>
    <v-row no-gutters class="pb-2">
      <v-col cols="3">
        <v-text-field
          class="mr-3"
          color="light_black"
          prepend-inner-icon="mdi-magnify"
          v-model="filter.search"
          label="Search items.."
          hide-details="auto"
          outlined
          dense
          clearable
          @input="getAllItems()"
        ></v-text-field>
      </v-col>
      <v-col cols="3">
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
          :animateRows="true"
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
          @click="openItemFilterDialog = true"
        >
          <v-icon small class="mr-1">mdi-filter</v-icon>
          Filter
        </v-btn>
      </v-col>
    </v-row>
    <v-row no-gutters>
      <v-col cols="12">
        <div class="pt-4">
          <AgGridVue
            @grid-ready="gridReady"
            :grid-options="gridOptions"
            :column-defs="columnDefs"
            :default-col-def="defaultColDef"
            :row-data="allItems"
            :style="{ width: '100%', height: gridHeight }"
            class="ag-theme-material cf-table"
          >
          </AgGridVue>
        </div>
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

    <ItemItemfilter
      ref="itemFilterDialog"
      v-model="openItemFilterDialog"
      @itemFilterChanged="itemFilterChanged"
    />
    <ItemItemform v-model="openItemForm" :formType="formType" />
    <CommonDialogBulkUpload v-model="itemListBulkUpload" upload-to="Items" />
  </div>
</template>

<script>
import { AgGridVue } from "ag-grid-vue";
import itemEdit from "~/components/common/aggrid/buttons/itemEdit.vue";
import authHeader from "~/store/authHeader";
import { downloadBlobData } from "~/assets/utils.js";
import { makeInstance, encryptLocal } from "~/assets/js/encryptLocal";

export default {
  components: {
    AgGridVue,
    itemEdit,
  },
  data() {
    return {
      formType: "add",
      itemListBulkUpload: false,
      openItemForm: false,
      openItemFilterDialog: false,
      customFilter: {},
      tableSelectedHeader: [
        "item_no",
        "item_description",
        "unit",
        "storage_type",
        "cbm",
        "length",
        "width",
        "height",
        "weight",
      ],
      selectColumnDefs: [],
      defaultColDef: {
        lockPosition: true,
      },
      columnDefs: [
        {
          headerName: "Item number",
          field: "item_no",
          resizable: true,
          // autoSizeColumn: true,
          pinned : "left",
          maxWidth : 150,
          minWidth : 150,
          hide: false,
        },
        {
          headerName: "Item name",
          field: "item_description",
          resizable: true,
          width:500,
          hide: false,
        },
        {
          headerName: "Unit",
          field: "unit",
          hide: false,
        },
        {
          headerName: "Item Group",
          field: "storage_type",
          hide: false,
        },
        {
          headerName: "Length",
          field: "length",
          hide: false,
        },
        {
          headerName: "Width",
          field: "width",
          hide: false,
        },
        {
          headerName: "Height",
          field: "height",
          hide: false,
        },
        {
          headerName: "Weight",
          field: "weight",
          hide: false,
        },
        {
          headerName: "L*W*H (Volume)",
          field: "cbm",
          hide: false,
        },
        {
          headerName: "Actions",
          field: "actions",
          pinned: "right",
          maxWidth : 100,
          minWidth : 100,
          cellRendererFramework: "itemEdit",
          hide: false,
        },
      ],
      filter: {},
      frameworkComponents: null,
      gridApi: null,
      columnApi: null,
      selectedHeaders: 9,
      gridOptions: {
        onGridSizeChanged: () => {
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
    allItems() {
      return this.$store.state.item.items;
    },
    totalPages() {
      return Math.ceil(this.$store.state.item.totalItems / this.itemsPerPage);
    },
    offset() {
      return this.itemsPerPage * (this.pageNo - 1);
    },
    headersToShow() {
      return this.columnDefs.filter((header) => header.field != "actions");
    },
  },
  methods: {
    downloadAllItems() {
      this.$store
        .dispatch("item/DOWNLOAD_ALL_ITEMS")
        .then((result) => {
          downloadBlobData(result, "Item Masters.xls");
          this.$notifier.showMessage({
            content: "All Items Downloaded",
            color: "success",
          });
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
    changeHeadersToshow(e) {
      this.headersToShow.forEach((header) => {
        if (e.indexOf(header.field) > -1 || e.length == 0) {
          this.columnApi.setColumnVisible(header.field, true);
          this.selectedHeaders = e.length;
        } else {
          this.columnApi.setColumnVisible(header.field, false);
        }
      });
      this.gridOptions.api.sizeColumnsToFit();
      this.tableSelectedHeader = e;
      localStorage.setItem("item_columns", JSON.stringify(e));
    },
    gridReady(params) {
      this.gridApi = params.api;
      this.columnApi = params.columnApi;
      this.getSelectedColumn();
      this.setSelectedColumn();
    },
    getAllItems() {
      this.filter.limit = this.itemsPerPage;
      this.filter.offset = this.offset;
      this.$store
        .dispatch("item/GET_ALL_ITEMS", {...this.filter, ...this.customFilter})
        .then((result) => {})
        .catch((err) => {
          this.$notifier.showMessage({
            content: err.detail,
            color: "error",
          });
        });
    },
    addItem() {
      this.$axios.options("/api/v1/items/", { headers: authHeader() });
      this.formType = "add";
      this.openItemForm = true;
    },
    editItem(id) {
      this.$store
        .dispatch("item/GET_ITEM_DETAILS", id)
        .then(() => {
          this.formType = "edit";
          this.openItemForm = true;
        })
        .catch((err) => {
          this.$notifier.showMessage({
            content: "Couln't fetch data",
            color: "error",
          });
        });
    },
    nextPage() {
      this.pageNo++;
      this.getAllItems();
    },
    prevPage() {
      this.pageNo--;
      this.getAllItems();
    },
    itemsPerPageChange(value) {
      this.pageNo = 1;
      this.itemsPerPage = value;
      this.getAllItems();
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
    getSelectedColumn() {
      this.tableSelectedHeader =
        JSON.parse(localStorage.getItem("item_columns")) != null
          ? JSON.parse(localStorage.getItem("item_columns"))
          : this.tableSelectedHeader;
    },
    itemFilterChanged() {
      let filters = localStorage.getItem("itemFilters");
      if (!filters) {
        filters = {};
      }
      if (typeof filters == typeof "string") {
        filters = JSON.parse(filters);
      }
      if(filters && "storage_type" in filters && Array.isArray(filters.storage_type)) {
        filters.storage_type = filters.storage_type.join(",");
      }
      if(filters && "unit" in filters && Array.isArray(filters.unit)) {
        filters.unit = filters.unit.join(",");
      }
      if (filters && "ordering" in filters && "sorting" in filters) {
        if (filters.sorting == "descending") {
          filters.ordering = "-" + filters.ordering;
        }
      }
      this.customFilter = filters;
      this.pageNo = 1;
      this.getAllItems();
    },
  },
  mounted() {
    this.itemFilterChanged();
    this.getSelectedColumn();
  },
  beforeMount() {
    this.getSelectedColumn();
  },
  beforeCreate() {
    if (encryptLocal == null) {
      makeInstance(localStorage.getItem("user"));
    }
  },
};
</script>