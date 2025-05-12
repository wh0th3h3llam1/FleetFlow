<template>
  <v-dialog
    v-model="openLoadSheetDownlaodDialog"
    persistent
    scrollable
    width="45%"
  >
    <v-card>
      <v-card-title class="background-primary text-white px-3 py-2">
        <span class="text-subtitle-1 text-uppercase"> Picking Sheet </span>
        <v-spacer></v-spacer>
        <v-btn depressed color="white" icon small @click="closeDialog">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>
      <v-card-text class="py-6">
        <v-row>
          <v-col cols="5">
            <v-menu
              v-model="menu1"
              :close-on-content-click="false"
              :nudge-right="40"
              transition="scale-transition"
              offset-y
              min-width="auto"
            >
              <template v-slot:activator="{ on, attrs }">
                <v-text-field
                  v-model="getFromDate"
                  label="From"
                  prepend-inner-icon="mdi-calendar"
                  readonly
                  outlined
                  dense
                  hide-details="auto"
                  v-bind="attrs"
                  v-on="on"
                ></v-text-field>
              </template>
              <v-date-picker
                @change="dateValidator"
                v-model="getFromDate"
                @input="menu1 = false"
              ></v-date-picker>
            </v-menu>
          </v-col>
          <v-col cols="5">
            <v-menu
              v-model="menu2"
              :close-on-content-click="false"
              :nudge-right="40"
              transition="scale-transition"
              offset-y
              min-width="auto"
            >
              <template v-slot:activator="{ on, attrs }">
                <v-text-field
                  v-model="getToDate"
                  label="To"
                  prepend-inner-icon="mdi-calendar"
                  readonly
                  dense
                  outlined
                  hide-details="auto"
                  v-bind="attrs"
                  v-on="on"
                ></v-text-field>
              </template>
              <v-date-picker
                @change="dateValidator"
                v-model="getToDate"
                @input="menu2 = false"
              ></v-date-picker>
            </v-menu>
          </v-col>
          <v-col cols="2" class="d-flex align-center">
            <v-btn
              small
              class="primary elevation-0 text-uppercase"
              @click="downlaodTripSheet"
              :disabled="!isVisilbe"
            >
              <span>download</span>
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>


<script>
import XLSX from "xlsx";
import { toCapitalize } from "~/assets/utils";

export default {
  data() {
    return {
      bulkExcelSheetData: [],
      isVisilbe: false,
      loadSheetData: [],
      fileNameList: [],
      getFromDate: null,
      getToDate: null,
      nowDate: new Date().toISOString().slice(0, 10),
      menu1: false,
      modal: false,
      menu2: false,
      instructionDialog: {
        dialog: false,
        RequestType: null,
      },
      dublicatefileNameList: [],
    };
  },
  props: {
    value: Boolean,
  },
  methods: {
    dateValidator() {
      if (
        this.getFromDate &&
        this.getToDate &&
        this.getFromDate > this.getToDate
      ) {
        let _ = this.getToDate;
        this.getToDate = this.getFromDate;
        this.getFromDate = _;
        this.gettripLoadSheetData();
      } else {
        this.gettripLoadSheetData();
      }
    },
    closeDialog() {
      this.openLoadSheetDownlaodDialog = false;
      this.getFromDate = null;
      this.getToDate = null;
      this.isVisilbe = false;
    },
    formatHeaders(data) {
      return data.map((e, i) => {
        let obj = {};
        Object.keys(e).forEach((header, j) => {
          let h = header.replace(/\_/g, " ");
          obj[toCapitalize(h)] = e[header];
        });
        return obj;
      });
    },
    gettripLoadSheetData() {
      let payload = {
        toDate: this.getFromDate,
        fromDate: this.getToDate,
      };
      this.$store
        .dispatch("trip/GET_TRIP_LOAD_SHEET_DATA", payload)
        .then((response) => {
          if (response && response.length != 0) {
            this.loadSheetData = response;
            this.isVisilbe = true;
          } else {
            this.$notifier.showMessage({
              content: "Trip Sheet Data not found!",
              color: "error",
            });
          }
        })
        .catch((error) => {
          console.log(error);
        });
    },
    downlaodTripSheet() {
      const data = XLSX.utils.json_to_sheet(
        this.formatHeaders(this.loadSheetData)
      );
      const wb = XLSX.utils.book_new();
      wb.Props = {
        Title: this.uploadTo + " Trip Load Sheet excel file",
        Subject: "Trip Load Sheet Excel",
        Author: "chefme",
        CreatedDate: new Date(),
      };

      XLSX.utils.book_append_sheet(wb, data, "data");
      XLSX.writeFile(wb, " Picking-sheet.xlsx");
      this.closeDialog();
    },
  },
  computed: {
    openLoadSheetDownlaodDialog: {
      get() {
        return this.value;
      },
      set(value) {
        this.$emit("input", value);
      },
    },
  },
  mounted() {},
};
</script>
