<template>
  <v-dialog
    v-model="bulkUploadDialog"
    persistent
    scrollable
    width="70%"
    max-width="900px"
  >
    <v-card class="pa-4">
      <v-card-title class="d-flex justify-space-between">
        <span
          v-if="uploadTo == 'Orders Update'"
          class="
            text-lg-subtitle-1 text-xl-h6 text-uppercase
            font-weight-black
            primary--text
          "
        >
          Bulk {{ uploadTo }}
        </span>
        <span
          v-else
          class="
            text-lg-subtitle-1 text-xl-h6 text-uppercase
            font-weight-black
            primary--text
          "
        >
          Bulk Upload {{ uploadTo }}
        </span>
        <v-btn depressed fab class="mt-n3" small @click="closeDialog()">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>
      <v-card-text>
        <v-row class="pt-8">
          <v-col cols="5" class="d-flex">
            <v-file-input
              v-model="file"
              hide-details
              dense
              label="Upload Document"
              prepend-inner-icon="mdi-attachment mdi-rotate-90"
              class="mr-4"
              prepend-icon=""
              outlined
              @change="getFileData($event)"
            ></v-file-input>
            <v-icon color="primary" @click="openInstructionDialog"
              >mdi-information</v-icon
            >
          </v-col>
          <v-col cols="7" class="d-flex justify-end">
            <v-btn class="primary" depressed @click="downloadSampleExcel()">
              Download Sample Excel File
            </v-btn>
          </v-col>
          <v-col cols="12" class="d-flex justify-space-between pt-0">
            <span> Total Records : {{ totalRecordCount }}</span>
            <span> Records with Error : {{ rowData.length }}</span>
          </v-col>
          <v-col v-if="distinctErrors.length > 0" class="py-0">
            <v-alert border="left" colored-border color="red">
              <v-row no-gutters>
                <v-col class="grow">
                  <v-list class="py-0">
                    <v-list-item-content class="py-0">
                      <v-list-item-title class="text-grey font-weight-medium"
                        >Error(s):
                      </v-list-item-title>
                      <v-list-item-subtitle
                        class="pl-4 pt-1 text-grey"
                        v-for="(err, index) in distinctErrors"
                        :key="index"
                      >
                        {{ err }}
                      </v-list-item-subtitle>
                    </v-list-item-content>
                  </v-list>
                </v-col>
                <v-col class="shrink">
                  <v-btn
                    class="error"
                    depressed
                    @click="removeAllRecordWithError"
                  >
                    Remove All With Error
                  </v-btn>
                </v-col>
              </v-row>
            </v-alert>
          </v-col>
          <v-col cols="12" v-if="rowData.length > 0">
            <AgGridVue
              @grid-ready="gridReady"
              :grid-options="gridOptions"
              :column-defs="columnDefs"
              :default-col-def="defaultColDef"
              :row-data="rowData"
              style="width: 100%; height: 400px"
              class="ag-theme-material"
            >
            </AgGridVue>
          </v-col>
        </v-row>
      </v-card-text>
      <v-card-actions class="pa-4 d-flex justify-end">
        <v-btn
          color="primary"
          :loading="loading"
          :disabled="!file || rowData.length != 0"
          @click="submitData()"
          >Submit</v-btn
        >
      </v-card-actions>
    </v-card>
    <Instruction
      :openDialog="instructionDialog"
      @closeDialogBox="closeChildDiaologBox"
    />
  </v-dialog>
</template>

<script>
import XLSX from "xlsx";
import { AgGridVue } from "ag-grid-vue";
import Instruction from "@/components/common/dialog/instruction";
import RemoveRowButtonBulkUpload from "@/components/common/aggrid/buttons/removeRowButtonBulkUpload";
import stringCompare from "~/assets/js/string-compare";
import triporderscardVue from '../../trip/triporderscard.vue';

