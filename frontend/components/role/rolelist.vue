<template>
  <div class="pa-6">
    <v-row no-gutters class="pb-6">
      <v-col cols="6">
        <span class="text-h5 text-uppercase font-weight-bold"> Roles </span>
      </v-col>
      <v-col cols="6" class="text-right">
        <v-btn small depressed class="primary" @click="addRole()">
          <v-icon small class="mr-1">mdi-plus</v-icon>
          <span>Add Role</span>
        </v-btn>
      </v-col>
    </v-row>
    <v-row no-gutters class="pb-2">
      <v-col cols="3">
        <v-text-field
          color="light_black"
          label="Search here.."
          prepend-inner-icon="mdi-magnify"
          hide-details="auto"
          outlined
          dense
          v-model="searching_role"
          @input="getRoleListSearching()"
          clearable
        ></v-text-field>
      </v-col>
    </v-row>
    <div class="pt-4">
      <AgGridVue
        :grid-options="gridOptions"
        :column-defs="
          userPermissions.role &&
          (userPermissions.role.change || userPermissions.role.delete)
            ? columnDefs
            : restrictedColumnDefs
        "
        :default-col-def="defaultColDef"
        :row-data="roleList"
        style="width: 100%; height: 450px"
        class="ag-theme-material cf-table"
      >
      </AgGridVue>
    </div>
    <RoleRoleform v-model="openRoleForm" :formType="formType" />
  </div>
</template>

<script>
import { AgGridVue } from "ag-grid-vue";
import RoleButton from "~/components/common/aggrid/buttons/RoleButton.vue";
import { makeInstance, encryptLocal } from "~/assets/js/encryptLocal";

export default {
  components: {
    AgGridVue,
    RoleButton,
  },
  data() {
    return {
      formType: "add",
      defaultColDef: {
        lockPosition: true,
      },
      openRoleForm: false,
      searching_role: null,
      columnDefs: [
        {
          headerName: "Role Name",
          field: "role_name",
        },
        {
          headerName: "Actions",
          width: 170,
          maxWidth: 170,
          minWidth: 170,
          field: "actions",
          pinned: "right",
          cellRendererFramework: "RoleButton",
        },
      ],
      restrictedColumnDefs: [
        {
          headerName: "Role Name",
          field: "role_name",
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
      userPermissions: encryptLocal.getItem("permissions"),
    };
  },
  methods: {
    addRole() {
      this.formType = "add";
      this.openRoleForm = true;
    },
    editRole(id) {
      this.$store
        .dispatch("role/GET_ROLE_DETAILS", id)
        .then((response) => {
          this.formType = "edit";
          this.openRoleForm = true;
        })
        .catch((error) => {
          this.$notifier.showMessage({
            content: "Couln't fetch data",
            color: "error",
          });
        });
    },
    deleteRole(id) {
      this.$store
        .dispatch("role/DELETE_ROLE", id)
        .then((response) => {
          this.$notifier.showMessage({
            content: "Role Deleted successfully",
            color: "error",
          });
        })
        .catch((error) => {
          this.$notifier.showMessage({
            content: "Role can't Deleted",
            color: "error",
          });
        });
    },
    getRoleList() {
      this.$store.dispatch("role/GET_ALL_ROLE");
    },
    getRoleListSearching() {
      this.gridOptions.api.setQuickFilter(this.searching_role);
    },
  },
  computed: {
    roleList() {
      return this.$store.state.role.rolelist;
    },
  },
  beforeMount() {
    this.getRoleList();
  },
  beforeCreate() {
    if (encryptLocal == null) {
      makeInstance(localStorage.getItem("user"));
    }
  },
};
</script>