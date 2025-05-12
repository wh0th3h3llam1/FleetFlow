<template>
  <div class="pa-6">
    <v-row no-gutters class="pb-6">
      <v-col cols="6">
        <span class="text-h5 text-uppercase font-weight-bold"> Zones </span>
      </v-col>
      <v-col cols="6" class="text-right">
        <v-btn
          small
          depressed
          class="primary"
          v-if="userPermissions.zone && userPermissions.zone.add"
          @click="addZone()"
        >
          <v-icon>mdi-plus</v-icon>
          <span>Add Zone</span>
        </v-btn>
      </v-col>
    </v-row>
    <v-row no-gutters class="pb-2">
      <v-col cols="3">
        <v-text-field
          color="light_black"
          label="Search Zones..."
          prepend-inner-icon="mdi-magnify"
          hide-details="auto"
          outlined
          dense
          clearable
          v-model="filter.search"
          @input="searchZone()"
        ></v-text-field>
      </v-col>
      <v-col cols="9" class="text-right">
        <v-btn
          depressed
          color="primary"
          class="rounded"
          @click="openZoneFilterDialog = true"
        >
          <v-icon small class="mr-1">mdi-filter</v-icon>
          Filter
        </v-btn>
      </v-col>
    </v-row>
    <div class="pt-4">
      <AgGridVue
        :grid-options="gridOptions"
        :column-defs="
          userPermissions.zone &&
          (userPermissions.zone.change || userPermissions.zone.delete)
            ? columnDefs
            : restrictedColumnDefs
        "
        :default-col-def="defaultColDef"
        :row-data="zoneList"
        :style="{ width: '100%', height: gridHeight }"
        class="ag-theme-material cf-table"
      >
      </AgGridVue>
    </div>
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
    <ZoneZoneform ref="zoneFrom" v-model="openZoneForm" :formType="formType" />
    <ZoneZonefilter 
      ref="zoneFilterDialog"
      v-model="openZoneFilterDialog"
      @zoneFilterChanged="zoneFilterChanged"
    />
  </div>
</template>

<script>
import { AgGridVue } from "ag-grid-vue";
import ZoneButton from "~/components/common/aggrid/buttons/ZoneButton.vue";
import { makeInstance, encryptLocal } from "~/assets/js/encryptLocal";

export default {
  components: {
    AgGridVue,
    ZoneButton,
  },
  data() {
    return {
      showProjectListDialog: false,
      formType: "add",
      defaultColDef: {
        lockPosition: true,
      },
      openZoneForm: false,
      customFilter: {},
      openZoneFilterDialog: false,
      searching_user: null,
      filter: {},
      columnDefs: [
        {
          headerName: "Zone Name",
          field: "zone_name",
        },
        {
          headerName: "Zone Description",
          field: "zone_desc",
        },
        {
          headerName: "Project",
          field: "project",
        },
        {
          headerName: "Actions",
          width: 170,
          maxWidth: 170,
          minWidth: 170,
          field: "id",
          pinned: "right",
          cellRendererFramework: "ZoneButton",
        },
      ],
      restrictedColumnDefs: [
        {
          headerName: "Zone Name",
          field: "zone_name",
        },
        {
          headerName: "Zone Description",
          field: "zone_desc",
        },
        {
          headerName: "Project",
          field: "project",
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
      itemsPerPage: 10,
      pageNo: 1,
      userPermissions: encryptLocal.getItem("permissions"),
    };
  },
  computed: {
    gridHeight() {
      return `${window.innerHeight - 288}px`;
    },
    totalPages() {
      return Math.ceil(this.$store.state.zone.totalCount / this.itemsPerPage);
    },
    offset() {
      return this.itemsPerPage * (this.pageNo - 1);
    },
    zoneList() {
      return this.$store.state.zone.zonelist;
    },
  },
  methods: {
    downloadAllZones(projects) {
      let params = {};
      if (projects && projects.length) {
        params.project__project_id = projects;
      }
      this.$store
        .dispatch("zone/DOWNLOAD_ALL_ZONES", params)
        .then((result) => {
          downloadBlobData(result, "Zones.xls");
          this.$notifier.showMessage({
            content: "All Zones Downloaded",
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
    addZone() {
      this.formType = "add";
      this.openZoneForm = true;
    },
    editZone(id) {
      this.$store
        .dispatch("zone/GET_ZONE_DETAILS", id)
        .then((response) => {
          this.formType = "edit";
          this.openZoneForm = true;
          let path = [];
          response.geofence.coordinates[0].forEach((element) => {
            path.push({ lat: element[1], lng: element[0] });
          });
          this.$refs.zoneFrom.setEditZoneDetails(
            path,
            response.remaining_zones.zones,
            response.geofence.coordinates[0]
          );
        })
        .catch((error) => {
          this.$notifier.showMessage({
            content: "Couln't fetch data",
            color: "error",
          });
        });
    },
    deleteZone(id) {
      this.$store
        .dispatch("zone/DELETE_ZONE", id)
        .then((response) => {
          this.$notifier.showMessage({
            content: "Zone Deleted successfully",
            color: "error",
          });
        })
        .catch((error) => {
          this.$notifier.showMessage({
            content: "Zone can't delete",
            color: "error",
          });
        });
    },
    getZoneList() {
      this.filter.limit = this.itemsPerPage;
      this.filter.offset = this.offset;
      this.$store.dispatch("zone/GET_ALL_ZONES", {...this.filter, ...this.customFilter});
    },
    searchZone() {
      this.pageNo = 1;
      this.getZoneList();
    },
    nextPage() {
      this.pageNo++;
      this.getZoneList();
    },
    prevPage() {
      this.pageNo--;
      this.getZoneList();
    },
    itemsPerPageChange(value) {
      this.pageNo = 1;
      this.itemsPerPage = value;
      this.getZoneList();
    },
    zoneFilterChanged(){
      let filters = localStorage.getItem("zoneFilters");
      if (!filters) {
        filters = {};
      }
      if (typeof filters == typeof "string") {
        filters = JSON.parse(filters);
      }
      if(filters && "project" in filters && Array.isArray(filters.project)) {
        filters.project = filters.project.join(",");
      }
      this.customFilter = filters
      this.pageNo = 1;    
      this.getZoneList();
    }
  },
  mounted() {
    this.zoneFilterChanged();
  },
  beforeCreate() {
    if (encryptLocal == null) {
      makeInstance(localStorage.getItem("user"));
    }
  },
};
</script>
