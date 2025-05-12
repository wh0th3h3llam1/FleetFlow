<template>
  <v-dialog
    v-model="addVehicleFormDialog"
    persistent
    scrollable
    width="70%"
    max-width="60%"
  >
    <v-card class="pa-4">
      <v-card-title
        class="
          text-lg-subtitle-1 text-xl-h6 text-uppercase
          font-weight-black
          primary--text
          pb-4
        "
      >
        <span>{{ formType }} Vehicle</span>
        <v-spacer />
        <v-btn
          depressed
          text
          small
          icon
          class="primary-text"
          @click="closeDialog()"
        >
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>
      <v-card-text class="pa-5 pt-2" ref="vehicleSectionForm">
        <v-alert v-if="nonFieldError.length" dense type="error">
          <v-list
            class="pa-0"
            dense
            style="background: inherit !important"
            v-for="(error, i) in nonFieldError"
            :key="i"
          >
            <v-list-item dense style="min-height: 20px !important">
              <span>{{ i }} .</span><span>{{ error }}</span>
            </v-list-item>
          </v-list>
        </v-alert>
        <v-form
          v-if="addVehicleFormDialog"
          v-model="isValid"
          ref="vehicleForm"
          id="vehicleForm"
        >
          <v-row>
            <v-col cols="6" lg="4">
              <v-text-field
                outlined
                :rules="[(v) => !!v || 'Vehicle number is required']"
                name="vehicle_plate_no"
                :error-messages="error.vehicle_plate_no"
                :value="vehicleFormDetails.vehicle_plate_no"
                hide-details="auto"
                label="Vehicle number*"
                class="background-white"
                @input="syncData($event, 'vehicle_plate_no')"
              ></v-text-field>
            </v-col>
            <v-col cols="6" lg="4">
              <v-select
                outlined
                :rules="[(v) => !!v || 'Project is required']"
                name="project"
                :error-messages="error.project"
                :items="allProjects"
                hide-details="auto"
                label="Select Project*"
                class="background-white"
                :value="vehicleFormDetails.project"
                @change="syncData($event, 'project')"
                :menu-props="{ offsetY: true }"
              ></v-select>
            </v-col>
            <v-col cols="6" lg="4">
              <v-select
                outlined
                :rules="[(v) => !!v || 'Fuel type is required']"
                name="fuel_type"
                :error-messages="error.fuel_type"
                hide-details="auto"
                label="Fuel Type*"
                :items="fuelType"
                item-text="title"
                item-value="value"
                class="background-white"
                :value="vehicleFormDetails.fuel_type"
                @change="syncData($event, 'fuel_type')"
                :menu-props="{ offsetY: true }"
              ></v-select>
            </v-col>
            <v-col cols="6" lg="4">
              <v-text-field
                type="number"
                name="tonnage_capacity"
                :error-messages="error.tonnage_capacity"
                :rules="[(v) => !!v || 'Tonnage capacity is required']"
                step="0.01"
                min="0"
                outlined
                hide-details="auto"
                label="Tonnage Capacity*"
                class="background-white"
                :value="vehicleFormDetails.tonnage_capacity"
                @input="syncData($event, 'tonnage_capacity')"
              ></v-text-field>
            </v-col>
            <v-col cols="6" lg="4">
              <v-text-field
                outlined
                name="cbm_capacity"
                :error-messages="error.cbm_capacity"
                step="0.01"
                min="0"
                :rules="[(v) => !!v || 'CBM capacity is required']"
                type="number"
                hide-details="auto"
                label="CBM Capacity*"
                class="background-white"
                :value="vehicleFormDetails.cbm_capacity"
                @input="syncData($event, 'cbm_capacity')"
              ></v-text-field>
            </v-col>
            <v-col cols="6" lg="4">
              <v-text-field
                outlined
                name="box_capacity"
                :error-messages="error.box_capacity"
                type="number"
                hide-details="auto"
                label="Box Capacity"
                class="background-white"
                max="999"
                :value="vehicleFormDetails.box_capacity"
                @input="syncData($event, 'box_capacity')"
              ></v-text-field>
            </v-col>
            <v-col cols="6" lg="4">
              <v-text-field
                :rules="[(v) => !!v || 'Vehicle Permits is required']"
                outlined
                :error-messages="error.permits"
                name="permits"
                hide-details="auto"
                label="Permits*"
                class="background-white"
                :value="vehicleFormDetails.permits"
                @input="syncData($event, 'permits')"
              ></v-text-field>
            </v-col>
            <v-col cols="6" lg="4">
              <v-text-field
                outlined
                :rules="[(v) => !!v || 'Insurance number is required']"
                name="insurance_policy_number"
                hide-details="auto"
                label="Insurance number*"
                :value="vehicleFormDetails.insurance_policy_number"
                @input="syncData($event, 'insurance_policy_number')"
              ></v-text-field>
            </v-col>
            <v-col cols="6" lg="4">
              <v-menu
                ref="insuranceExpiryDatePicker"
                v-model="insuranceExpiryDatePicker"
                :close-on-content-click="false"
                :return-value.sync="insuranceExpiryDate"
                transition="scale-transition"
                min-width="auto"
                offset-y
              >
                <template v-slot:activator="{ on, attrs }">
                  <v-text-field
                    name="insurance_expiry_date"
                    :error-messages="error.insurance_expiry_date"
                    label="Insurance Expiry Date"
                    hide-details="auto"
                    prepend-inner-icon="mdi-calendar"
                    readonly
                    outlined
                    v-bind="attrs"
                    v-on="on"
                    :value="vehicleFormDetails.insurance_expiry_date"
                    @input="syncData($event, 'insurance_expiry_date')"
                  ></v-text-field>
                </template>
                <v-date-picker
                  no-title
                  reactive
                  :value="vehicleFormDetails.insurance_expiry_date"
                  scrollable
                  :min="nowDate"
                  @change="
                    syncData($event, 'insurance_expiry_date'),
                      $refs.insuranceExpiryDatePicker.save(insuranceExpiryDate)
                  "
                >
                </v-date-picker>
              </v-menu>
            </v-col>
            <v-col cols="6" lg="4">
              <v-text-field
                outlined
                name="insurance_type"
                :error-messages="error.insurance_type"
                hide-details="auto"
                label="Insurance Type"
                :value="vehicleFormDetails.insurance_type"
                @input="syncData($event, 'insurance_type')"
              ></v-text-field
            ></v-col>
            <v-col cols="6" lg="4">
              <v-text-field
                outlined
                :error-messages="error.rc_number"
                :rules="[(v) => !!v || 'RC number is required']"
                name="rc_number"
                hide-details="auto"
                label="RC number*"
                :value="vehicleFormDetails.rc_number"
                @input="syncData($event, 'rc_number')"
              ></v-text-field>
            </v-col>
            <v-col cols="6" lg="4">
              <v-menu
                ref="rcExpiryDatePicker"
                v-model="rcExpiryDatePicker"
                :close-on-content-click="false"
                :return-value.sync="rcExpiryDate"
                transition="scale-transition"
                min-width="auto"
                offset-y
              >
                <template v-slot:activator="{ on, attrs }">
                  <v-text-field
                    :rules="[(v) => !!v || 'RC expiry date is required']"
                    label="RC Expiry Date*"
                    name="rc_expiry_date"
                    :error-messages="error.rc_expiry_date"
                    hide-details="auto"
                    prepend-inner-icon="mdi-calendar"
                    readonly
                    outlined
                    v-bind="attrs"
                    v-on="on"
                    :value="vehicleFormDetails.rc_expiry_date"
                    @input="syncData($event, 'rc_expiry_date')"
                  ></v-text-field>
                </template>
                <v-date-picker
                  :value="vehicleFormDetails.rc_expiry_date"
                  :min="nowDate"
                  no-title
                  scrollable
                  @change="
                    syncData($event, 'rc_expiry_date'),
                      $refs.rcExpiryDatePicker.save(rcExpiryDate)
                  "
                >
                </v-date-picker>
              </v-menu>
            </v-col>
            <v-col cols="6" lg="4">
              <v-text-field
                :rules="[
                  (v) => !!v || 'Vehicle manufacturing company is required',
                ]"
                outlined
                :error-messages="error.vehicle_make"
                name="vehicle_make"
                hide-details="auto"
                label="Vehicle Make*"
                class="background-white"
                :value="vehicleFormDetails.vehicle_make"
                @input="syncData($event, 'vehicle_make')"
              ></v-text-field>
            </v-col>
            <v-col cols="6" lg="4">
              <v-text-field
                :rules="[(v) => !!v || 'Vehicle model is required']"
                outlined
                :error-messages="error.vehicle_model"
                name="vehicle_model"
                hide-details="auto"
                label="Vehicle Model*"
                class="background-white"
                :value="vehicleFormDetails.vehicle_model"
                @input="syncData($event, 'vehicle_model')"
              ></v-text-field>
            </v-col>
            <v-col cols="6" lg="4">
              <v-text-field
                :rules="[
                  (v) => !!v || 'Vehicle Manufacturing year is required',
                  (v) =>
                    v <= new Date().getFullYear() ||
                    'Vehicle can not be from future',
                ]"
                outlined
                :error-messages="error.vehicle_year"
                name="vehicle_year"
                hide-details="auto"
                type="number"
                min="1980"
                :max="new Date().getFullYear()"
                step="01"
                label="Vehicle Manufacturing Year*"
                class="background-white"
                :value="vehicleFormDetails.vehicle_year"
                @input="syncData($event, 'vehicle_year')"
              ></v-text-field>
            </v-col>
            <v-col cols="6" lg="4">
              <v-text-field
                :rules="[(v) => !!v || 'Vehicle price is required']"
                outlined
                type="number"
                min="0"
                step="01"
                :error-messages="error.vehicle_cost"
                name="vehicle_cost"
                hide-details="auto"
                label="Vehicle Cost*"
                class="background-white"
                :value="vehicleFormDetails.vehicle_cost"
                @input="syncData($event, 'vehicle_cost')"
              ></v-text-field>
            </v-col>
            <v-col cols="6" lg="4">
              <v-text-field
                :rules="[
                  (v) => !!v || 'Odometer reading of the vehicle is required',
                ]"
                outlined
                type="number"
                min="0"
                step="01"
                :error-messages="error.milage"
                name="mileage"
                hide-details="auto"
                label="Odometer reading*"
                class="background-white"
                :value="vehicleFormDetails.mileage"
                @input="syncData($event, 'mileage')"
              ></v-text-field>
            </v-col>
            <v-col cols="3">
              <v-select
                outlined
                name="status"
                :error-messages="error.status"
                :items="vehicleStatusList"
                hide-details="auto"
                label="Select Status*"
                class="background-white"
                :value="vehicleFormDetails.status"
                @change="syncData($event, 'status')"
                :menu-props="{ offsetY: true }"
              ></v-select>
            </v-col>
          </v-row>
          <!---------------------------------------------- Storage section ---------------------------------------------->
          <v-row no-gutters>
            <v-col cols="12" class="my-4">
              <span class="font-weight-bold text-subtitle-1"
                >Vehicle Storage Information</span
              >
              <hr />
            </v-col>
            <v-col cols="3" class="pa-1">
              <v-select
                outlined
                :rules="[(v) => !!v || 'Storage types are required']"
                name="available_storages"
                multiple
                :error-messages="error.available_storages"
                hide-details="auto"
                label="Storages*"
                :items="storageType"
                item-text="title"
                item-value="value"
                class="background-white"
                :value="vehicleFormDetails.storages"
                @change="syncData($event, 'storages')"
                :menu-props="{ offsetY: true }"
              >
                <template v-slot:selection="{ item, index }">
                  <span v-if="index === 0">{{ item.title }}</span>
                  <span v-if="index === 1" class="grey--text text-caption">
                    (+{{ vehicleFormDetails.storages.length - 1 }} others)
                  </span>
                </template>
              </v-select>
            </v-col>
            <v-col
              cols="3"
              class="pa-1"
              v-for="(n, i) in vehicleFormDetails.storages"
              :key="i"
            >
              <v-text-field
                outlined
                multiple
                :error-messages="error.sensor_info"
                hide-details="auto"
                persistent-hint
                :hint="`${n}'s Sensor-id`"
                :label="`${n}'s Sensor ID`"
                class="background-white"
                :value="vehicleFormDetails.sensors[n]"
                @input="syncData($event, 'sensors', n)"
              >
              </v-text-field>
            </v-col>
          </v-row>

          <v-row no-gutters>
            <v-col cols="12" class="mt-6 mb-8">
              <span class="font-weight-bold text-subtitle-1"> Tags </span>
              <hr />
            </v-col>
            <v-col cols="4">
              <CommonCustomselect
                :itemsList="vehicletagslist"
                item-text="title"
                item-value="title"
                label="Select Tag"
                :returnObject="false"
                :value="assigned_tags"
                :isMounted="addVehicleFormDialog"
                @selectionChanged="syncData($event, 'tags')"
                class="background-white"
              />
            </v-col>
          </v-row>

          <!------------------------------------------- Documnet upload section ------------------------------------------->
          <v-row no-gutters>
            <v-col cols="12" class="mt-4 mb-8">
              <span class="font-weight-bold text-subtitle-1"
                >Upload Documents</span
              >
              <hr />
            </v-col>
            <v-col cols="12">
              <v-row>
                <v-col cols="3">
                  <v-select
                    outlined
                    hide-details="auto"
                    label="Document Type"
                    :items="documentType"
                    v-model="uploadDocumentType"
                    item-text="title"
                    item-value="value"
                    return-object
                    class="background-white"
                    name="document_type"
                    :menu-props="{ offsetY: true }"
                  ></v-select>
                </v-col>
                <v-col cols="6">
                  <v-file-input
                    ref="fileInput"
                    :clearable="true"
                    hide-details
                    type="file"
                    :disabled="uploadDocumentType ? false : true"
                    v-model="uploadFiles"
                    label="Upload Document"
                    prepend-inner-icon="mdi-attachment mdi-rotate-90"
                    prepend-icon=""
                    accept="image/*, .pdf"
                    outlined
                    @change="getFileData($event)"
                  ></v-file-input>
                </v-col>
              </v-row>
            </v-col>
            <v-col cols="12 pt-8 pb-14">
              <div>
                <div
                  class="mt-0 mb-4 pl-4"
                  v-show="
                    vehicleFormDetails.vehicle_documents &&
                    vehicleFormDetails.vehicle_documents.length
                  "
                >
                  <span class="font-weight-bold text-subtitle-1">
                    Uploaded
                  </span>
                </div>

                <v-card
                  elevation="0"
                  outlined
                  v-for="(data, i) in vehicleFormDetails.vehicle_documents"
                  :key="i"
                >
                  <v-card-text>
                    <v-row>
                      <v-col cols="11">
                        <a :href="data.document" target="_black">
                          <h4>{{ data.document_type }}</h4>
                        </a>
                      </v-col>
                      <v-col cols="1">
                        <v-icon
                          small
                          color="red"
                          @click="deleteDocument(data.id, i)"
                          >mdi-close</v-icon
                        >
                      </v-col>
                    </v-row>
                  </v-card-text>
                </v-card>
              </div>

              <div
                class="mt-5 mb-4 pl-4"
                v-show="documentList && documentList.length"
              >
                <span class="font-weight-bold text-subtitle-1">
                  New Upload
                </span>
              </div>

              <v-card
                elevation="0"
                outlined
                v-for="(data, j) in documentList"
                :key="j"
              >
                <v-card-text>
                  <v-row>
                    <v-col cols="7">
                      <a :href="generateUrl(data.file)" target="_black">
                        <h4>{{ data.document_name }}</h4>
                      </a>
                    </v-col>
                    <v-col cols="2">
                      <h4>{{ getSize(data.file.size) }}</h4>
                    </v-col>
                    <v-col cols="2"> </v-col>
                    <v-col cols="1">
                      <v-icon small color="primary" @click="removeFile(j)"
                        >mdi-close</v-icon
                      >
                    </v-col>
                  </v-row>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </v-form>
      </v-card-text>
      <v-card-actions class="pb-3 d-flex justify-center">
        <v-btn
          :disabled="!isValid"
          @click.prevent="submitVehicleForm()"
          class="primary text-uppercase mr-3"
        >
          <span>Submit</span>
        </v-btn>
        <v-btn
          type="reset"
          v-if="formType == 'add'"
          class="primary text-uppercase"
          @click="resetForm()"
        >
          <span>Reset</span>
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
// import { genrateFormData } from "~/assets/js/formMethods";

