<template>
  <v-dialog
    v-model="openDriverFormDialog"
    persistent
    scrollable
    width="80%"
    @keydown.esc="closeDialog()"
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
        <span>{{ formType }} Driver</span>
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
      <v-card-text
        v-if="openDriverFormDialog"
        class="pa-5 pt-2"
        ref="DriverForm"
      >
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
        <v-form ref="DriverFormAdd" id="DriverFormAdd" v-model="isValid">
          <v-row>
            <v-col cols="12" lg="8">
              <v-row>
                <v-col cols="6" lg="4">
                  <v-text-field
                    outlined
                    hide-details="auto"
                    label="First Name*"
                    class="background-white"
                    name="first_name"
                    :rules="[
                      (v) =>
                        (!!v && v.trim().length > 0) ||
                        'First name is required',
                    ]"
                    :error-messages="error.first_name"
                    :value="driverFormDetails.first_name"
                    @input="syncData($event, 'first_name')"
                  ></v-text-field>
                </v-col>
                <v-col cols="6" lg="4">
                  <v-text-field
                    outlined
                    hide-details="auto"
                    label="Last Name*"
                    class="background-white"
                    name="last_name"
                    :rules="[
                      (v) =>
                        (!!v && v.trim().length > 0) || 'Last name is required',
                    ]"
                    :error-messages="error.last_name"
                    :value="driverFormDetails.last_name"
                    @input="syncData($event, 'last_name')"
                  ></v-text-field>
                </v-col>
                <v-col cols="6" lg="4">
                  <v-text-field
                    outlined
                    hide-details="auto"
                    label="Username*"
                    name="username"
                    class="background-white"
                    :rules="[
                      (v) =>
                        (!!v && v.trim().length > 0) || 'Username is required',
                    ]"
                    :error-messages="error.username"
                    :value="driverFormDetails.username"
                    @input="syncData($event, 'username')"
                  ></v-text-field>
                </v-col>
                <v-col cols="6" lg="4">
                  <v-text-field
                    outlined
                    hide-details="auto"
                    type="password"
                    name="password"
                    label="Password*"
                    class="background-white"
                    :rules="
                      formType == 'add'
                        ? [
                            (v) =>
                              (!!v && v.trim().length > 0) ||
                              'Password is required',
                          ]
                        : []
                    "
                    :error-messages="error.password"
                    :value="driverFormDetails.password"
                    @input="syncData($event, 'password')"
                  ></v-text-field>
                </v-col>
                <v-col cols="6" lg="4">
                  <v-text-field
                    outlined
                    hide-details="auto"
                    type="password"
                    label="Confirm Password*"
                    class="background-white"
                    :rules="
                      formType == 'add'
                        ? [
                            (v) =>
                              (!!v && v.trim().length > 0) ||
                              'Confirm password is required',
                          ].concat([
                            (v) =>
                              this.driverFormDetails.password ===
                                this.driverFormDetails.confirm_password ||
                              'Passwords do not match',
                          ])
                        : [
                            (v) =>
                              this.driverFormDetails.password ===
                                this.driverFormDetails.confirm_password ||
                              'Passwords do not match',
                          ]
                    "
                    :error-messages="error.confirm_password"
                    :value="driverFormDetails.confirm_password"
                    @input="syncData($event, 'confirm_password')"
                  ></v-text-field>
                </v-col>
                <v-col cols="6" lg="4">
                  <v-text-field
                    outlined
                    hide-details="auto"
                    label="Contact Number*"
                    type="number"
                    min="0"
                    name="contact_number"
                    class="background-white"
                    :rules="[(v) => !!v || 'Contact Number is required']"
                    :error-messages="error.contact_number"
                    :value="driverFormDetails.contact_number"
                    @input="syncData($event, 'contact_number')"
                  ></v-text-field>
                </v-col>
                <v-col cols="6" lg="4">
                  <v-select
                    outlined
                    hide-details="auto"
                    label="Project*"
                    :items="allProjects"
                    name="project"
                    class="background-white"
                    :rules="[(v) => !!v || 'Project is required']"
                    :error-messages="error.project"
                    :value="driverFormDetails.project"
                    @input="syncData($event, 'project')"
                    @change="updateVehicleZoneList($event)"
                    :menu-props="{ offsetY: true }"
                  ></v-select>
                </v-col>
                <v-col cols="6" lg="4">
                  <v-select
                    outlined
                    hide-details="auto"
                    label="Zone"
                    ref="zoneField"
                    :items="allZones"
                    item-text="zone_name"
                    item-value="zone_name"
                    class="background-white"
                    name="zone"
                    :no-data-text="
                      !driverFormDetails.project
                        ? 'Select Project First !'
                        : 'No data available.'
                    "
                    :error-messages="error.zone"
                    :value="driverFormDetails.zone"
                    @input="syncData($event, 'zone')"
                    :menu-props="{ offsetY: true }"
                  ></v-select>
                </v-col>
                <v-col cols="6" lg="4">
                  <v-select
                    outlined
                    ref="vehicleAssigned"
                    hide-details="auto"
                    label="Vehicle Assigned"
                    :items="allVehicles"
                    name="vehicle_assigned"
                    item-text="vehicle_plate_no"
                    item-value="vehicle_plate_no"
                    class="background-white"
                    :no-data-text="
                      !driverFormDetails.project
                        ? 'Select Project First !'
                        : 'No data available.'
                    "
                    :error-messages="error.vehicle_assigned"
                    :value="driverFormDetails.vehicle_assigned"
                    @input="syncData($event, 'vehicle_assigned')"
                    :menu-props="{ offsetY: true }"
                  ></v-select>
                </v-col>
                <v-col cols="6" lg="4">
                  <v-text-field
                    outlined
                    hide-details="auto"
                    type="time"
                    label="Shift Timmings (Start)*"
                    :rules="[(v) => !!v || 'Shift start time is required']"
                    class="background-white"
                    name="shift_start"
                    :error-messages="error.shift_start"
                    :value="driverFormDetails.shift_start"
                    @input="syncData($event, 'shift_start')"
                  ></v-text-field>
                </v-col>
                <v-col cols="6" lg="4">
                  <v-text-field
                    outlined
                    hide-details="auto"
                    type="time"
                    label="Shift Timmings (End)*"
                    class="background-white"
                    :rules="[
                      (v) => !!v || 'Value required',
                      (v) =>
                        (v &&
                          v.slice(0, 5) !==
                            driverFormDetails.shift_start.slice(0, 5)) ||
                        'Start and End Shift time cant be same',
                    ]"
                    name="shift_end"
                    :error-messages="error.shift_end"
                    :value="driverFormDetails.shift_end"
                    @input="syncData($event, 'shift_end')"
                  ></v-text-field>
                </v-col>

                <v-col cols="6" lg="4">
                  <v-select
                    outlined
                    hide-details="auto"
                    label="User Status"
                    name="is_active"
                    :items="statusType"
                    class="background-white"
                    :error-messages="error.is_active"
                    :value="driverFormDetails.is_active"
                    @input="syncData($event, 'is_active')"
                    :menu-props="{ offsetY: true }"
                  ></v-select>
                </v-col>
              </v-row>
            </v-col>
            <v-col cols="12" lg="4" class="d-flex flex-column align-center">
              <v-img
                v-if="!driverFormDetails.profile_image"
                :src="driverImage"
                height="200px"
                width="200px"
                contain
              />
              <div v-else class="pos-rel mt-12">
                <v-btn
                  fab
                  x-small
                  class="floating-btn-tr"
                  @click="removeImage('profile')"
                >
                  <v-icon small>mdi-close</v-icon>
                </v-btn>
                <v-img
                  :src="driverFormDetails.profile_image"
                  height="200px"
                  width="200px"
                  contain
                />
              </div>
              <v-btn
                v-if="!driverFormDetails.profile_image"
                small
                depressed
                class="primary"
                :loading="isProfilePhotoSelecting"
                @click="onButtonClick('profile')"
              >
                <v-icon small>mdi-attachment</v-icon>
                <span class="pl-2">Driver Photo</span>
              </v-btn>
              <input
                name="profile_image"
                ref="profilePhotoUploader"
                class="d-none"
                type="file"
                accept="image/png, image/jpg, image/jpeg"
                @change="onFileChanged($event, 'profile')"
              />
            </v-col>
            <v-col cols="12" lg="8">
              <v-row>
                <v-col cols="6" lg="3">
                  <v-text-field
                    outlined
                    hide-details="auto"
                    label="Licence Number*"
                    class="background-white"
                    name="license_number"
                    :rules="[
                      (v) =>
                        (!!v && v.trim().length > 0) ||
                        'Licence number is required',
                    ]"
                    :error-messages="error.license_number"
                    :value="driverFormDetails.license_number"
                    @input="syncData($event, 'license_number')"
                  ></v-text-field>
                </v-col>
                <v-col cols="6" lg="3">
                  <v-menu
                    ref="licenseExpiry"
                    v-model="DatePickerMenu1"
                    :close-on-content-click="false"
                    :return-value.sync="date"
                    transition="scale-transition"
                    max-width="290px"
                    min-width="auto"
                    offset-y
                  >
                    <template v-slot:activator="{ on, attrs }">
                      <v-text-field
                        outlined
                        hide-details="auto"
                        label="Licence Expiry*"
                        class="background-white"
                        aria-autocomplete="false"
                        prepend-inner-icon="mdi-calendar"
                        v-bind="attrs"
                        v-on="on"
                        name="license_expiry"
                        readonly
                        :rules="[(v) => !!v || 'Licence expiry is required']"
                        :error-messages="error.license_expiry"
                        :value="driverFormDetails.license_expiry"
                        @input="syncData($event, 'license_expiry')"
                      ></v-text-field>
                    </template>
                    <v-date-picker
                      no-title
                      scrollable
                      reactive
                      :min="nowDate"
                      :value="driverFormDetails.license_expiry"
                      @change="
                        syncData($event, 'license_expiry'),
                          $refs.licenseExpiry.save(date)
                      "
                    >
                    </v-date-picker>
                  </v-menu>
                </v-col>
                <v-col cols="6" lg="3">
                  <v-text-field
                    outlined
                    hide-details="auto"
                    label="Nationality"
                    name="nationality"
                    class="background-white"
                    :error-messages="error.nationality"
                    :value="driverFormDetails.nationality"
                    @input="syncData($event, 'nationality')"
                  ></v-text-field>
                </v-col>
                <v-col cols="6" lg="3">
                  <v-menu
                    ref="nationalIdExpiry"
                    v-model="DatePickerMenu2"
                    :close-on-content-click="false"
                    :return-value.sync="date"
                    transition="scale-transition"
                    max-width="290px"
                    min-width="auto"
                    offset-y
                  >
                    <template v-slot:activator="{ on, attrs }">
                      <v-text-field
                        outlined
                        hide-details="auto"
                        label="National Id Expiry Date*"
                        prepend-inner-icon="mdi-calendar"
                        class="background-white"
                        aria-autocomplete="false"
                        name="national_id_expiry"
                        v-bind="attrs"
                        v-on="on"
                        :rules="[
                          (v) => !!v || 'National ID Expiry is required',
                        ]"
                        readonly
                        :error-messages="error.national_id_expiry"
                        :value="driverFormDetails.national_id_expiry"
                        @input="syncData($event, 'national_id_expiry')"
                      ></v-text-field>
                    </template>
                    <v-date-picker
                      no-title
                      scrollable
                      reactive
                      :min="nowDate"
                      :value="driverFormDetails.national_id_expiry"
                      @change="
                        syncData($event, 'national_id_expiry'),
                          $refs.nationalIdExpiry.save(date)
                      "
                    >
                    </v-date-picker>
                  </v-menu>
                </v-col>
              </v-row>
            </v-col>
            <v-col cols="12" lg="8">
              <v-row>
                <v-col cols="6" lg="3">
                  <v-text-field
                    outlined
                    hide-details="auto"
                    label="Health Card Number"
                    name="health_card_number"
                    class="background-white"
                    :error-messages="error.health_card_number"
                    :value="driverFormDetails.health_card_number"
                    @input="syncData($event, 'health_card_number')"
                  ></v-text-field>
                </v-col>
                <v-col cols="6" lg="3">
                  <v-menu
                    ref="healthCardExpiry"
                    v-model="DatePickerMenu3"
                    :close-on-content-click="false"
                    :return-value.sync="date"
                    transition="scale-transition"
                    max-width="290px"
                    min-width="auto"
                    offset-y
                  >
                    <template v-slot:activator="{ on, attrs }">
                      <v-text-field
                        outlined
                        hide-details="auto"
                        label="Health Card Expiry Date"
                        prepend-inner-icon="mdi-calendar"
                        class="background-white"
                        name="health_card_expiry"
                        aria-autocomplete="false"
                        v-bind="attrs"
                        v-on="on"
                        readonly
                        :error-messages="error.health_card_expiry"
                        :value="driverFormDetails.health_card_expiry"
                        @input="syncData($event, 'health_card_expiry')"
                      ></v-text-field>
                    </template>
                    <v-date-picker
                      no-title
                      scrollable
                      reactive
                      :min="nowDate"
                      :value="driverFormDetails.health_card_expiry"
                      @change="
                        syncData($event, 'health_card_expiry'),
                          $refs.healthCardExpiry.save(date)
                      "
                    >
                    </v-date-picker>
                  </v-menu>
                </v-col>
                <v-col cols="6" lg="3">
                  <v-text-field
                    outlined
                    hide-details="auto"
                    label="Visa number"
                    class="background-white"
                    name="visa_number"
                    :error-messages="error.visa_number"
                    :value="driverFormDetails.visa_number"
                    @input="syncData($event, 'visa_number')"
                  ></v-text-field>
                </v-col>
                <v-col cols="6" lg="3">
                  <v-menu
                    ref="visaExpiry"
                    v-model="DatePickerMenu4"
                    :close-on-content-click="false"
                    :return-value.sync="date"
                    transition="scale-transition"
                    max-width="290px"
                    min-width="auto"
                    offset-y
                  >
                    <template v-slot:activator="{ on, attrs }">
                      <v-text-field
                        outlined
                        hide-details="auto"
                        label="Visa Expiry Date"
                        class="background-white"
                        name="visa_expiry"
                        aria-autocomplete="false"
                        prepend-inner-icon="mdi-calendar"
                        v-bind="attrs"
                        v-on="on"
                        readonly
                        :error-messages="error.visa_expiry"
                        :value="driverFormDetails.visa_expiry"
                        @input="syncData($event, 'visa_expiry')"
                      ></v-text-field>
                    </template>
                    <v-date-picker
                      no-title
                      scrollable
                      reactive
                      :min="nowDate"
                      :value="driverFormDetails.visa_expiry"
                      @change="
                        syncData($event, 'visa_expiry'),
                          $refs.visaExpiry.save(date)
                      "
                    >
                    </v-date-picker>
                  </v-menu>
                </v-col>
              </v-row>
            </v-col>
            <v-col cols="12" lg="4">
              <v-row>
                <v-col cols="6">
                  <v-text-field
                    outlined
                    hide-details="auto"
                    type="number"
                    min="0"
                    step="01"
                    name="salary"
                    label="Salary"
                    class="background-white"
                    :error-messages="error.salary"
                    :value="driverFormDetails.salary"
                    @input="syncData($event, 'salary')"
                  ></v-text-field>
                </v-col>

                <v-col cols="6">
                  <v-select
                    outlined
                    hide-details="auto"
                    label="Service Type"
                    :items="serviceType"
                    class="background-white"
                    name="service_type"
                    :error-messages="error.service_type"
                    :value="driverFormDetails.service_type"
                    @input="syncData($event, 'service_type')"
                    :menu-props="{ offsetY: true }"
                  ></v-select>
                </v-col>
              </v-row>
            </v-col>
          </v-row>

          <!-- NOte : this functionality used in future -->
          <!-- <v-row no-gutters>
            <v-col cols="12" class="mt-6 mb-8">
              <span class="font-weight-bold text-subtitle-1"> Tag </span>
              <hr />
            </v-col>
            <v-col cols="4">
              <v-select
                outlined
                hide-details="auto"
                label="Tags"
                multiple="multiple"
                :items="drivertagslist"
                item-text="title"
                item-value="value"
                class="background-white"
                name="tags"
                :value="assigned_tags"
                @input="syncData($event, 'tags')"
                :menu-props="{ offsetY: true }"
              ></v-select>
            </v-col>
          </v-row> -->

          <v-row no-gutters>
            <v-col cols="12" class="mt-6 mb-8">
              <span class="font-weight-bold text-subtitle-1">
                Upload Documents
              </span>
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
                    driverFormDetails.driver_documents &&
                    driverFormDetails.driver_documents.length
                  "
                >
                  <span class="font-weight-bold text-subtitle-1">
                    Uploaded
                  </span>
                </div>

                <v-card
                  elevation="0"
                  outlined
                  v-for="(data, i) in driverFormDetails.driver_documents"
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
          @click.prevent="submitDriverForm()"
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
import defaultDriverImage from "@/static/user.png";
import authHeader from "~/store/authHeader";

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
      // Form handling varibles
      nonFieldError: [],
      documentList: [],
      uploadFiles: null,
      uploadDocumentType: null,
      error: {
        user: {},
      },
      documentType: [
        {
          title: "Licence",
          value: "license_photo",
        },
        {
          title: "Food safety certificate ",
          value: "food_safety_permits",
        },
        {
          title: "Emirates Id ",
          value: "emirates_id",
        },
        {
          title: "Vaccination ID",
          value: "vaccination_card",
        },
        {
          title: "Health ID ",
          value: "health_card",
        },
        {
          title: "Visa ID",
          value: "visa",
        },
        {
          title: "National Id Card ",
          value: "national_id_card",
        },
        {
          title: "Other Documents",
          value: "other",
        },
      ],
      driverImage: defaultDriverImage,
      isValid: false,
      // loader variable
      isProfilePhotoSelecting: false,

      // image removal flag varibles for edit
      hasProfileImage: false,
      // date picker variables
      nowDate: new Date().toISOString().slice(0, 10),
      date: null,
      DatePickerMenu1: false,
      DatePickerMenu2: false,
      DatePickerMenu3: false,
      DatePickerMenu4: false,
      serviceType: ["B2B", "B2C"],
      statusType: [
        {
          text: "Active",
          value: true,
        },
        {
          text: "Deactivate",
          value: false,
        },
      ],
    };
  },
  computed: {
    drivertagslist: {
      get() {
        return this.$store.state.customer.customerAddress.drivertaglist;
      },
      set(value) {
        this.$store.commit("customer/customerAddress/SET_DRIVER_TAGS", value);
      },
    },
    assigned_tags() {
      if (this.$store.state.driver.driverForm.assigned_tags) {
        return this.$store.state.driver.driverForm.assigned_tags.map(
          (item) => item.id
        );
      } else {
        return [];
      }
    },
    openDriverFormDialog: {
      get() {
        return this.value;
      },
      set(value) {
        this.$emit("input", value);
      },
    },
    driverFormDetails: {
      get() {
        return this.$store.state.driver.driverForm;
      },
      set(value) {
        this.$store.commit("driver/SET_DRIVER_FORM_DETAILS", value);
      },
    },
    allProjects() {
      return this.$store.getters["project/PROJECT_LIST_FOR_DROPDOWN"];
    },
    // Filtered Vehicle list according to the project selected
    allVehicles: {
      get() {
        return this.$store.state.driver.allVehicles;
      },
      set() {},
    },
    // Filtered Zone list according to the project selected
    allZones: {
      get() {
        return this.$store.state.driver.allZones;
      },
      set() {},
    },
  },
  methods: {
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
        this.$refs.fileInput.reset();
        this.uploadDocumentType = null;

        this.scrollTobottom();
      }
    },
    scrollTobottom() {
      setTimeout(() => {
        this.$refs.DriverForm.scrollTo({
          top: this.$refs.DriverForm.scrollHeight,
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
          .dispatch("driver/UPLOAD_DOCUMENT", payload)
          .then((response) => {})
          .catch((err) => {
            console.log(err);
          });
      });
    },
    deleteDocument(id, index) {
      this.$store
        .dispatch("driver/DELETE_DOCUMENT", id)
        .then((response) => {
          this.$store.commit("driver/REMOVE_DRIVER_DOCUMENT", index);
        })
        .catch((err) => {
          console.log(err);
        });
    },
    updateVehicleZoneList(project) {
      if (project) {
        this.$store
          .dispatch(
            "driver/GET_VEHICLE_LIST_FOR_FORM",
            project
          )
          .then((result) => {
            this.$forceUpdate();
          })
          .catch((err) => {
            this.$notifier.showMessage({
              content: err.message,
              color: "error",
            });
          });
        this.$store
          .dispatch(
            "driver/GET_ZONE_LIST_FOR_FORM",
            project
          )
          .then((result) => {
            this.$forceUpdate();
          })
          .catch((err) => {
            this.$notifier.showMessage({
              content: err.message,
              color: "error",
            });
          });
      }
    },
    closeDialog() {
      this.resetForm();
      this.openDriverFormDialog = false;
    },
    syncData(e, key, subKey) {
      if (this.error[key]) {
        this.error[key] = null;
        delete this.error[key];
      }
      if (key == "project" && this.formType == "edit") {
        this.$store.commit("driver/SYNC_DRIVER_FORM_DETAILS", {
          key: "zone",
          subKey: null,
          value: "",
        });
        this.$store.commit("driver/SYNC_DRIVER_FORM_DETAILS", {
          key: "vehicle_assigned",
          subKey: null,
          value: "",
        });
        this.$refs.zoneField.value = "";
        this.$refs.vehicleAssigned.value = "";
      } else {
        this.$store.commit("driver/SYNC_DRIVER_FORM_DETAILS", {
          key: key,
          subKey: subKey,
          value: e,
        });
      }
    },
    onButtonClick(buttonType) {
      if (buttonType == "profile") {
        this.isProfilePhotoSelecting = true;
        window.addEventListener(
          "focus",
          () => {
            this.isProfilePhotoSelecting = false;
          },
          { once: true }
        );
        this.$refs.profilePhotoUploader.click();
      }
    },
    onFileChanged(e, input_type) {
      const selectedFile = e.target.files[0];
      if (
        selectedFile.type.toLowerCase().indexOf("png") == -1 &&
        selectedFile.type.toLowerCase().indexOf("jpg") == -1 &&
        selectedFile.type.toLowerCase().indexOf("jpeg") == -1
      ) {
        alert("File type not supported \nSupported Types: PNG, JPG, JPEG");
        return null;
      }
      if (input_type == "profile" && selectedFile) {
        const url = URL.createObjectURL(selectedFile);
        this.syncData(url, "profile_image");
        this.hasProfileImage = true;
      }
      this.$forceUpdate();
    },
    removeImage(buttonType) {
      if (buttonType == "profile") {
        if (this.formType != "add") {
          this.hasProfileImage = true;
        }
        this.syncData(null, "profile_image");
        this.hasProfileImage = false;
        this.$refs.profilePhotoUploader.type = "text";
        this.$refs.profilePhotoUploader.type = "file";
      }
      this.$forceUpdate();
    },
    submitDriverForm() {
      const form = document.getElementById("DriverFormAdd");
      let postData = new FormData(form);
      postData = this.checkFields(postData);

      let payload = {
        isBulkupload: true,
        data: postData,
      };
      if (this.formType == "add") {
        this.$store
          .dispatch("driver/ADD_DRIVER", payload)
          .then((result) => {
            this.$notifier.showMessage({
              content: "Driver added Successfuly!",
              color: "success",
            });
            this.uploadDocument(result.id);
            this.resetForm();
            this.openDriverFormDialog = false;
          })
          .catch((err) => {
            if ("non_field_errors" in err) {
              this.nonFieldError = err.non_field_errors;
            }
            this.error = err.errors;
          });
      } else {
        this.$store
          .dispatch("driver/UPDATE_DRIVER_DETAILS", {
            data: postData,
            id: this.driverFormDetails.id,
          })
          .then((result) => {
            this.$notifier.showMessage({
              content: "Driver Updated Successfuly!",
              color: "success",
            });

            this.uploadDocument(this.driverFormDetails.id);
            this.resetForm();
            this.openDriverFormDialog = false;
          })
          .catch((err) => {
            this.error = err.errors;
          });
      }
    },
    checkFields(formData) {
      if (formData.has("password") && formData.get("password").trim() == "") {
        formData.delete("password");
      }
      if (!this.hasProfileImage) {
        formData.delete("profile_image");
      }
      return formData;
    },
    getDriverTagList() {
      this.$store.dispatch("customer/customerAddress/GET_TAG_LIST");
    },
    resetForm() {
      this.driverFormDetails = {
        first_name: null,
        last_name: null,
        username: null,
        profile_image: null,
        contact_number: null,
        project: null,
        license_number: null,
        license_expiry: null,
        nationality: null,
        national_id: null,
        national_id_expiry: null,
        shift_start: null,
        shift_end: null,
        is_active: null,
        tags: null,
      };
      this.documentList = [];
      this.uploadFiles = null;
      this.uploadDocumentType = null;

      this.$refs.DriverFormAdd.reset();
    },
  },
  mounted() {
    this.getDriverTagList();
  },
  beforeDestroy() {
    this.allZones = [];
    this.allVehicles = [];
  },
};
</script>