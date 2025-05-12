<template>
  <div class="pa-6">
    <v-row no-gutters class="pb-6">
      <v-col cols="6">
        <span class="text-h5 text-uppercase font-weight-bold"> Tickets </span>
      </v-col>
      <v-col cols="6" class="text-right">
        <v-btn small depressed class="primary" @click="AddTicket()" v-if="ticket_permissions.add == true">
          <v-icon small class="mr-1">mdi-plus</v-icon>
          <span>Add Ticket</span>
        </v-btn>
      </v-col>
    </v-row>
    <v-row no-gutters class="pb-2">
      <v-col cols="3">
        <v-text-field
          color="light_black"
          label="Search Tickets..."
          prepend-inner-icon="mdi-magnify"
          hide-details="auto"
          outlined
          dense
          clearable
          v-model="filter.search"
          @input="searchTicket()"
        ></v-text-field>
      </v-col>
    </v-row>
    <div class="pt-4">
      <v-row>
        <v-col cols="12">
          <AgGridVue
            :grid-options="gridOptions"
            :column-defs="columnDefs"
            :context="context"
            :row-data="ticketList"
            style="width: 100%; height: 450px"
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
    </div>
    <SupportTicketsform v-model="openTicketForm" :formType="formType" />
  </div>
</template>

<script>
import { AgGridVue } from "ag-grid-vue";
import supportButton from "~/components/common/aggrid/buttons/supportButton.vue";
import { toTitleCase } from "~/assets/utils.js";

export default {
  components: {
    AgGridVue,
    supportButton,
  },
  data() {
    return {
      context: { parentComponent: this },
      formType: "add",
      filter: {},
      openTicketForm: false,
      searching_tickets: null,
      itemsPerPage: 10,
      pageNo: 1,
      columnDefs: [
        {
          headerName: "Title",
          field: "title",
        },
        {
          headerName: "Status",
          field: "status",
          cellRenderer: (params) => {
            return toTitleCase(params.value);
          },
        },
        {
          headerName: "Module",
          field: "module",
          cellRenderer: (params) => {
            return toTitleCase(params.value);
          },
        },
        {
          headerName: "Priority",
          field: "priority",
          cellRenderer: (params) => {
            return toTitleCase(params.value);
          },
        },
        {
          headerName: "Actions",
          width: 170,
          maxWidth: 170,
          minWidth: 170,
          field: "actions",
          pinned: "right",
          cellRendererFramework: "supportButton",
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
    };
  },
  computed: {
    ticketList() {
      return this.$store.state.support.ticketList;
    },
    totalPages() {
      return Math.ceil(this.$store.state.support.totalItems / this.itemsPerPage);
    },
    offset() {
      return this.itemsPerPage * (this.pageNo - 1);
    },
    ticket_permissions() {
      return this.$store.state.profile.permissions.ticket;
    }
  },
  methods: {
    nextPage() {
      this.pageNo++;
      this.getTicketList();
    },
    prevPage() {
      this.pageNo--;
      this.getTicketList();
    },
    itemsPerPageChange(value) {
      this.pageNo = 1;
      this.itemsPerPage = value;
      this.getTicketList();
    },
    editTicket() {
      this.formType = "edit";
      this.openTicketForm = true;
    },
    getTicketList() {
      this.filter.limit = this.itemsPerPage;
      this.filter.offset = this.offset;
      this.$store.dispatch("support/GET_TICKETS_DATA", this.filter);
    },
    getTicketListSearching() {
      this.gridOptions.api.setQuickFilter(this.searching_tickets);
    },
    searchTicket() {
      this.pageNo = 1;
      this.getTicketList();
    },
    AddTicket() {
      this.formType = "add";
      this.openTicketForm = true;
    },
  },

  beforeMount() {
    this.getTicketList();
  },
};
</script>