export default {
  props: {
    value: Boolean,
    formType: {
      type: String,
      default: "add",
    },
  },
  data() {
    return {
      menu: false,
      activePicker: null,
      error: [],
      nonFieldError: [],
      isValid: false,
      documentList: [],
      fileNameList: [],
      uploadFiles: null,
      uploadDocumentType: null,
      documentType: [
        {
          title: "Vehicle Photo",
          value: "vehicle_photo",
        },
        {
          title: "vehicle Rc Photo",
          value: "vehicle_rc_photo",
        },
        {
          title: "Food Delivery Permits",
          value: "food_delivery_permits",
        },
        {
          title: "Calibration Certificate",
          value: "calibration_certificate",
        },
        {
          title: "Insurance Certificate",
          value: "insurance_certificate",
        },
        {
          title: "Other Documents",
          value: "other",
        },
      ],
      storageType: [
        {
          title: "Dry",
          value: "Dry",
        },
        {
          title: "Chilled",
          value: "Chilled",
        },
        {
          title: "Frozen",
          value: "Frozen",
        },
      ],
      fuelType: [
        {
          title: "Petrol",
          value: "petrol",
        },
        {
          title: "Diesel",
          value: "diesel",
        },
        {
          title: "Other",
          value: "other",
        },
      ],
      nowDate: new Date().toISOString().slice(0, 10),
      rcExpiryDate: null,
      rcExpiryDatePicker: false,
      insuranceExpiryDatePicker: false,
      insuranceExpiryDate: null,
    };
  },
  computed: {
    vehicleStatusList() {
      return [
        { text: "Activate", value: "idle" },
        { text: "Deactivate", value: "deactivated" },
      ];
    },
    vehicleFormDetails: {
      get() {
        return this.$store.state.vehicle.selectedVehicle;
      },
      set(value) {
        this.$store.commit("vehicle/SET_VEHICLE_FORM_DETAILS", value);
      },
    },
    vehicletagslist: {
      get() {
        return this.$store.state.customer.customerAddress.vehicletaglist;
      },
      set(value) {
        this.$store.commit("customer/customerAddress/SET_VEHICLE_TAGS", value);
      },
    },
    assigned_tags() {
      if (this.$store.state.vehicle.selectedVehicle.assigned_tags) {
        return this.$store.state.vehicle.selectedVehicle.assigned_tags.map(
          (item) => item.tag
        );
      } else {
        return [];
      }
    },
    addVehicleFormDialog: {
      get() {
        return this.value;
      },
      set(value) {
        this.$emit("input", value);
      },
    },
    allProjects() {
      return this.$store.getters["project/PROJECT_LIST_FOR_DROPDOWN"];
    },
  },
  methods: {
    getVehicleTagList() {
      this.$store.dispatch("customer/customerAddress/GET_TAG_LIST");
    },
    generateUrl(file) {
      return URL.createObjectURL(file);
    },
    removeFile(index) {
      this.documentList.splice(index, 1);
    },
    imageFileCheck(fileName) {
      let extension = fileName.slice(
        (Math.max(0, fileName.lastIndexOf(".")) || Infinity) + 1
      );
      if (extension == "png" || extension == "jpeg" || extension == "jpg") {
        return true;
      } else {
        this.$notifier.showMessage({
          content: `Select file(s) are not supported.Support file Types: PNG, JPEG, JPG `,
          color: "error",
        });
        return false;
      }
    },
    getFileData(fileInput) {
      if (fileInput && fileInput.name && !this.imageFileCheck(fileInput.name)) {
        this.$refs.fileInput.reset();
        this.uploadDocumentType = null;
        return false;
      }

      if (fileInput) {
        this.documentList.push({
          file: fileInput,
          document_type: this.uploadDocumentType.value,
          document_name: this.uploadDocumentType.title,
        });
        this.fileNameList.push(fileInput.name);
        this.$refs.fileInput.reset();
        this.uploadDocumentType = null;
        this.scrollTobottom();
      }
    },
    scrollTobottom() {
      setTimeout(() => {
        this.$refs.vehicleSectionForm.scrollTo({
          top: this.$refs.vehicleSectionForm.scrollHeight,
          behavior: "smooth",
        });
      }, 300);
    },
    getSize(bytes) {
      var sizes = ["Bytes", "KB", "MB", "GB", "TB"];
      if (bytes == 0) return "0 Byte";
      var i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)));
      return Math.round(bytes / Math.pow(1024, i), 2) + " " + sizes[i];
    },
    uploadDocument(id = null) {
      this.documentList.forEach((details, index) => {
        let payload = {
          id: null,
          data: null,
        };
        payload.id = id;
        let newForm = new FormData();
        newForm.append("document_type", details.document_type);
        newForm.append("document", details.file);
        payload.data = newForm;
        this.$store
          .dispatch("vehicle/UPLOAD_DOCUMENT", payload)
          .then((response) => {})
          .catch((err) => {
            console.log(err);
          });
      });
    },
    deleteDocument(id, index) {
      this.$store
        .dispatch("vehicle/DELETE_DOCUMENT", id)
        .then((response) => {
          this.$store.commit("vehicle/REMOVE_VEHICLE_DOCUMENT", index);
        })
        .catch((err) => {
          console.log(err);
        });
    },
    closeDialog() {
      this.addVehicleFormDialog = false;
      this.resetForm();
    },
    syncData(input_value, key, subKey) {
      if (this.error[key]) {
        this.error[key] = null;
        delete this.error[key];
      }
      if (this.error["sensor_info"] && key == "sensors") {
        this.error["sensor_info"] = null;
        delete this.error["sensor_info"];
      }
      if (this.error["available_storages"] && key == "storages") {
        this.error["available_storages"] = null;
        delete this.error["available_storages"];
      }
      this.$store.commit("vehicle/SYNC_VEHICLE_FORM_DETAILS", {
        key: key,
        value: input_value,
        subKey: subKey,
      });
      this.$forceUpdate();
    },
    get_all_vehicles() {
      this.$store
        .dispatch("vehicle/GET_ALL_VEHICLES")
        .then((result) => {})
        .catch((err) => {
          this, $notifier.showMessage({ content: err, color: "error" });
        });
    },
    submitVehicleForm() {
      const form = document.getElementById("vehicleForm");
      let postData = new FormData(form);
      if(this.vehicleFormDetails.storages) {
          postData.set(
            "sensor_info",
          this.vehicleFormDetails.storages
            .map((key) => {
              return this.vehicleFormDetails.sensors[key];
            })
            .join()
        );
      }

      if (this.vehicleFormDetails.tags) {
        postData.set('tags', this.vehicleFormDetails.tags.join())
      }
      if (this.formType == "add") {
        this.$store
          .dispatch("vehicle/ADD_VEHICLE", postData)
          .then((result) => {
            this.$notifier.showMessage({
              content: "Vehicle added Successfuly!",
              color: "success",
            });
            this.uploadDocument(result.id);
            this.resetForm();
            this.addVehicleFormDialog = false;
          })
          .catch((err) => {
            if ("non_field_errors" in err) {
              this.nonFieldError = err.non_field_errors;
            }
            this.error = err;
          });
      } else {
        this.$store
          .dispatch("vehicle/UPDATE_VEHICLE_DETAILS", {
            data: postData,
            id: this.vehicleFormDetails.id,
          })
          .then((result) => {
            this.$notifier.showMessage({
              content: "Vehicle Updated Successfuly!",
              color: "success",
            });
            this.uploadDocument(this.vehicleFormDetails.id);
            this.resetForm();
            this.addVehicleFormDialog = false;
          })
          .catch((err) => {
            if ("non_field_errors" in err) {
              this.nonFieldError = err.non_field_errors;
            }
            this.error = err;
          });
      }
    },
    resetForm() {
      this.vehicleFormDetails = {
        cbm_capacity: null,
        fuel_type: null,
        insurance_expiry_date: null,
        insurance_policy_number: null,
        insurance_type: null,
        permits: null,
        box_capacity: null,
        project: null,
        rc_expiry_date: null,
        rc_number: null,
        status: null,
        tonnage_capacity: null,
        vehicle_plate_no: null,
        sensors: {},
      };
      this.documentList = [];
      this.fileNameList = [];
      this.error = [];
      this.nonFieldError = [];
      this.uploadFiles = null;
      this.uploadDocumentType = null;

      this.$refs.vehicleForm.reset();
    },
  },
  mounted() {
    this.getVehicleTagList();
  },
};
</script>