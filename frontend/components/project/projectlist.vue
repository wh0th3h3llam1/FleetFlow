<template>
  <div class="pa-6">
    <v-row no-gutters class="pb-6">
      <v-col cols="6">
        <span class="text-h5 text-uppercase font-weight-bold"> Projects </span>
      </v-col>
      <v-col
        v-if="userPermissions.project && userPermissions.project.add"
        cols="6"
        class="text-right"
      >
        <v-btn small depressed class="primary" @click="addProject()">
          <v-icon small class="mr-1">mdi-plus</v-icon>
          <span>Add Project</span>
        </v-btn>
      </v-col>
    </v-row>
    <v-row no-gutters class="pb-2">
      <v-col cols="3">
        <v-text-field
          color="light_black"
          v-model="filter.search"
          label="Search here.."
          prepend-inner-icon="mdi-magnify"
          hide-details="auto"
          outlined
          dense
          clearable
          @input="getProjectList()"
        ></v-text-field>
      </v-col>
    </v-row>
    <v-row no-gutters>
      <v-col cols="12">
        <div class="pt-4">
          <AgGridVue
            @grid-ready="gridReady"
            :grid-options="gridOptions"
            :column-defs="
              userPermissions.project &&
              (userPermissions.project.change || userPermissions.project.delete)
                ? columnDefs
                : restrictedColumnDefs
            "
            :default-col-def="defaultColDef"
            :row-data="projectList"
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
    <ProjectProjectform
      v-model="openProjectForm"
      ref="projectForm"
      :formType="formType"
    />
    <ProjectProjectzonevisualization
      v-model="openProjectZoneVisualizationDialog"
      ref="zoneVisualization"
    />
  </div>
</template>


<style scoped>
.info-card {
  position: absolute;
  bottom: 60px;
  right: 26px;
  padding: 0;
  margin: 0;
  min-width: 30px !important;
  border-radius: 0;
}
</style>

<script>
import { AgGridVue } from "ag-grid-vue";
import projectEdit from "~/components/common/aggrid/buttons/projectEdit";
import { makeInstance, encryptLocal } from "~/assets/js/encryptLocal";
import { toTitleCase } from "~/assets/utils.js";

export default {
  components: {
    AgGridVue,
    projectEdit,
  },
  data() {
    return {
      openProjectZoneVisualizationDialog: false,
      formType: "add",
      searchString: "",
      openProjectForm: false,
      defaultColDef: {
        lockPosition: true,
      },
      restrictedColumnDefs: [
        {
          headerName: "Project Name",
          pinned: "left",
          field: "project_name",
        },
        {
          headerName: "Project ID",
          field: "project_id",
        },
        {
          headerName: "Template Name",
          field: "planning_template",
        },
        {
          headerName: "Status",
          field: "status",
        },
        {
          headerName: "Base Address",
          field: "base_address",
        },
      ],
      columnDefs: [
        {
          headerName: "Project Name",
          pinned: "left",
          field: "project_name",
        },
        {
          headerName: "Project ID",
          field: "project_id",
        },
        {
          headerName: "Template Name",
          field: "planning_template",
        },
        {
          headerName: "Status",
          field: "status",
          cellRenderer: (params) => {
            return toTitleCase(params.value);
          },
        },
        {
          headerName: "Base Address",
          field: "base_address",
        },
        {
          headerName: "Actions",
          width: 170,
          maxWidth: 170,
          minWidth: 170,
          field: "actions",
          pinned: "right",
          cellRendererFramework: "projectEdit",
        },
      ],
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
      filter: {},
      itemsPerPage: 10,
      pageNo: 1,
      userPermissions: encryptLocal.getItem("permissions"),
    };
  },
  computed: {
    gridHeight() {
      return `${window.innerHeight - 288}px`;
    },
    projectList() {
      return this.$store.state.project.projects;
    },
    totalPages() {
      return Math.ceil(
        this.$store.state.project.totalItems / this.itemsPerPage
      );
    },
    offset() {
      return this.itemsPerPage * (this.pageNo - 1);
    },
  },
  watch: {
    projectList() {
      setTimeout(() => {
        this.autoSizeAll();
      }, 1000);
    },
  },
  methods: {
    autoSizeAll() {
      let allColumnIds = [];
      this.gridOptions.columnApi.getAllColumns().forEach(function (column) {
        allColumnIds.push(column.colId);
      });
      this.gridOptions.columnApi.autoSizeColumns(allColumnIds);
    },
    viewZonesHandler(zone) {
      this.openProjectZoneVisualizationDialog = true;
      this.$refs.zoneVisualization.viewZones(zone);
    },
    addProject() {
      this.formType = "add";
      this.openProjectForm = true;
    },
    editProject(id) {
      this.$store
        .dispatch("project/GET_PROJECT_DETAILS", id)
        .then((result) => {
          this.formType = "edit";
          this.openProjectForm = true;
          this.$refs.projectForm.loadServisableArea(
            result.serviceable_area.coordinates
          );
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
    },
    getProjectList() {
      this.filter.limit = this.itemsPerPage;
      this.filter.offset = this.offset;
      this.$store.dispatch("project/GET_PROJECT_LIST", this.filter);
    },
    nextPage() {
      this.pageNo++;
      this.getProjectList();
    },
    prevPage() {
      this.pageNo--;
      this.getProjectList();
    },
    itemsPerPageChange(value) {
      this.pageNo = 1;
      this.itemsPerPage = value;
      this.getProjectList();
    },
  },
  beforeMount() {
    this.getProjectList();
  },
  beforeCreate() {
    if (encryptLocal == null) {
      makeInstance(localStorage.getItem("user"));
    }
  },
};
</script>