export default {
  components: {
    AgGridVue,
    Instruction,
    RemoveRowButtonBulkUpload,
  },
  props: {
    value: Boolean,
    uploadTo: {
      required: true,
      type: String,
    },
  },
  data() {
    return {
      instructionDialog: {
        dialog: false,
        RequestType: null,
      },
      loading: false,
      file: null,
      fulldata: [],
      rowData: [],
      columnDefs: [],
      _reqFields: [],
      _allFields: null,
      gridApi: null,
      columnApi: null,
      gridOptions: {
        headerHeight: 40,
        rowHeight: 40,
        rowSelection: "multiple",
        suppressRowClickSelection: true,
        suppressDragLeaveHidesColumns: true,
        enableCellTextSelection: true,
      },
      defaultColDef: {
        lockPosition: true,
      },
      requiredHeaders: [],
      serverErrors: [],
    };
  },
  computed: {
    totalRecordCount() {
      return this.fulldata.filter((obj) => Object.keys(obj).length !== 0)
        .length;
    },
    bulkUploadDialog: {
      get() {
        return this.value;
      },
      set(value) {
        this.$emit("input", value);
      },
    },
    ordersFields() {
      return [
        {
          name: "SO Number*",
          key: "reference_number",
          type: "string",
          required: true,
          matchRatio: 0.95,
        },
        {
          name: "Customer Code*",
          key: "customer_code",
          type: "number",
          required: true,
          matchRatio: 0.95,
        },
        {
          name: "Delivery Date*",
          key: "delivery_date",
          type: "string",
          required: true,
          matchRatio: 0.95,
        },
        {
          name: "Item No*",
          key: "item_no",
          type: "number",
          required: true,
          matchRatio: 0.9,
        },
        {
          name: "Quantity*",
          key: "quantity",
          type: "number",
          required: true,
          matchRatio: 0.9,
        },
      ];
    },
    itemFields() {
      return [
        {
          name: "Item No*",
          key: "item_no",
          type: "id",
          required: true,
          matchRatio: 0.9,
        },
        {
          name: "Storage Type*",
          key: "storage_type",
          type: "string",
          required: true,
          matchRatio: 0.9,
        },
        {
          name: "Weight*",
          key: "weight",
          type: "number",
          required: true,
          dp: 4,
          matchRatio: 0.98,
        },
        {
          name: "Volume (CBM)*",
          key: "cbm",
          type: "number",
          required: true,
          dp: 7,
          matchRatio: 0.9,
        },
        {
          name: "Item name*",
          key: "item_description",
          type: "string",
          required: true,
          matchRatio: 0.8,
        },
        {
          name: "Case Factor*",
          key: "case_factor",
          type: "number",
          required: true,
          dp: 5,
          matchRatio: 0.9,
        },
        {
          name: "Length*",
          key: "length",
          type: "number",
          required: true,
          dp: 5,
          matchRatio: 0.98,
        },
        {
          name: "Width*",
          key: "width",
          type: "number",
          required: true,
          dp: 5,
          matchRatio: 0.98,
        },
        {
          name: "Height*",
          key: "height",
          type: "number",
          required: true,
          dp: 5,
          matchRatio: 0.98,
        },
        {
          name: "Unit*",
          key: "unit",
          type: "string",
          required: true,
          matchRatio: 0.95,
        },
      ];
    },
    customerAddressFields() {
      return [
        {
          name: "Longitude*",
          key: "longitude",
          type: "number",
          dp: 7,
          required: true,
          merge_into: "coordinates",
          merge_type: "object",
          matchRatio: 0.94,
        },
        {
          name: "Latitude*",
          key: "latitude",
          type: "number",
          dp: 7,
          required: true,
          merge_into: "coordinates",
          merge_type: "object",
          matchRatio: 0.94,
        },
        {
          name: "Customer Code*",
          key: "customer_code",
          type: "id",
          required: true,
          matchRatio: 0.95,
        },
        {
          name: "Customer Name*",
          key: "customer_name",
          type: "string",
          required: true,
          matchRatio: 0.95,
        },
        {
          name: "Customer Type",
          key: "customer_type",
          type: "string",
          required: false,
          matchRatio: 0.95,
        },
        {
          name: "Customer Number",
          key: "contact_number",
          type: "string",
          required: false,
          matchRatio: 0.95,
        },
        {
          name: "Contact Email*",
          key: "contact_email",
          type: "string",
          required: true,
          matchRatio: 0.95,
        },
        {
          name: "Contact Person",
          key: "contact_person",
          type: "string",
          required: false,
          matchRatio: 0.95,
        },
        {
          name: "Address*",
          key: "address",
          type: "string",
          required: true,
          matchRatio: 0.94,
        },
        {
          name: "Project Id*",
          key: "project",
          type: "string",
          required: true,
          matchRatio: 0.94,
        },
        {
          name: "From time*",
          key: "from_time",
          type: "time",
          required: true,
          matchRatio: 0.95,
        },
        {
          name: "To time*",
          key: "to_time",
          type: "time",
          required: true,
          matchRatio: 0.95,
        },
        {
          name: "Remarks",
          key: "remarks",
          type: "string",
          required: false,
          matchRatio: 0.94,
        },
        {
          name: "Processing time",
          key: "processing_time",
          type: "number",
          required: false,
          matchRatio: 0.9,
        },
        {
          name: "Whatsapp Notification",
          key: "whatsapp_notification",
          type: "boolean",
          required: false,
          matchRatio: 0.94,
        },
        {
          name: "Email Notification",
          key: "email_notification",
          type: "boolean",
          required: false,
          matchRatio: 0.94,
        },
        {
          name: "Tags",
          key: "tags",
          type: "string",
          required: false,
          matchRatio: 0.94,
        },
      ];
    },
    vehicleFields() {
      return [
        {
          name: "Licence Plate No *",
          key: "vehicle_plate_no",
          type: "string",
          required: true,
          matchRatio: 0.8,
        },
        {
          name: "Vehicle Make*",
          key: "vehicle_make",
          type: "string",
          required: true,
          matchRatio: 0.92,
        },
        {
          name: "Vehicle Model*",
          key: "vehicle_model",
          type: "string",
          required: true,
          matchRatio: 0.92,
        },
        {
          name: "Vehicle Year*",
          key: "vehicle_year",
          type: "string",
          required: true,
          matchRatio: 0.92,
        },
        {
          name: "Vehicle Cost*",
          key: "vehicle_cost",
          type: "string",
          required: true,
          matchRatio: 0.92,
        },
        {
          name: "Odometer Reading*",
          key: "mileage",
          type: "string",
          required: true,
          matchRatio: 0.95,
        },
        {
          name: "Project Id*",
          key: "project",
          type: "string",
          required: true,
          matchRatio: 0.9,
        },
        {
          name: "Fuel Type*",
          key: "fuel_type",
          type: "string",
          required: true,
          matchRatio: 0.9,
        },
        {
          name: "Tonnage Capacity*",
          key: "tonnage_capacity",
          type: "number",
          dp: 2,
          required: true,
          matchRatio: 0.95,
        },
        {
          name: "CBM Capacity*",
          key: "cbm_capacity",
          type: "number",
          dp: 2,
          required: true,
          matchRatio: 0.95,
        },
        {
          name: "Box Capacity",
          key: "box_capacity",
          type: "number",
          dp: 0,
          required: false,
          matchRatio: 0.95,
        },
        {
          name: "Permits*",
          key: "permits",
          type: "string",
          required: true,
          matchRatio: 0.95,
        },
        {
          name: "Insurance Policy Number*",
          key: "insurance_policy_number",
          type: "string",
          required: true,
          matchRatio: 0.9,
        },
        {
          name: "Insurance Expiry Date",
          key: "insurance_expiry_date",
          type: "date",
          required: false,
          matchRatio: 0.9,
        },
        {
          name: "Insurance Type",
          key: "insurance_type",
          type: "string",
          required: false,
          matchRatio: 0.95,
        },
        {
          name: "RC Number*",
          key: "rc_number",
          type: "string",
          required: true,
          matchRatio: 0.95,
        },
        {
          name: "RC Expiry Date*",
          key: "rc_expiry_date",
          type: "date",
          required: true,
          matchRatio: 0.95,
        },
        {
          name: "Status",
          key: "status",
          type: "string",
          required: false,
          matchRatio: 0.95,
        },
        {
          name: "Storages*",
          key: "available_storages",
          type: "string",
          required: true,
          matchRatio: 0.94,
        },
        {
          name: "Sensor Ids",
          key: "sensor_info",
          type: "string",
          required: false,
          matchRatio: 0.94,
        },
        {
          name: "Tags",
          key: "tags",
          type: "string",
          required: false,
          matchRatio: 0.94,
        },
      ];
    },
    driverFields() {
      return [
        {
          name: "First Name*",
          key: "first_name",
          type: "string",
          required: true,
          matchRatio: 0.95,
        },
        {
          name: "Last Name*",
          key: "last_name",
          type: "string",
          required: true,
          matchRatio: 0.95,
        },
        {
          name: "Username*",
          key: "username",
          type: "string",
          required: true,
          matchRatio: 0.95,
        },
        {
          name: "Password*",
          key: "password",
          type: "string",
          required: true,
          matchRatio: 0.9,
        },
        {
          name: "Contact Number*",
          key: "contact_number",
          type: "string",
          required: true,
          matchRatio: 0.95,
        },
        {
          name: "Project Id*",
          key: "project",
          type: "string",
          required: true,
          matchRatio: 0.9,
        },
        {
          name: "License Expiry*",
          key: "license_expiry",
          type: "date",
          required: true,
          matchRatio: 0.95,
        },
        {
          name: "License Number*",
          key: "license_number",
          type: "string",
          required: true,
          matchRatio: 0.95,
        },
        {
          name: "Nationality",
          key: "nationality",
          type: "string",
          required: false,
          matchRatio: 0.95,
        },
        {
          name: "Service Type",
          key: "service_type",
          type: "string",
          required: false,
          matchRatio: 0.9,
        },
        {
          name: "National Id Expiry*",
          key: "national_id_expiry",
          type: "date",
          required: true,
          matchRatio: 0.95,
        },
        {
          name: "Salary",
          key: "salary",
          type: "number",
          dp: 2,
          required: false,
          matchRatio: 0.9,
        },
        {
          name: "Health Card Number",
          key: "health_card_number",
          type: "string",
          required: false,
          matchRatio: 0.95,
        },
        {
          name: "Health Card Expiry",
          key: "health_card_expiry",
          type: "date",
          required: false,
          matchRatio: 0.95,
        },
        {
          name: "Shift Start*",
          key: "shift_start",
          type: "time",
          required: true,
          matchRatio: 0.95,
        },
        {
          name: "Shift End*",
          key: "shift_end",
          type: "time",
          required: true,
          matchRatio: 0.95,
        },
        {
          name: "Zone",
          key: "zone",
          type: "string",
          required: false,
          matchRatio: 0.95,
        },
        {
          name: "Vehicle Assigned",
          key: "vehicle_assigned",
          type: "string",
          required: false,
          matchRatio: 0.95,
        },
        {
          name: "Status",
          key: "status",
          type: "string",
          required: false,
          matchRatio: 0.95,
        },
      ];
    },
    distinctErrors() {
      let err = [];

      this.serverErrors
        .filter((e) => {
          return Object.keys(e).length > 0;
        })
        .map((m) => {
          return Object.keys(m).map((k) => {
            return m[k];
          });
        })
        .forEach((r) => {
          r.forEach((s) => {
            err = [...new Set([...err, ...s])];
          });
        });
      return err;
    },
    bulkUpdateFields() {
      return [
        {
          name: "SO Number*",
          key: "reference_number",
          type: "string",
          required: true,
          matchRatio: 0.94,
        },
        {
          name: "Invoice Number*",
          key: "invoice_number",
          type: "string",
          required: true,
          matchRatio: 0.94,
        },
        {
          name: "Delivery Date*",
          key: "execution_date",
          type: "date",
          required: true,
          matchRatio: 0.94,
        },
        {
          name: "Payment Type",
          key: "payment_type",
          type: "string",
          required: false,
          matchRatio: 0.94,
        },
        {
          name: "Order Value",
          key: "order_value",
          type: "string",
          required: false,
          matchRatio: 0.94,
        },
        {
          name: "Proof of Delivery",
          key: "require_proof_of_delivery",
          type: "string",
          required: false,
          matchRatio: 0.94,
        },
      ];
    },
    bulkUploadB2CFields() {
      return [
        {
          name: "Item No*",
          key: "item_no",
          type: "string",
          required: true,
          matchRatio: 0.94,
        },
        {
          name: "SO Number*",
          key: "reference_number",
          type: "string",
          required: true,
          matchRatio: 0.94,
        },
        {
          name: "Delivery Date*",
          key: "delivery_date",
          type: "date",
          required: true,
          matchRatio: 0.94,
        },
        {
          name: "Quantity*",
          key: "quantity",
          type: "string",
          required: true,
          matchRatio: 0.94,
        },
        {
          name: "Customer Number*",
          key: "customer_number",
          type: "string",
          required: true,
          matchRatio: 0.94,
        },
        {
          name: "Customer Name*",
          key: "customer_name",
          type: "string",
          required: true,
          matchRatio: 0.94,
        },
        {
          name: "Customer Type*",
          key: "customer_type",
          type: "string",
          required: true,
          matchRatio: 0.94,
        },
        {
          name: "Contact Email*",
          key: "contact_email",
          type: "string",
          required: true,
          matchRatio: 0.94,
        },
        {
          name: "Project Id*",
          key: "project_id",
          type: "string",
          required: true,
          matchRatio: 0.94,
        },
        {
          name: "Processing Time",
          key: "processing_time",
          type: "number",
          required: false,
          matchRatio: 0.94,
        },
        {
          name: "Address*",
          key: "address",
          type: "string",
          required: true,
          matchRatio: 0.94,
        },
        {
          name: "Latitude*",
          key: "latitude",
          type: "number",
          dp: 6,
          required: true,
          matchRatio: 0.94,
        },
        {
          name: "Longitude*",
          key: "longitude",
          type: "number",
          dp: 6,
          required: true,
          matchRatio: 0.94,
        },
        {
          name: "From Time*",
          key: "from_time",
          type: "time",
          required: true,
          matchRatio: 0.94,
        },
        {
          name: "To Time*",
          key: "to_time",
          type: "time",
          required: true,
          matchRatio: 0.94,
        },
        {
          name: "Whatsapp Notification",
          key: "whatsapp_notification",
          type: "boolean",
          required: false,
          matchRatio: 0.94,
        },
        {
          name: "Email Notification",
          key: "email_notification",
          type: "boolean",
          required: false,
          matchRatio: 0.94,
        },
        {
          name: "Tags",
          key: "tags",
          type: "string",
          required: false,
          matchRatio: 0.94,
        },
      ];
    },
  },
  methods: {
    openInstructionDialog() {
      this.instructionDialog.dialog = true;
      this.instructionDialog.RequestType = this.uploadTo;
    },
    closeChildDiaologBox() {
      this.instructionDialog.dialog = false;
    },
    gridReady(params) {
      this.gridApi = params.api;
      this.columnApi = params.columnApi;
    },
    setMandatoryFields() {
      if (this.uploadTo == "Orders") {
        this._reqFields = this.ordersFields.filter((f) => f.required);
        this._allFields = this.ordersFields;
      }
      if (this.uploadTo == "Orders Update") {
        this._reqFields = this.bulkUpdateFields.filter((f) => f.required);
        this._allFields = this.bulkUpdateFields;
      }
      if (this.uploadTo == "B2C Orders") {
        this._reqFields = this.bulkUploadB2CFields.filter((f) => f.required);
        this._allFields = this.bulkUploadB2CFields;
      }
      if (this.uploadTo == "Items") {
        this._reqFields = this.itemFields.filter((f) => f.required);
        this._allFields = this.itemFields;
      }
      if (this.uploadTo == "Customer Addresses") {
        this._reqFields = this.customerAddressFields.filter((f) => f.required);
        this._allFields = this.customerAddressFields;
      }
      if (this.uploadTo == "Vehicles") {
        this._reqFields = this.vehicleFields.filter((f) => f.required);
        this._allFields = this.vehicleFields;
      }
      if (this.uploadTo == "Drivers") {
        this._reqFields = this.driverFields.filter((f) => f.required);
        this._allFields = this.driverFields;
      }
    },
    getFileData(file) {
      if (file) {
        this.loading = true;
        let reader = new FileReader();

        this.setMandatoryFields();

        reader.onload = async () => {
          /**
           * Clear previous data if any
           */
          this.excelData = [];

          /**
           * Read the uploaded file
           */
          let fileData = reader.result;
          let wb = XLSX.read(fileData, {
            type: "binary",
          });

          if (await this.hasMissingHeader(wb.Sheets[wb.SheetNames[0]])) {
            return;
          }

          let rowData = XLSX.utils.sheet_to_row_object_array(
            wb.Sheets[wb.SheetNames[0]]
          );

          /** Check if other headers are present. */
          let filterdData = await this.checkData(rowData);

          this.setData(filterdData);
        };

        reader.readAsBinaryString(file);
      } else {
        this.clearDialogData();
      }
    },
    async hasMissingHeader(sheetData) {
      let headers = XLSX.utils
        .sheet_to_csv(sheetData)
        .split(/\r?\n/)[0]
        .split(",");

      let missingHeaders = await this.getMissingHeaders(headers);

      if (missingHeaders.length > 0) {
        this.clearDialogData();
        this.loading = false;
        alert("Column(s) '" + missingHeaders.join(", ") + "' are missing");
        return true;
      } else {
        this.correctSpellingMistakesInHeaders(headers);
        return false;
      }
    },
    async getMissingHeaders(headers) {
      let missingFields = [];
      this._reqFields.forEach((_field, index) => {
        let field = headers.find((head, index) => {
          return (
            stringCompare.compareTwoStrings(_field.name, head) >=
              _field.matchRatio ||
            stringCompare.compareTwoStrings(_field.key, head) >=
              _field.matchRatio
          );
        });
        if (!field) {
          missingFields.push(_field.name);
        }
      });
      return missingFields;
    },
    correctSpellingMistakesInHeaders(headers) {
      headers.forEach((header, index) => {
        let keyConfig = this.getKeyConfig(header);
        headers[index] = keyConfig.name;
        if (headers.length - 1 == index) {
          this.setHeaders(headers);
        }
      });
    },
    async checkData(rowObj) {
      let data = [];
      let dataWithError = [];

      rowObj.forEach((obj, index) => {
        Object.keys(obj).forEach((k) => {
          if (typeof obj[k] == "object") {
            let __o;
            if (Array.isArray(obj[k])) {
              __o = obj[k][0];
            } else {
              __o = obj[k];
            }
            Object.keys(__o).forEach((__k) => {
              obj[__k] = __o[__k];
            });
            delete obj[k];
          }
        });

        obj = this.correctSpellingMistakesInKeys(obj);

        let keys = Object.keys(obj);

        let missingFields = this.checkMissingFieldsForRecord(keys);

        if (missingFields.length > 0 || this.hasServerError(index)) {
          obj.oldIndex = index;
          dataWithError.push(obj);
          let err = {};
          missingFields.forEach((mf) => {
            err[mf.key] = [`${mf.name} is Required`];
          });
          this.serverErrors.push(err);
        } else {
          this.serverErrors.push({});
        }

        keys.forEach((name) => {
          let type = this.getKeyConfig(name);
          if (type) {
            if (type.key != name) {
              obj[type.key] = obj[name];
              delete obj[name];
            }

            if (type.type === "date" || type.type === "time") {
              obj[type.key] = this.getDate(obj[type.key], type.type);
            }
            if (type.type === "number" && type.dp) {
              obj[type.key] = Number.parseFloat(obj[type.key]).toFixed(type.dp);
            }
            if (type.merge_into) {
              if (!obj[type.merge_into]) {
                if (type.merge_type == "array") {
                  obj[type.merge_into] = [{}];
                } else {
                  obj[type.merge_into] = {};
                }
              }
              if (type.merge_type == "array") {
                obj[type.merge_into][0][type.key] = obj[type.key];
              } else {
                obj[type.merge_into][type.key] = obj[type.key];
              }
              delete obj[type.key];
            }
          }
        });
        data.push(obj);
      });

      return { data: data, dataWithError: dataWithError };
    },
    correctSpellingMistakesInKeys(object) {
      let obj = {};
      Object.keys(object).forEach((key, index) => {
        let keyConfig = this.getKeyConfig(key);
        obj[keyConfig.name] = object[key];
      });
      return obj;
    },
    getKeyConfig(name) {
      let field = this._allFields.find((f) => {
        return (
          stringCompare.compareTwoStrings(f.name, name.trim()) >=
            f.matchRatio ||
          stringCompare.compareTwoStrings(f.key, name.trim()) >= f.matchRatio
        );
      });

      if (field) {
        return field;
      } else {
        return null;
      }
    },
    async setData(filterdData) {
      this.fulldata = filterdData.data;
      if (filterdData.dataWithError.length > 0) {
        this.rowData = filterdData.dataWithError;
      }
      this.loading = false;
    },
    hasServerError(index) {
      if (
        this.serverErrors &&
        this.serverErrors.length > 0 &&
        this.serverErrors[index] &&
        Object.keys(this.serverErrors[index]).length > 0
      ) {
        return true;
      } else {
        return false;
      }
    },
    checkMissingFieldsForRecord(fields) {
      return this._reqFields.filter((field) => {
        let map = fields.map((k) => {
          return k.trim();
        });

        return map.indexOf(field.name) == -1 && map.indexOf(field.key) == -1;
      });
    },
    async checkEditedRecord(param) {
      if (param.newValue == param.oldValue) {
        return null;
      }

      let record = param.data;

      let keys = Object.keys(record);
      let i = 0;

      while (i < keys.length) {
        let k = keys[i];
        if (typeof record[k] == "object") {
          let __o;
          if (Array.isArray(record[k])) {
            __o = record[k][0];
          } else {
            __o = record[k];
          }
          Object.keys(__o).forEach((__k) => {
            record[__k] = __o[__k];
          });
        }
        i++;
      }

      keys = Object.keys(record);

      let _errhead = this._reqFields.filter((f) => {
        let hasKey =
          keys.indexOf(f.key.toLowerCase().replace(/\ /g, "_")) == -1;

        if (f.merge_into) {
          delete record[f.key];
        }

        return hasKey;
      });

      if (_errhead.length > 0) {
        return null;
      }

      let reqKeys = this._reqFields.map((k) => {
        return k.key;
      });

      while (i < reqKeys.length) {
        let type = this.getKeyConfig(reqKeys[i]);

        if (record[type.key] == null || record[type.key] == "") {
          return null;
        } else {
          if (type) {
            if (type.type == "number" && type.dp) {
              record[type.key] = parseFloat(record[type.key]).toFixed(type.dp);
            }
          }
        }
        i++;
      }

      this.rowData.splice(
        this.rowData.indexOf(
          this.rowData.find((d) => d.oldIndex == record.oldIndex)
        ),
        1
      );
      let index = record.oldIndex;
      delete record.oldIndex;
      this.fulldata.splice(index, 1, record);

      if (this.rowData.length == 0) {
        this.serverErrors = [];
      }
    },
    removeAllRecordWithError() {
      while (this.rowData.length > 0) {
        this.removeDataFromRow(this.rowData[0].oldIndex, 0);
      }
    },
    removeDataFromRow(oldIndex, currentIndex) {
      this.fulldata.splice(oldIndex, 1, {});
      this.rowData.splice(currentIndex, 1);

      let data = this.fulldata.filter((obj) => Object.keys(obj).length !== 0);

      if (data.length == 0) {
        this.clearDialogData();
      }

      if (this.rowData.length == 0) {
        this.serverErrors = [];
      }
    },
    async setHeaders(headers) {
      this.columnDefs = [];

      headers.forEach((header) => {
        let field = this.getKeyConfig(header);
        let key = field.key;
        header = field.name;

        if (field.merge_into) {
          key = `${field.merge_into}.${field.key}`;
        }

        let obj = {
          headerName: header,
          field: key,
          editable: true,
          onCellValueChanged: (param) => {
            this.checkEditedRecord(param);
          },
        };

        obj.cellClass = (param) => {
          let f = param.colDef.field.split(".");
          let field = f[f.length - 1];
          if (
            this.serverErrors.length > 0 &&
            Object.keys(param.data).indexOf("oldIndex") > -1 &&
            Array.isArray(this.serverErrors[param.data.oldIndex][field])
          ) {
            return "cell-error";
          }
        };

        this.columnDefs.push(obj);
      });
      this.columnDefs.push({
        headerName: "Action",
        pinned: "right",
        width: 90,
        cellRendererFramework: "RemoveRowButtonBulkUpload",
      });
    },
    getDate(serial, type) {
      if (typeof serial == "number") {
        let utc_days = Math.floor(serial - 25569);
        let utc_value = utc_days * 86400;
        let date_info = new Date(utc_value * 1000);

        let fractional_day = serial - Math.floor(serial) + 0.0000001;

        let total_seconds = Math.floor(86400 * fractional_day);

        let seconds = total_seconds % 60;

        total_seconds -= seconds;

        let hours = Math.floor(total_seconds / (60 * 60));
        let minutes = Math.floor(total_seconds / 60) % 60;

        if (hours < 10) {
          hours = "0" + hours;
        }
        if (minutes < 10) {
          minutes = "0" + minutes;
        }

        if (type == "date") {
          return [
            date_info.getFullYear(),
            date_info.getMonth() + 1,
            date_info.getDate(),
          ].join("-");
        } else {
          return [hours, minutes].join(":");
        }
      } else {
        return serial;
      }
    },
    getSheetData() {
      if (this.uploadTo == "Orders") {
        let ws = XLSX.utils.json_to_sheet(
          this.$store.state.bulk_upload.orderSampleData
        );
        return ws;
      } else if (this.uploadTo == "Items") {
        let ws = XLSX.utils.json_to_sheet(
          this.$store.state.bulk_upload.itemSampleData
        );
        return ws;
      } else if (this.uploadTo == "Customer Addresses") {
        let ws = XLSX.utils.json_to_sheet(
          this.$store.state.bulk_upload.customerAddressSampleData
        );
        return ws;
      } else if (this.uploadTo == "Vehicles") {
        let ws = XLSX.utils.json_to_sheet(
          this.$store.state.bulk_upload.vehiclesSampleData
        );
        return ws;
      } else if (this.uploadTo == "Drivers") {
        let ws = XLSX.utils.json_to_sheet(
          this.$store.state.bulk_upload.driversSampleData
        );
        return ws;
      } else if (this.uploadTo == "Orders Update") {
        let ws = XLSX.utils.json_to_sheet(
          this.$store.state.bulk_upload.bulkUpdateSampleData
        );
        return ws;
      } else if (this.uploadTo == "B2C Orders") {
        let ws = XLSX.utils.json_to_sheet(
          this.$store.state.bulk_upload.bulkUploadOrderB2CSampleData
        );
        return ws;
      } else {
        let ws = XLSX.utils.json_to_sheet([]);
        return ws;
      }
    },
    downloadSampleExcel() {
      var wb = XLSX.utils.book_new();
      wb.Props = {
        Title: this.uploadTo + " Sample excel file",
        Subject: "Sample Excel",
        Author: "Fero",
        CreatedDate: new Date(),
      };

      wb.SheetNames.push(`${this.uploadTo} Sheet`);

      wb.Sheets[`${this.uploadTo} Sheet`] = this.getSheetData();

      var wbout = XLSX.write(wb, { bookType: "xlsx", type: "binary" });

      let blob = new Blob([this.s2ab(wbout)], {
        type: "application/octet-stream",
      });

      this.download(blob);
    },
    s2ab(s) {
      var buf = new ArrayBuffer(s.length);
      var view = new Uint8Array(buf);
      for (var i = 0; i < s.length; i++) view[i] = s.charCodeAt(i) & 0xff;
      return buf;
    },
    download(blob) {
      let url = window.URL.createObjectURL(blob);

      let a = document.createElement("a");
      a.href = url;
      a.download = this.uploadTo + " Sample excel file.xlsx";
      a.click();
      window.URL.revokeObjectURL(url);
    },
    submitData() {
      this.loading = true;

      this.serverErrors = [];
      this.fulldata = this.fulldata.filter((obj) => {
        return Object.keys(obj).length !== 0;
      });

      if (this.fulldata.length == 0) {
        this.clearDialogData();
        return null;
      }

      let url;
      let payload, actionName;
      if (this.uploadTo == "Customer Addresses") {
        url = "customer/customerAddress/ADD_CUSTOMER_ADDRESS_DETAILS";
        payload = {
          isBulkupload: true,
          data: this.fulldata,
        };
      }
      if (this.uploadTo == "Items") {
        url = "item/ADD_ITEM";
        payload = {
          isBulkupload: true,
          data: this.fulldata,
        };
      }
      if (this.uploadTo == "Orders") {
        /**
         * Data from this url is not dynamicly updated
         * because list of orders have scroll pagination
         */
        url = "bulk_upload/UPLOAD_ORDERS";
        payload = this.fulldata;
        actionName = "order/orderListStore/GET_ALL_ORDERS";
      }
      if (this.uploadTo == "Orders Update") {
        url = "bulk_upload/UPDATE_ORDERS";
        payload = this.fulldata;
      }
      if (this.uploadTo == "B2C Orders") {
        url = "bulk_upload/UPLOAD_B2C_ORDERS";
        payload = this.fulldata;
      }
      if (this.uploadTo == "Vehicles") {
        url = "vehicle/ADD_VEHICLE";
        payload = this.fulldata;
      }
      if (this.uploadTo == "Drivers") {
        url = "driver/ADD_DRIVER";
        payload = {
          isBulkupload: true,
          data: this.fulldata,
        };
      }

      this.$store
        .dispatch(url, payload)
        .then((resp) => {
          if (this.uploadTo == "Vehicles") {
            this.$parent.getAllVehicles();
          }
          if (this.uploadTo == "Orders Update") {
            this.$parent.get_order_list(true);
          }
          if (this.uploadTo == "B2C Orders") {
            this.$parent.get_order_list(true);
          }
          if (this.uploadTo == "Customer Addresses") {
            this.$parent.getCustomerAddresses();
          }
          if (this.uploadTo == "Drivers") {
            this.$parent.get_drivers_list();
          }

          this.loading = false;
          this.$notifier.showMessage({
            content: "Successfully added ",
            color: "success",
          });
          if (actionName) {
            this.$store.dispatch(actionName, true);
          }
          this.serverErrors = [];
          this.closeDialog();
        })
        .catch(async (err) => {
          if (err) {
            this.serverErrors = err;
            let filterdData = await this.checkData(this.fulldata);
            this.setData(filterdData);
          }

          this.$notifier.showMessage({
            content: "Error Uploading Sheet",
            color: "error",
          });
          this.loading = false;
        });
    },
    closeDialog() {
      this.bulkUploadDialog = false;
      this.clearDialogData();
    },
    clearDialogData() {
      this.file = null;
      this.fulldata = [];
      this.rowData = [];
      this._reqFields = [];
      this.serverErrors = [];
    },
  },
};
</script>

<style>
</style>
