<template>
  <v-dialog
    v-model="openBulkuploadFormDialog"
    persistent
    scrollable
    width="50%"
  >
    <v-card>
      <v-card-title class="background-primary text-white px-3 py-2">
        <span class="text-subtitle-1 text-uppercase"
          >Temperature Sheet Bulk Upload
        </span>
        <v-spacer></v-spacer>
        <v-btn depressed color="white" icon small @click="closeDialog">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>
      <v-card-text class="py-6">
        <v-form ref="uploadFile">
          <v-row no-gutters>
            <v-col cols="5" class="d-flex justify-space-between">
              <v-file-input
                ref="files"
                hide-details
                multiple="multiple"
                dense
                label="Upload Document"
                prepend-inner-icon="mdi-attachment mdi-rotate-90"
                prepend-icon=""
                accept=".xlsm , .xlsb, .xltx, .xls, .xlsx"
                outlined
                class="pr-4"
                @change="getFileData($event)"
              ></v-file-input>
              <v-icon color="primary" @click="openInstructionDialog">
                mdi-information
              </v-icon>
            </v-col>
            <v-col cols="12" class="pt-6">
              <div v-for="(name, i) in dublicatefileNameList" :key="i">
                <v-alert dense type="error" text dismissible>
                  <v-list
                    class="pa-0"
                    dense
                    outlined
                    style="background: inherit !important"
                  >
                    <v-list-item dense style="min-height: 20px !important">
                      <span class="primary--text"
                        >Duplicate Found {{ i + 1 }} .</span
                      ><span class="primary--text">{{ name }}</span>
                    </v-list-item>
                  </v-list>
                </v-alert>
              </div>
              <div v-for="(name, i) in otherFileSelectedList" :key="i">
                <v-alert dense type="error" text dismissible>
                  <v-list
                    class="pa-0"
                    dense
                    outlined
                    style="background: inherit !important"
                  >
                    <v-list-item dense style="min-height: 20px !important">
                      <span class="primary--text"
                        >This file format is not allowed {{ i + 1 }} .</span
                      ><span class="primary--text">{{ name }}</span>
                    </v-list-item>
                  </v-list>
                </v-alert>
              </div>
            </v-col>
          </v-row>
        </v-form>

        <v-list
          two-line
          subheader
          class="pt-1"
          v-show="bulkExcelSheetData.length"
        >
          <v-subheader>Upload</v-subheader>
          <div v-for="(file, i) in bulkExcelSheetData" :key="i">
            <v-list-item>
              <v-list-item-content class="pa-0">
                <v-card outlined elevation="0">
                  <v-card-title>
                    <v-row>
                      <v-col cols="8">
                        <v-list-item-title>{{ file.name }}</v-list-item-title>
                      </v-col>
                      <v-col cols="4" class="d-flex justify-space-between">
                        <v-list-item-subtitle>
                          {{ getSize(file.size) }}
                        </v-list-item-subtitle>

                        <v-icon small @click="removeFile(i)" class=""
                          >mdi-close</v-icon
                        >
                      </v-col>
                    </v-row>
                  </v-card-title>
                </v-card>
              </v-list-item-content>
            </v-list-item>
          </div>
        </v-list>
      </v-card-text>
      <v-card-actions class="d-flex justify-end pa-4 background-light_grey">
        <v-btn small class="primary elevation-0" @click="SubmitData">
          <span>Submit</span>
        </v-btn>
      </v-card-actions>
    </v-card>
    <CommonDialogInstruction
      :openDialog="instructionDialog"
      @closeDialogBox="closeChildDiaologBox"
    />
  </v-dialog>
</template>


<script>
import XLSX from "xlsx";

export default {
  data() {
    return {
      bulkExcelSheetData: [],
      fileNameList: [],
      instructionDialog: {
        dialog: false,
        RequestType: null,
      },
      dublicatefileNameList: [],
      otherFileSelectedList: [],
    };
  },
  props: {
    value: Boolean,
  },
  methods: {
    openInstructionDialog() {
      this.instructionDialog.dialog = true;
      this.instructionDialog.RequestType = "temperaturesheet";
    },
    closeChildDiaologBox() {
      this.instructionDialog.dialog = false;
    },
    generateFormData(data) {
      let fd = new FormData();
      data.forEach((f, i) => {
        fd.append("files", f);
      });
      return fd;
    },
    getSize(bytes) {
      var sizes = ["Bytes", "KB", "MB", "GB", "TB"];
      if (bytes == 0) return "0 Byte";
      var i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)));
      return Math.round(bytes / Math.pow(1024, i), 2) + " " + sizes[i];
    },
    getFileData(fileInput) {
      if (fileInput) {
        this.dublicatefileNameList = [];
        fileInput.forEach((file, index) => {
          if (this.excelFileCheck(file.name)) {
            this.checkDublicateFile(file);
          } else {
            this.otherFileSelectedList.push(file.name);
          }
        });
      }
    },
    excelFileCheck(fileName) {
      let extension = fileName.slice(
        (Math.max(0, fileName.lastIndexOf(".")) || Infinity) + 1
      );
      if (
        extension == "xlsm" ||
        extension == "xlsb" ||
        extension == "xltx" ||
        extension == "xls" ||
        extension == "xlsx"
      ) {
        return true;
      } else {
        return false;
      }
    },
    checkDublicateFile(file) {
      if (this.fileNameList.includes(file.name)) {
        this.dublicatefileNameList.push(file.name);
      } else {
        this.bulkExcelSheetData.push(file);
        this.fileNameList.push(file.name);
      }
    },
    removeFile(index) {
      this.bulkExcelSheetData.splice(index, 1);
    },
    SubmitData() {
      let payload = this.generateFormData(this.bulkExcelSheetData);
      this.$store
        .dispatch("trip/SET_TEMPRATURE_DATA", payload)
        .then(() => {
          this.$notifier.showMessage({
            content: "Temprature Sheet Uploaded Successfuly!",
            color: "success",
          });
          this.closeDialog();
        })
        .catch((error) => {
          console.log(error);
        });
    },
    closeDialog() {
      this.$refs.files.reset();
      this.openBulkuploadFormDialog = false;
      this.dublicatefileNameList = [];
      this.otherFileSelectedList = [];
      this.fileNameList = [];
      this.bulkExcelSheetData = [];
    },
  },
  computed: {
    openBulkuploadFormDialog: {
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