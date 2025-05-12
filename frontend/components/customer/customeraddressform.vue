<template>
  <v-dialog
    v-model="addCustomerAddressFormDialog"
    persistent
    scrollable
    width="55%"
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
        <span v-if="isEditMode"> Edit </span>
        <span v-else> Add </span>
        &nbsp;Customer Address
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
      <v-card-text class="pa-5 pt-2" id="customerAddressForm">
        <v-alert v-if="nonFieldError.length" dense type="error">
          <v-list
            class="pa-0"
            dense
            style="background: inherit !important"
            v-for="(error, i) in nonFieldError"
            :key="i"
          >
            <v-list-item dense style="min-height: 20px !important">
              <span>{{ i + 1 }} .</span><span>{{ error }}</span>
            </v-list-item>
          </v-list>
        </v-alert>
        <v-form v-model="isFormVaid" class="pb-16" ref="customerAddressForm">
          <v-row>
            <v-col cols="6" md="4" xl="4">
              <v-text-field
                outlined
                hide-details="auto"
                class="background-white"
                label="Customer Code*"
                :rules="[
                  (v) =>
                    (!!v && v.trim().length > 0) || 'Customer Code is required',
                ]"
                :error-messages="error.customer_code"
                :value="addressDetails.customer_code"
                @input="syncData($event, 'customer_code')"
              ></v-text-field>
            </v-col>
            <v-col cols="6" md="4" xl="4">
              <v-text-field
                outlined
                hide-details="auto"
                class="background-white"
                label="Customer Name*"
                :rules="[
                  (v) =>
                    (!!v && v.trim().length > 0) || 'Customer Name is required',
                ]"
                :error-messages="error.customer_name"
                :value="addressDetails.customer_name"
                @input="syncData($event, 'customer_name')"
              ></v-text-field>
            </v-col>
            <v-col cols="6" md="4" xl="4">
              <v-select
                outlined
                hide-details="auto"
                class="background-white"
                label="Customer Type"
                :items="customerType"
                :error-messages="error.customer_type"
                :value="addressDetails.customer_type"
                :menu-props="{ offsetY: true }"
                @change="syncData($event, 'customer_type')"
              ></v-select>
            </v-col>
            <v-col cols="6" md="4" xl="4">
              <v-text-field
                outlined
                hide-details="auto"
                class="background-white"
                label="Contact Person"
                :error-messages="error.contact_person"
                :value="addressDetails.contact_person"
                @input="syncData($event, 'contact_person')"
              ></v-text-field>
            </v-col>
            <v-col cols="6" md="4" xl="4">
              <v-text-field
                outlined
                hide-details="auto"
                class="background-white"
                label="Contact Number*"
                type="number"
                min="0"
                step="1"
                :error-messages="error.contact_number"
                :value="addressDetails.contact_number"
                :rules="[(v) => !!v || 'Contact Number is required']"
                @input="syncData($event, 'contact_number')"
              ></v-text-field>
            </v-col>
            <v-col cols="6" md="4" xl="4">
              <v-text-field
                outlined
                hide-details="auto"
                class="background-white"
                label="Contact email*"
                :rules="emailRules"
                :error-messages="error.contact_email"
                :value="addressDetails.contact_email"
                @input="syncData($event, 'contact_email')"
              ></v-text-field>
            </v-col>
          </v-row>
          <v-row class="pt-5">
            <v-col cols="6">
              <v-select
                outlined
                hide-details="auto"
                class="background-white"
                label="Project*"
                :items="projects"
                :rules="[(v) => !!v || 'Project is required']"
                :error-messages="error.project"
                :value="addressDetails.project"
                :menu-props="{ offsetY: true }"
                @change="syncData($event, 'project')"
              ></v-select>
            </v-col>
            <v-col cols="6">
              <v-text-field
                outlined
                hide-details="auto"
                class="background-white"
                label="Processing Time(Minutes)*"
                min="0"
                type="number"
                step="01"
                :rules="[(v) => !!v || 'Processing Time is required']"
                :error-messages="error.processing_time"
                :value="addressDetails.processing_time"
                @input="syncData($event, 'processing_time')"
              ></v-text-field>
            </v-col>
            <v-col cols="6">
              <v-row>
                <v-col cols="12">
                  <v-text-field
                    outlined
                    ref="customerAddressFormAddress"
                    hide-details="auto"
                    class="background-white"
                    placeholder="Enter Address*"
                    :rules="[
                      (v) =>
                        (!!v && v.trim().length > 0) || 'Address is required',
                    ]"
                    :error-messages="error.address"
                    :value="addressDetails.address"
                  ></v-text-field>
                </v-col>
                <v-col cols="6">
                  <v-text-field
                    outlined
                    hide-details="auto"
                    class="background-white"
                    label="Latitude"
                    type="number"
                    step="0.000001"
                    :error-messages="error.coordinates"
                    :value="addressDetails.coordinates.latitude"
                    @input="syncData($event, 'coordinates', 'latitude')"
                  ></v-text-field>
                </v-col>
                <v-col cols="6">
                  <v-text-field
                    outlined
                    hide-details="auto"
                    class="background-white"
                    label="Longitude"
                    type="number"
                    step="0.0000001"
                    :error-messages="error.coordinates"
                    :value="addressDetails.coordinates.longitude"
                    @input="syncData($event, 'coordinates', 'longitude')"
                  ></v-text-field>
                </v-col>
              </v-row>
            </v-col>
            <v-col cols="6">
              <v-textarea
                outlined
                hide-details="auto"
                class="background-white"
                label="Remark"
                :error-messages="error.remarks"
                :value="addressDetails.remarks"
                @input="syncData($event, 'remarks')"
              ></v-textarea>
            </v-col>
            <v-col cols="6">
              <v-switch
                label="WhatsApp Notifications"
                :true-value="true"
                :false-value="false"
                :input-value="addressDetails.whatsapp_notification"
                @change="syncData($event, 'whatsapp_notification')"
              ></v-switch>
            </v-col>
            <v-col cols="6">
              <v-switch
                label="E-mail Notifications"
                :true-value="true"
                :false-value="false"
                :input-value="addressDetails.email_notification"
                @change="syncData($event, 'email_notification')"
              ></v-switch>
            </v-col>
          </v-row>
          <v-row no-gutters class="pt-5">
            <v-col cols="12">
              <span class="text-h6">Tags</span>
            </v-col>
          </v-row>
          <v-row>
            <!-- NOte : this functionality used in future -->
            <!-- <v-col cols="5">
              <v-select
                :items="drivertagslist"
                v-model="drivertags"
                item-text="title"
                item-value="value"
                chips
                label="Driver Tags"
                multiple
                outlined
                hide-details="auto"
                class="background-white"
                :menu-props="{ offsetY: true }"
                @change="syncData($event, 'tags')"
              >
                <template v-slot:selection="{ item, index }">
                  <v-chip v-if="index == 0">
                    <span>{{ item.title }}</span>
                  </v-chip>
                  <span v-if="index == 0" class="grey--text text-caption">
                    ({{ drivertags.length }} selected)
                  </span>
                </template>
              </v-select>
            </v-col> -->
            <v-col cols="5">
              <CommonCustomselect
                :itemsList="vehicletagslist"
                v-model="vehicletags"
                item-text="title"
                item-value="title"
                label="Select Tag"
                :returnObject="false"
                :isMounted="addCustomerAddressFormDialog"
                @selectionChanged="syncData($event, 'tags')"
                class="background-white"
              />
            </v-col>
          </v-row>

          <v-row no-gutters class="pt-5">
            <v-col cols="6">
              <span class="text-h6">Time slots</span>
            </v-col>
          </v-row>
          <v-row v-for="(slot, index) in timeSlots" :key="index">
            <v-col cols="5">
              <v-menu
                v-model="menu1['fromTime' + index]"
                :close-on-content-click="false"
                :nudge-right="40"
                :return-value.sync="fromTime[index]"
                transition="scale-transition"
                offset-y
                max-width="290px"
                min-width="290px"
              >
                <template v-slot:activator="{ on, attrs }">
                  <v-text-field
                    label="From Time*"
                    outlined
                    type="time"
                    class="background-white"
                    hide-details="auto"
                    prepend-inner-icon="mdi-clock-time-four-outline"
                    readonly
                    :rules="[(v) => !!v || 'From time is required']"
                    :error-messages="error.from_time"
                    :value="slot.from_time"
                    v-bind="attrs"
                    v-on="on"
                  ></v-text-field>
                </template>
                <v-time-picker
                  format="24hr"
                  v-if="menu1['fromTime' + index]"
                  :value="slot.from_time"
                  full-width
                  @change="syncTimeSlot($event, index, 'from_time')"
                ></v-time-picker>
              </v-menu>
            </v-col>
            <v-col cols="5">
              <v-menu
                v-model="menu2['toTime' + index]"
                :close-on-content-click="false"
                :nudge-right="40"
                :return-value.sync="toTime[index]"
                transition="scale-transition"
                offset-y
                max-width="290px"
                min-width="290px"
              >
                <template v-slot:activator="{ on, attrs }">
                  <v-text-field
                    label="To Time*"
                    type="time"
                    outlined
                    class="background-white"
                    hide-details="auto"
                    prepend-inner-icon="mdi-clock-time-four-outline"
                    readonly
                    :rules="[
                      (v) => !!v || 'To time is required',
                      (v) =>
                        (v &&
                          v.slice(0, 5) !==
                            timeSlots[index].from_time.slice(0, 5)) ||
                        'From time and To time not be same',
                    ]"
                    :error-messages="error.to_time"
                    :value="slot.to_time"
                    v-bind="attrs"
                    v-on="on"
                  ></v-text-field>
                </template>
                <v-time-picker
                  :min="slot['from_time']"
                  format="24hr"
                  v-if="menu2['toTime' + index]"
                  :value="slot.to_time"
                  full-width
                  @change="syncTimeSlot($event, index, 'to_time')"
                ></v-time-picker>
              </v-menu>
            </v-col>
            <v-col cols="2" class="d-flex justify-center">
              <div class="pr-3">
                <v-btn
                  v-if="timeSlots.length > 1"
                  small
                  elevation="0"
                  class="error elevation-0 py-6"
                  @click="removeTimeSlot(index)"
                >
                  <v-icon>mdi-minus</v-icon>
                </v-btn>
              </div>
              <v-btn
                small
                class="primary elevation-0 py-6"
                :disabled="timeSlots.length >= 3"
                @click="addTimeSlot()"
              >
                <v-icon>mdi-plus</v-icon>
              </v-btn>
            </v-col>
          </v-row>
        </v-form>
      </v-card-text>

      <v-card-actions class="d-flex justify-center pt-2 pb-4">
        <v-btn
          class="primary text-uppercase mr-3"
          :disabled="!isFormVaid"
          @click="submit()"
        >
          <span>Submit</span>
        </v-btn>
        <v-btn
          v-show="formType == 'add'"
          class="primary text-uppercase"
          @click="clear()"
        >
          <span>Reset</span>
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  props: {
    value: Boolean,
    formType: {
      type: String,
      default: "add",
    },
  },
  mounted() {
    const interval = setInterval(async () => {
      if (
        this.$refs.customerAddressFormAddress &&
        window.google &&
        window.google.maps
      ) {
        clearInterval(interval);

        let input = this.$refs.customerAddressFormAddress.$refs.input;

        this.autocomplete = new window.google.maps.places.Autocomplete(input);

        this.autocomplete.addListener("place_changed", () => {
          let place = this.autocomplete.getPlace();
          let lat = place.geometry.location.lat();
          let lon = place.geometry.location.lng();

          setTimeout(() => {
            this.syncData(
              place.name + ", " + place.formatted_address,
              "address"
            );
            this.syncData(lat, "coordinates", "latitude");
            this.syncData(lon, "coordinates", "longitude");
          }, 100);
        });
      }
    }, 100);

    this.getTagList();

    setTimeout(() => {
      this.$forceUpdate();
    }, 1000);
  },
  data() {
    return {
      emailRules: [
        (v) =>
          /^(([^<>()[\]\\.,;:\s@']+(\.[^<>()\\[\]\\.,;:\s@']+)*)|('.+'))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/.test(
            v
          ) || "E-mail must be valid",
      ],
      timeDiff: 1,
      menu1: {},
      menu2: {},
      fromTime: [],
      toTime: [],
      radioGroup: "active",
      rcExpiryDate: null,
      drivertags: null,
      vehicletags: null,
      rcExpiryDatePicker: false,
      insuranceExpiryDatePicker: false,
      insuranceExpiryDate: null,
      isFormVaid: false,
      error: {},
      nonFieldError: [],
      customerType: [
        { text: "Business", value: "B2B" },
        { text: "Individual", value: "B2C" },
      ],
    };
  },
  computed: {
    addressSuggestations() {
      return this.$store.state.customer.customerAddress.addressList;
    },
    isEditMode() {
      return this.$store.state.customer.customerAddress.editMode;
    },
    projects() {
      return this.$store.getters["project/PROJECT_LIST_FOR_DROPDOWN"];
    },
    addCustomerAddressFormDialog: {
      get() {
        return this.value;
      },
      set(value) {
        this.$emit("input", value);
      },
    },
    addressDetails: {
      get() {
        let address =
          this.$store.state.customer.customerAddress.customerAddressDetails;
        this.drivertags = address.assigned_driver_tags
          ? address.assigned_driver_tags.map((item) => item.id)
          : [];
        this.vehicletags = address.assigned_vehicle_tags
          ? address.assigned_vehicle_tags.map((item) => item.tag)
          : [];
        return address;
      },
      set(value) {
        this.$store.commit(
          "customer/customerAddress/SET_CUSTOMER_ADDRESS_DETAILS",
          value
        );
      },
    },
    drivertagslist: {
      get() {
        return this.$store.state.customer.customerAddress.drivertaglist;
      },
      set(value) {
        this.$store.commit("customer/customerAddress/SET_DRIVER_TAGS", value);
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
    timeSlots: {
      get() {
        return this.$store.state.customer.customerAddress.time_slots;
      },
      set(value) {
        this.$store.commit("customer/customerAddress/SET_TIME_SLOT", value);
      },
    },
  },
  methods: {
    getTagList() {
      this.$store.dispatch("customer/customerAddress/GET_TAG_LIST");
    },
    closeDialog() {
      this.clear();
      this.addCustomerAddressFormDialog = false;
    },
    addTimeSlot() {
      this.$store.commit("customer/customerAddress/ADD_TIME_SLOT");
      let id = document.getElementById("customerAddressForm");
      id.scrollTop = id.scrollHeight;
    },
    removeTimeSlot(index) {
      this.$store.commit("customer/customerAddress/REMOVE_TIME_SLOT", index);
    },
    syncData(input_value, key, subKey) {
      if (this.error[key]) {
        this.error[key] = null;
        delete this.error[key];
      }
      this.$store.commit(
        "customer/customerAddress/SYNC_CUSTOMER_ADDRESS_DETAILS",
        {
          key: key,
          value: input_value,
          subKey: subKey,
        }
      );
    },
    syncTimeSlot(input_value, index, key) {
      if (this.error[key]) {
        this.error[key] = null;
        delete this.error[key];
      }
      this.$store.commit("customer/customerAddress/SYNC_TIME_SLOT", {
        index: index,
        value: input_value,
        key: key,
      });
      if (key == "from_time") {
        this.menu1["fromTime" + index] = false;
      } else if (key == "to_time") {
        this.menu2["toTime" + index] = false;
      }
    },
    clear() {
      this.$refs.customerAddressForm.resetValidation();
      this.addressDetails = {
        customer_name: null,
        customer_code: null,
        customer_type: null,
        contact_number: null,
        project: null,
        coordinates: {
          latitude: null,
          longitude: null,
        },
        address: null,
        contact_email: null,
        contact_person: null,
        remarks: null,
        processing_time: null,
        whatsapp_notification: false,
        email_notification: false,
        tags: [],
        assigned_tags: [],
      };
      this.vehicletags = []
      this.timeSlots = [
        {
          from_time: null,
          to_time: null,
        },
      ];
      this.error = {};
      this.nonFieldError = [];
    },
    submit() {
      this.addressDetails.tags = [
        ...this.drivertags,
        ...this.vehicletags,
      ].toString();

      let postData = this.addressDetails;
      postData.time_slots = this.timeSlots;
      if (this.isEditMode) {
        this.$store
          .dispatch(
            "customer/customerAddress/UPDATE_CUSTOMER_ADDRESS_DETAILS",
            postData
          )
          .then((result) => {
            this.closeDialog();
            this.$notifier.showMessage({
              content: "Address Successfully updated!",
              color: "success",
            });
          })
          .catch((err) => {
            if ("non_field_errors" in err) {
              this.nonFieldError = err.non_field_errors;
            }
            this.error = err;
          });
      } else {
        this.$store
          .dispatch("customer/customerAddress/ADD_CUSTOMER_ADDRESS_DETAILS", {
            isBulkupload: false,
            data: this.addressDetails,
          })
          .then((result) => {
            this.closeDialog();
            this.$notifier.showMessage({
              content: "Address Successfully added!",
              color: "success",
            });
          })
          .catch((err) => {
            if ("non_field_errors" in err) {
              this.nonFieldError = err.non_field_errors;
            }
            this.error = err;
          });
      }
    },
  },
};
</script>