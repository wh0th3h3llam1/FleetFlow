<template>
  <v-dialog
    v-model="openTagFormDialog"
    persistent
    scrollable
    width="50%"
    @keydown.esc="closeDialog()"
  >
    <v-card>
      <v-card-title class="background-primary text-white px-3 py-2">
        <span
          class="text-lg-subtitle-1 text-xl-h6 text-uppercase font-weight-black"
        >
          Driver Tag
        </span>
        <v-spacer />
        <v-btn
          depressed
          text
          small
          icon
          class="white-text"
          @click="closeDialog()"
        >
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>
      <v-card-text class="pa-5 pt-2">
        <v-form ref="tagFormAdd" id="tagFormAdd" v-model="isValid">
          <v-row class="px-4 pt-7 d-flex align-baseline">
            <v-col cols="5">
              <v-text-field
                v-model="tag_name"
                dense
                label="Add Tag"
                outlined
                :rules="[(v) => !!v || 'Tag name is required']"
                :error-messages="error.tag"
                @input="error.tag = []"
              ></v-text-field>
            </v-col>
            <v-col cols="2">
              <v-btn
                :disabled="!isValid"
                @click.prevent="submitDriverForm()"
                class="primary text-uppercase mr-3"
              >
                <span>add</span>
              </v-btn>
            </v-col>
            <v-col cols="12" class="pt-4">
              <AgGridVue
                @grid-ready="gridReady"
                :grid-options="gridOptions"
                :column-defs="columnDefs"
                :pagination="true"
                :row-data="tagList"
                :paginationPageSize="10"
                style="width: 100%; height: 450px"
                class="ag-theme-material cf-table"
              >
              </AgGridVue>
              <!-- :style="{ width: '100%', height: gridHeight }" -->
            </v-col>
          </v-row>
        </v-form>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
import { AgGridVue } from "ag-grid-vue";
import tagButton from "~/components/common/aggrid/buttons/driverTagButton.vue";
export default {
  components: {
    AgGridVue,
    tagButton,
  },
  props: {
    value: Boolean,
    formType: {
      type: String,
      default: "add",
    },
  },
  data() {
    return {
      isValid: false,
      gridApi: null,
      columnApi: null,
      tag_name: null,
      error: {},
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
      columnDefs: [
        {
          headerName: "Tag Name",
          field: "tag",
        },
        {
          headerName: "Actions",
          width: 170,
          maxWidth: 170,
          minWidth: 170,
          field: "actions",
          pinned: "right",
          cellRendererFramework: "tagButton",
        },
      ],
    };
  },
  computed: {
    tagList: {
      get() {
        return this.$store.state.driver.taglist;
      },
      set(value) {
        this.$store.commit("driver/SET_TAGS", value);
      },
    },
    openTagFormDialog: {
      get() {
        return this.value;
      },
      set(value) {
        this.$emit("input", value);
      },
    },
  },
  methods: {
    gridHeight() {
      return `${window.innerHeight - 296}px`;
    },
    getTaglist() {
      this.$store.dispatch("driver/GET_TAG_LIST");
    },
    gridReady(params) {
      this.gridApi = params.api;
      this.columnApi = params.columnApi;
    },
    submitDriverForm() {
      let pyload = {
        tag: this.tag_name,
        tag_type: "driver_tag",
        description: "1",
      };
      this.$store
        .dispatch("driver/Add_DRIVER_TAG", pyload)
        .then((response) => {
          this.$notifier.showMessage({
            content: "Tag added Successfuly!",
            color: "success",
          });
          this.resetForm();
        })
        .catch((err) => {
          this.error = err;
        });
    },
    resetForm() {
      this.$refs.tagFormAdd.reset();
    },
    closeDialog() {
      this.openTagFormDialog = false;
    },
  },
  mounted() {
    this.getTaglist();
  },
};
</script>