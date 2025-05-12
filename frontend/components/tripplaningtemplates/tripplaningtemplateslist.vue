<template>
  <div
    class="pa-6"
    style="height: 100%; width: 100%; overflow: scroll; position: absolute"
  >
    <v-row no-gutters class="pb-6">
      <v-col cols="6">
        <span class="text-h5 text-uppercase font-weight-bold">
          Trip Planning Templates
        </span>
      </v-col>
      <v-col cols="6" class="text-right">
        <v-btn small depressed class="primary" @click="openForm(false, false)">
          <v-icon small class="mr-1">mdi-plus</v-icon>
          <span>Create Template</span>
        </v-btn>
      </v-col>
    </v-row>
    <v-row no-gutters class="pb-2">
      <v-col cols="3" class="mr-3">
        <v-text-field
          color="light_black"
          label="Search here.."
          hide-details="auto"
          prepend-inner-icon="mdi-magnify"
          v-model="search"
          outlined
          dense
          clearable
        ></v-text-field>
      </v-col>
    </v-row>
    <v-row no-gutters>
      <v-col cols="12" class="pt-4">
        <AgGridVue
          @grid-ready="gridReady"
          :grid-options="gridOptions"
          :column-defs="columnDefs"
          :default-col-def="defaultColDef"
          :row-data="allTemplates"
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
    <TripplaningtemplatesTripplaningtemplateform
      v-model="tripPlaningTemplateForm"
      :readonly="isReadonly"
      :editMode="templateFormType"
    />
  </div>
</template>

<script>
import { AgGridVue } from "ag-grid-vue";
import tripTemplateDetailsView from "~/components/common/aggrid/buttons/tripTemplateDetailsView.vue";

export default {
  components: {
    AgGridVue,
    tripTemplateDetailsView,
  },
  data() {
    return {
      templateFormType: false,
      defaultColDef: {
        lockPosition: true,
      },
      columnDefs: [
        {
          headerName: "Template Name",
          pinned: "left",
          field: "template_name",
        },
        {
          headerName: "Fill Ratio(%)",
          cellRenderer: (param) => {
            return param.data.fill_ratio + "%";
          },
        },
        {
          headerName: "Loading Timings",
          cellRenderer: (param) => {
            return (
              param.data.loading_start_time +
              " To " +
              param.data.loading_end_time
            );
          },
        },
        {
          headerName: "Offloading Timeing",
          cellRenderer: (param) => {
            return (
              param.data.offloading_start_time +
              " To " +
              param.data.offloading_end_time
            );
          },
        },
        {
          headerName: "Optimize By",
          field: "configuration",
          cellRenderer: (param) => {
            return param.value.replace(/\_/g, " ");
          },
          cellClass: ["text-capitalize"],
        },
        {
          headerName: "Actions",
          field: "actions",
          cellRendererFramework: "tripTemplateDetailsView",
          pinned: "right",
        },
      ],
      gridOptions: {
        onGridSizeChanged: () => {
          this.gridOptions.api.sizeColumnsToFit();
        },
        headerHeight: 40,
        rowHeight: 40,
        suppressRowClickSelection: true,
        enableCellTextSelection: true,
      },
      filter: {},
      tripPlaningTemplateForm: false,
      search: null,
      itemsPerPage: 10,
      pageNo: 1,
      tripPlaningTemplateDetails: false,
      isReadonly: false,
    };
  },
  watch: {
    search(value) {
      if (value !== null && value.length > 3) {
        this.filter.search = value;
        this.getAllTemplates();
      } else if (value == null || value.length == 0) {
        delete this.filter.search;
        this.getAllTemplates();
      }
    },
  },
  computed: {
    gridHeight() {
      return `${window.innerHeight - 296}px`;
    },
    allTemplates() {
      return this.$store.state.trip_planing_templates.templatesList;
    },
    totalPages() {
      return Math.ceil(
        this.$store.state.trip_planing_templates.totalItems / this.itemsPerPage
      );
    },
    offset() {
      return this.itemsPerPage * (this.pageNo - 1);
    },
  },
  methods: {
    gridReady(params) {
      this.gridApi = params.api;
      this.columnApi = params.columnApi;
    },
    getAllTemplates() {
      this.filter.limit = this.itemsPerPage;
      this.filter.offset = this.offset;
      this.$store.dispatch(
        "trip_planing_templates/GET_ALL_PLANNING_TEMPLATES",
        this.filter
      );
    },
    nextPage() {
      this.pageNo++;
      this.getAllTemplates();
    },
    prevPage() {
      this.pageNo--;
      this.getAllTemplates();
    },
    itemsPerPageChange(value) {
      this.pageNo = 1;
      this.itemsPerPage = value;
      this.getAllTemplates();
    },
    openForm(readOnly, editMode, data) {
      this.$store.commit("trip_planing_templates/TOGGLE_READONLY", readOnly);
      this.$store.commit("trip_planing_templates/TOGGLE_EDIT_MODE", editMode);
      if (data) {
        this.$store.commit(
          "trip_planing_templates/SET_TEMPLATE_FORM_DATA",
          data
        );
      }
      this.templateFormType = editMode;
      this.tripPlaningTemplateForm = true;
    },
    editTemplate(id, readOnly, editMode) {
      this.$store
        .dispatch("trip_planing_templates/GET_PLANNING_TEMPLATE_DETAILS", id)
        .then((result) => {
          this.$store.commit(
            "trip_planing_templates/TOGGLE_READONLY",
            readOnly
          );
          this.$store.commit(
            "trip_planing_templates/TOGGLE_EDIT_MODE",
            editMode
          );

          this.templateFormType = editMode;
          this.tripPlaningTemplateForm = true;
        })
        .catch((err) => {
          if (message in err.data) {
            this.$notifier.showMessage({
              content: err.data.message,
              color: "error",
            });
          } else {
            this.$notifier.showMessage({
              content: "Couldn't fetch data!",
              color: "error",
            });
          }
        });
    },
  },
  mounted() {
    this.getAllTemplates();
  },
};
</script>

<style>
</style>