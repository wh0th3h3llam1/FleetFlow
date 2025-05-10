<template>
  <div
    class="pa-6"
    @scroll="reSetColumn()"
    style="height: 100%; width: 100%; overflow: scroll; position: absolute"
  >
    <v-row no-gutters class="pb-6">
      <v-col cols="6">
        <span class="text-h5 text-uppercase font-weight-bold"> Users </span>
      </v-col>
      <v-col
        v-if="userPermissions.dashuser && userPermissions.dashuser.add"
        cols="6"
        class="text-right"
      >
        <v-btn small depressed class="primary" @click="addUser()">
          <v-icon small class="mr-1">mdi-plus</v-icon>
          <span>Add User</span>
        </v-btn>
      </v-col>
    </v-row>
    <v-row no-gutters class="pb-2">
      <v-col cols="3" class="mr-3">
        <v-text-field
          color="light_black"
          label="Search here.."
          prepend-inner-icon="mdi-magnify"
          hide-details="auto"
          outlined
          dense
          v-model="searching_user"
          @input="getUserListSearching()"
          clearable
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
          :value="selectColumnDefs"
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
    </v-row>
    <div class="pt-4">
      <AgGridVue
        @grid-ready="gridReady"
        :grid-options="gridOptions"
        :column-defs="
          userPermissions.dashuser &&
          (userPermissions.dashuser.change || userPermissions.dashuser.delete)
            ? columnDefs
            : restrictedColumnDefs
        "
        :default-col-def="defaultColDef"
        :row-data="userList"
        :style="{ width: '100%', height: gridHeight }"
        class="ag-theme-material"
      >
      </AgGridVue>
    </div>
    <UserUserform v-model="openUserForm" :formType="formType" />
  </div>
</template>

<script>
import { AgGridVue } from "ag-grid-vue";
import UserButton from "~/components/common/aggrid/buttons/UserButton.vue";
import { makeInstance, encryptLocal } from "~/assets/js/encryptLocal";

export default {
  components: {
    AgGridVue,
    UserButton,
  },
  data() {
    return {
      formType: "add",
      tableSelectedHeader: ["username", "first_name", "role_name"],
      selectColumnDefs: [],
      defaultColDef: {
        lockPosition: true,
      },
      selectedHeaders: 6,
      openUserForm: false,
      searching_user: null,
      restrictedColumnDefs: [
        {
          headerName: "First Name",
          field: "first_name",
        },
        {
          headerName: "Last Name",
          field: "last_name",
        },
        {
          headerName: "User Name",
          field: "username",
        },
        {
          headerName: "Contact Number",
          field: "contact_number",
        },
        {
          headerName: "Email",
          field: "email",
        },
        {
          headerName: "Role Name",
          field: "role_name",
        },
      ],
      columnDefs: [
        {
          headerName: "First Name",
          field: "first_name",
        },
        {
          headerName: "Last Name",
          field: "last_name",
        },
        {
          headerName: "User Name",
          field: "username",
        },
        {
          headerName: "Contact Number",
          field: "contact_number",
        },
        {
          headerName: "Email",
          field: "email",
        },
        {
          headerName: "Role Name",
          field: "role_name",
        },
        {
          headerName: "Actions",
          field: "id",
          width: 170,
          maxWidth: 170,
          minWidth: 170,
          cellRendererFramework: "UserButton",
          pinned: "right",
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
        pagination: true,
        paginationPageSize: 20,
        suppressRowClickSelection: true,
        suppressDragLeaveHidesColumns: true,
        enableCellTextSelection: true,
      },
      userPermissions: encryptLocal.getItem("permissions"),
    };
  },
  computed: {
    gridHeight() {
      return `${window.innerHeight - 240}px`;
    },
    userList() {
      return this.$store.state.user.userlist;
    },
    headersToShow() {
      return this.columnDefs.filter((header) => header.headerName != "Actions");
    },
  },
  methods: {
    reSetColumn() {
      this.$refs.select.blur();
    },
    addUser() {
      this.formType = "add";
      this.openUserForm = true;
    },
    editUser(id) {
      this.$store
        .dispatch("user/GET_USER_DETAILS", id)
        .then((response) => {
          this.formType = "edit";
          this.openUserForm = true;
        })
        .catch((error) => {
          this.$notifier.showMessage({
            content: "Couln't fetch data",
            color: "error",
          });
        });
    },
    deleteUser(id) {
      this.$store
        .dispatch("user/DELETE_USER", id)
        .then((response) => {
          this.$notifier.showMessage({
            content: "User Deleted successfully",
            color: "error",
          });
        })
        .catch((error) => {});
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
    },
    getUserList() {
      this.$store.dispatch("user/GET_ALL_USERS");
      this.$store.dispatch("role/GET_ALL_ROLE");
    },
    getUserListSearching() {
      this.gridOptions.api.setQuickFilter(this.searching_user);
    },
    gridReady(params) {
      this.gridApi = params.api;
      this.columnApi = params.columnApi;
      this.getSelectedColumn();
      this.setSelectedColumn();
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
      this.selectColumnDefs = [];
      this.selectColumnDefs = this.headersToShow.filter((column, index) => {
        return this.tableSelectedHeader.includes(column.field);
      });
    },
  },
  mounted() {
    this.getSelectedColumn();
  },
  beforeMount() {
    this.getUserList();
    this.getSelectedColumn();
    if (encryptLocal == null) {
      makeInstance(localStorage.getItem("user"));
    }
  },
};
</script>