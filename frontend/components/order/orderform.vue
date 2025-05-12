<template>
  <v-dialog
    v-model="orderFormDialog"
    persistent
    scrollable
    max-width="70%"
    @keydown.esc="closeDialog()"
  >
    <v-card class="pa-6">
      <v-card-title class="py-0">
        <v-row>
          <v-col cols="6">
            <span
              v-if="formType == 'add'"
              class="
                text-lg-subtitle-1 text-xl-h6 text-uppercase
                font-weight-black
                primary--text
              "
              >Create Order</span
            >
            <span
              v-else
              class="
                text-lg-subtitle-1 text-xl-h6 text-uppercase
                font-weight-black
                primary--text
              "
              >{{ formType }} Order</span
            >
          </v-col>
          <v-col cols="6" class="d-flex justify-end">
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
          </v-col>
          <v-col cols="12">
            <v-alert v-if="nonFieldError.length" dense type="error">
              <v-list
                class="pa-0"
                dense
                style="background: inherit !important"
                v-for="(error, i) in nonFieldError"
                :key="i"
              >
                <v-list-item dense style="min-height: 20px !important">
                  <span>{{ error }}</span>
                </v-list-item>
              </v-list>
            </v-alert>
          </v-col>
        </v-row>
      </v-card-title>

      <v-card-text class="pt-4 pb-12" id="orderFormCard">
        <v-form
          v-if="orderFormDialog"
          id="orderForm"
          ref="orderForm"
          v-model="isValid"
          class="pt-3"
        >
          <v-row>
            <v-col cols="6" lg="3">
              <v-text-field
                outlined
                hide-details="auto"
                class="background-white"
                label="SO Number*"
                name="reference_number"
                :rules="[
                  (v) =>
                    (!!v && v.trim().length > 0) || 'SO Number is required',
                ]"
                :value="orderFormDetails.reference_number"
                :error-messages="error.reference_number"
                @input="syncData($event, 'reference_number')"
              ></v-text-field>
            </v-col>
            <v-col cols="6" lg="3">
              <v-menu
                ref="orderDateMenu"
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
                    label="Order Date*"
                    prepend-inner-icon="mdi-calendar"
                    readonly
                    outlined
                    hide-details="auto"
                    name="execution_date"
                    v-bind="attrs"
                    v-on="on"
                    class="background-white"
                    :error-messages="error.execution_date"
                    :rules="[(v) => !!v || 'Order date is required']"
                    :value="orderFormDetails.execution_date"
                    @input="syncData($event, 'execution_date')"
                    :menu-props="{ offsetY: true }"
                  ></v-text-field>
                </template>
                <v-date-picker
                  no-title
                  scrollable
                  reactive
                  :min="nowDate"
                  :value="orderFormDetails.execution_date"
                  @click:date="
                    syncData($event, 'execution_date'),
                      $refs.orderDateMenu.save(date)
                  "
                >
                </v-date-picker>
              </v-menu>
            </v-col>
            <v-col ols="6" lg="3">
              <v-select
                :items="orderType"
                label="Order type"
                :menu-props="{ offsetY: true }"
                outlined
                name="order_type"
                item-text="name"
                item-value="value"
                :value="orderFormDetails.order_type"
                @change="syncData($event, 'order_type')"
                hide-details="auto"
                :readonly="formType != 'add'"
                class="mt-0 pt-0"
              >
              </v-select>
            </v-col>
            <v-col cols="6" lg="3">
              <v-text-field
                outlined
                hide-details="auto"
                class="background-white"
                type="number"
                label="Order Value"
                min="0"
                name="order_value"
                :error-messages="error.order_value"
                :value="orderFormDetails.order_value"
                @input="syncData($event, 'order_value')"
              ></v-text-field>
            </v-col>
            <v-col cols="6" lg="3">
              <v-select
                hide-details="auto"
                class="background-white"
                outlined
                :menu-props="{ offsetY: true }"
                label="Barcode Scanning"
                :items="barcodeScanning"
                name="barcode_scanning"
                item-text="name"
                item-value="value"
                :error-messages="error.barcode_scanning"
                :value="orderFormDetails.barcode_scanning"
                @input="syncData($event, 'barcode_scanning')"
              ></v-select>
            </v-col>
            <v-col cols="6" lg="3">
              <v-select
                hide-details="auto"
                class="background-white"
                outlined
                label="Proof of delivery"
                :menu-props="{ offsetY: true }"
                name="pod_required"
                :items="podRequired"
                item-text="name"
                item-value="value"
                :error-messages="error.pod_required"
                :value="orderFormDetails.pod_required"
                @input="syncData($event, 'pod_required')"
              ></v-select>
            </v-col>
            <v-col cols="6" lg="3">
              <v-select
                hide-details="auto"
                class="background-white"
                outlined
                :menu-props="{ offsetY: true }"
                label="Customer notification"
                name="customer_notifications"
                :items="customerNotifications"
                item-text="name"
                item-value="value"
                :value="orderFormDetails.customer_notifications"
                @input="syncData($event, 'customer_notifications')"
              ></v-select>
            </v-col>
            <v-col cols="3">
              <v-text-field
                outlined
                hide-details="auto"
                label="Invoice Number"
                name="invoice_number"
                :error-messages="error.invoice_number"
                :value="orderFormDetails.invoice_number"
                @input="syncData($event, 'invoice_number')"
              ></v-text-field>
            </v-col>
            <v-col cols="6" lg="3">
              <v-select
                hide-details="auto"
                class="background-white"
                :menu-props="{ offsetY: true }"
                outlined
                label="Payment type"
                name="payment_type"
                :items="paymentType"
                item-text="name"
                item-value="value"
                :error-messages="error.payment_type"
                :value="orderFormDetails.payment_type"
                @change="syncData($event, 'payment_type')"
              ></v-select>
            </v-col>
            <v-col cols="3">
              <v-text-field
                outlined
                hide-details="auto"
                label="Instructions"
                name="instructions"
                :error-messages="error.instructions"
                :value="orderFormDetails.instructions"
                @input="syncData($event, 'instructions')"
              ></v-text-field>
            </v-col>
            <v-col cols="6">
              <v-text-field
                outlined
                hide-details="auto"
                label="Order Remarks"
                name="order_remarks"
                :error-messages="error.order_remarks"
                :value="orderFormDetails.order_remarks"
                @input="syncData($event, 'order_remarks')"
              ></v-text-field>
            </v-col>
            <v-col
              cols="3"
              v-if="
                formType == 'edit' && orderFormDetails.payment_type == 'cod'
              "
            >
              <v-text-field
                outlined
                hide-details="auto"
                label="Payment received"
                name="payment_received"
                :error-messages="error.payment_received"
                :value="orderFormDetails.payment_received"
                @input="syncData($event, 'payment_received')"
              ></v-text-field>
            </v-col>
            <v-col v-if="formType != 'add'" cols="6" lg="3">
              <v-select
                outlined
                hide-details="auto"
                class="background-white"
                name="status"
                :items="orderStatus"
                item-text="name"
                item-value="value"
                label="Order Status"
                :error-messages="error.status"
                :value="orderFormDetails.status"
                @change="syncData($event, 'status')"
              ></v-select>
            </v-col>
            <v-col
              v-if="formType != 'add' && orderFormDetails.status == 'cancelled'"
              cols="6"
              lg="9"
            >
              <v-text-field
                outlined
                hide-details="auto"
                class="background-white"
                name="cancellation_remarks"
                label="Cancellation Remarks"
                :rules="[(v) => !!v || 'Cancellation remarks is required']"
                :error-messages="error.cancellation_remarks"
                :value="orderFormDetails.cancellation_remarks"
                @change="syncData($event, 'cancellation_remarks')"
              ></v-text-field>
            </v-col>
            <v-col cols="12" class="mt-4" v-if="formType == 'edit'">
              <span class="font-weight-bold text-subtitle-1">
                Upload attachment
              </span>
            </v-col>

            <v-col cols="4" v-if="formType == 'edit'">
              <v-file-input
                ref="fileInput"
                :clearable="true"
                hide-details
                type="file"
                multiple="multiple"
                v-model="uploadFiles"
                label="Upload Document"
                prepend-inner-icon="mdi-attachment mdi-rotate-90"
                accept="image/*, .pdf"
                prepend-icon=""
                outlined
                @change="getFileData($event)"
                @click:clear="clearFileSelection()"
              ></v-file-input>
            </v-col>
            <v-col
              cols="12"
              class="mt-4"
              v-if="formType == 'edit' && documentList.length != 0"
            >
              <span class="font-weight-bold text-subtitle-1"> New Upload </span>
            </v-col>

            <v-col
              cols="6"
              lg="9"
              v-if="formType == 'edit' && documentList.length != 0"
            >
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
                        <h4>{{ data.file.name }}</h4>
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
            <v-col
              cols="12"
              class="mt-4"
              v-if="
                formType == 'edit' &&
                orderFormDetails.order_attachments &&
                orderFormDetails.order_attachments.length != 0
              "
            >
              <span class="font-weight-bold text-subtitle-1">
                Order Attachments
              </span>
            </v-col>

            <v-col
              cols="6"
              lg="9"
              v-if="
                formType == 'edit' &&
                orderFormDetails.order_attachments &&
                orderFormDetails.order_attachments.length != 0
              "
            >
              <v-card
                elevation="0"
                outlined
                v-for="(data, j) in orderFormDetails.order_attachments"
                :key="j"
              >
                <v-card-text>
                  <v-row>
                    <v-col cols="9">
                      <a :href="data.url" target="_black">
                        <h4>{{ data.name }}</h4>
                      </a>
                    </v-col>
                    <v-col cols="2"> </v-col>
                    <v-col cols="1">
                      <v-icon
                        small
                        color="primary"
                        @click="deleteFile(data.id, j)"
                        >mdi-close</v-icon
                      >
                    </v-col>
                  </v-row>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>

          <v-row v-if="orderFormDetails.status != 'cancelled'">
            <v-col cols="6" class="mt-4">
              <span class="font-weight-bold text-subtitle-1"
                >Customer Details
              </span>
            </v-col>
            <v-col
              v-if="formType == 'add'"
              cols="6"
              class="mt-4 d-flex justify-end"
            >
              <span class="font-weight-bold text-subtitle-1">
                <v-radio-group
                  row
                  hide-details="auto"
                  class="ma-0"
                  name="new_customer"
                  mandatory
                  v-model="customerGroup"
                  @change="customerTypeChange"
                >
                  <v-radio label="Existing Customer" :value="false"></v-radio>
                  <v-radio label="New Customer" :value="true"></v-radio>
                </v-radio-group>
              </span>
            </v-col>
          </v-row>
          <hr class="my-4" v-if="orderFormDetails.status != 'cancelled'" />
          <!-------------------------- order type is new & customer already exists -------------------------->
          <v-row
            v-if="
              formType == 'add' &&
              !customerGroup &&
              orderFormDetails.status != 'cancelled'
            "
          >
            <v-col cols="6" lg="3">
              <v-combobox
                outlined
                hide-details="auto"
                class="background-white"
                label="Customer code*"
                :loading="isLoading"
                :search-input.sync="search"
                :items="customerCode"
                item-text="customer_code"
                item-value="id"
                name="customer_code"
                :rules="[(v) => !!v || 'Customer code is required']"
                :error-messages="error.customer_code"
                :value="orderFormDetails.customer_code"
                @change="setCustomerCode"
                return-object
              >
                <template v-slot:item="{ item }">
                  <v-list-item-content>
                    <v-list-item-title
                      v-text="item.customer_code"
                    ></v-list-item-title>
                  </v-list-item-content>
                </template>
              </v-combobox>
            </v-col>
            <v-col cols="6" lg="3">
              <v-text-field
                outlined
                hide-details="auto"
                class="background-white"
                label="Customer name*"
                name="customer_name"
                :error-messages="error.customer_name"
                :rules="[(v) => !!v || 'Customer name is required']"
                :value="orderFormDetails.customer_name"
                @input="syncData($event, 'customer_name')"
              ></v-text-field>
            </v-col>
            <v-col cols="6" lg="3">
              <v-text-field
                outlined
                hide-details="auto"
                class="background-white"
                label="Contact person"
                name="contact_person"
                :error-messages="error.contact_person"
                :value="orderFormDetails.contact_person"
                @input="syncData($event, 'contact_person')"
              ></v-text-field>
            </v-col>
            <v-col cols="6" lg="3">
              <v-text-field
                outlined
                hide-details="auto"
                type="number"
                class="background-white"
                label="Contact number"
                name="contact_number"
                min="0"
                :error-messages="error.contact_number"
                :value="orderFormDetails.contact_number"
                @input="syncData($event, 'contact_number')"
              ></v-text-field>
            </v-col>
            <v-col cols="6" lg="3">
              <v-text-field
                outlined
                hide-details="auto"
                class="background-white"
                label="Contact email"
                name="contact_email"
                :error-messages="error.contact_email"
                :value="orderFormDetails.contact_email"
                @input="syncData($event, 'contact_email')"
              ></v-text-field>
            </v-col>
          </v-row>
          <!------------------------------- Order & customer both are new  ------------------------------->
          <v-row
            v-if="
              formType == 'add' &&
              customerGroup &&
              orderFormDetails.status != 'cancelled'
            "
          >
            <!--------------------------------- Customer form --------------------------------->
            <v-row class="pt-6">
              <v-col cols="6" md="3">
                <v-text-field
                  outlined
                  hide-details="auto"
                  class="background-white"
                  label="Customer Code*"
                  :rules="[
                    (v) =>
                      (!!v && v.trim().length > 0) ||
                      'Customer Code is required',
                  ]"
                  :error-messages="error.customer_code"
                  :value="orderFormDetails.customer_code"
                  @input="syncData($event, 'customer_code')"
                ></v-text-field>
              </v-col>
              <v-col cols="6" md="3">
                <v-text-field
                  outlined
                  hide-details="auto"
                  class="background-white"
                  label="Customer Name*"
                  name="customer_name"
                  :rules="[
                    (v) =>
                      (!!v && v.trim().length > 0) ||
                      'Customer Name is required',
                  ]"
                  :error-messages="error.customer_name"
                  :value="orderFormDetails.customer_name"
                  @input="syncData($event, 'customer_name')"
                ></v-text-field>
              </v-col>
              <v-col cols="6" md="3">
                <v-select
                  outlined
                  hide-details="auto"
                  class="background-white"
                  :menu-props="{ offsetY: true }"
                  label="Customer Type"
                  :items="customerType"
                  name="customer_type"
                  :error-messages="error.customer_type"
                  :value="orderFormDetails.customer_type"
                  @change="syncData($event, 'customer_type')"
                ></v-select>
              </v-col>
              <v-col cols="6" md="3">
                <v-text-field
                  outlined
                  hide-details="auto"
                  class="background-white"
                  label="Contact Person"
                  name="contact_person"
                  :error-messages="error.contact_person"
                  :value="orderFormDetails.contact_person"
                  @input="syncData($event, 'contact_person')"
                ></v-text-field>
              </v-col>
              <v-col cols="6" md="3">
                <v-text-field
                  outlined
                  hide-details="auto"
                  class="background-white"
                  label="Contact Number"
                  name="contact_number"
                  type="number"
                  min="0"
                  step="1"
                  :error-messages="error.contact_number"
                  :value="orderFormDetails.contact_number"
                  @input="syncData($event, 'contact_number')"
                ></v-text-field>
              </v-col>
              <v-col cols="6" md="3">
                <v-text-field
                  outlined
                  hide-details="auto"
                  class="background-white"
                  label="Contact email*"
                  name="contact_email"
                  :rules="emailRules"
                  :error-messages="error.contact_email"
                  :value="orderFormDetails.contact_email"
                  @input="syncData($event, 'contact_email')"
                ></v-text-field>
              </v-col>
              <v-col cols="3">
                <v-select
                  outlined
                  hide-details="auto"
                  class="background-white"
                  label="Project*"
                  :menu-props="{ offsetY: true }"
                  name="project"
                  :items="allProjects"
                  :rules="[(v) => !!v || 'Project is required']"
                  :error-messages="error.project"
                  :value="orderFormDetails.project"
                  @change="syncData($event, 'project')"
                ></v-select>
              </v-col>
              <v-col cols="3">
                <v-text-field
                  outlined
                  hide-details="auto"
                  class="background-white"
                  label="Processing Time(Minutes)*"
                  name="processing_time"
                  min="0"
                  type="number"
                  step="01"
                  :error-messages="error.processing_time"
                  :value="orderFormDetails.processing_time"
                  :rules="[(v) => !!v || 'Processing Time is required']"
                  @input="syncData($event, 'processing_time')"
                ></v-text-field>
              </v-col>
              <v-col cols="12">
                <v-text-field
                  outlined
                  ref="customerAddressFormAddress"
                  hide-details="auto"
                  class="background-white"
                  name="address"
                  placeholder="Enter Address*"
                  :rules="[
                    (v) =>
                      (!!v && v.trim().length > 0) || 'Address is required',
                  ]"
                  :error-messages="error.address"
                  :value="orderFormDetails.address"
                  @input="syncData($event, 'address')"
                ></v-text-field>
              </v-col>
              <v-col cols="3">
                <v-text-field
                  outlined
                  hide-details="auto"
                  class="background-white"
                  label="Latitude"
                  type="number"
                  step="0.000001"
                  name="latitude"
                  :error-messages="error.coordinates"
                  :value="orderFormDetails.coordinates.latitude"
                  @input="syncData($event, 'coordinates', 'latitude')"
                ></v-text-field>
              </v-col>
              <v-col cols="3">
                <v-text-field
                  outlined
                  hide-details="auto"
                  class="background-white"
                  label="Longitude"
                  type="number"
                  step="0.0000001"
                  name="longitude"
                  :error-messages="error.coordinates"
                  :value="orderFormDetails.coordinates.longitude"
                  @input="syncData($event, 'coordinates', 'longitude')"
                ></v-text-field>
              </v-col>
              <!------------------------ New customer time slot ----------------------------->
              <v-col cols="3">
                <v-text-field
                  label="From Time*"
                  outlined
                  type="time"
                  class="background-white"
                  hide-details="auto"
                  name="from_time"
                  :error-messages="error.delivery_window_start"
                  :value="orderFormDetails.delivery_window_start"
                  :rules="[(v) => !!v || 'From time is required']"
                  @change="syncData($event, 'delivery_window_start')"
                ></v-text-field>
              </v-col>
              <v-col cols="3">
                <v-text-field
                  label="To Time*"
                  type="time"
                  outlined
                  class="background-white"
                  hide-details="auto"
                  name="to_time"
                  :error-messages="error.delivery_window_end"
                  :value="orderFormDetails.delivery_window_end"
                  :rules="[
                    (v) => !!v || 'To time is required',
                    (v) =>
                      (orderFormDetails.delivery_window_start &&
                        v > orderFormDetails.delivery_window_start) ||
                      'To time can not be less than from time',
                  ]"
                  @change="syncData($event, 'delivery_window_end')"
                ></v-text-field>
              </v-col>
              <v-col cols="6">
                <v-switch
                  label="WhatsApp Notifications"
                  :true-value="true"
                  :false-value="false"
                  :input-value="orderFormDetails.whatsapp_notification"
                  @change="syncData($event, 'whatsapp_notification')"
                ></v-switch>
              </v-col>
              <v-col cols="6">
                <v-switch
                  label="E-mail Notifications"
                  :true-value="true"
                  :false-value="false"
                  :input-value="orderFormDetails.email_notification"
                  @change="syncData($event, 'email_notification')"
                ></v-switch>
              </v-col>
            </v-row>
          </v-row>
          <!--------------------------------------- If form type is edit --------------------------------------->
          <v-row
            v-if="formType == 'edit' && orderFormDetails.status != 'cancelled'"
          >
            <v-col cols="6" md="4" xl="4">
              <v-text-field
                outlined
                hide-details="auto"
                class="background-white"
                label="Contact Person"
                name="contact_person"
                :error-messages="error.contact_person"
                :value="orderFormDetails.contact_person"
                @input="syncData($event, 'contact_person')"
              ></v-text-field>
            </v-col>
            <v-col cols="6" md="4" xl="4">
              <v-text-field
                outlined
                hide-details="auto"
                class="background-white"
                label="Contact Number"
                name="contact_number"
                type="number"
                min="0"
                step="1"
                :error-messages="error.contact_number"
                :value="orderFormDetails.contact_number"
                @input="syncData($event, 'contact_number')"
              ></v-text-field>
            </v-col>
            <v-col cols="6" md="4" xl="4">
              <v-text-field
                outlined
                hide-details="auto"
                class="background-white"
                label="Contact email*"
                name="contact_email"
                :rules="emailRules"
                :error-messages="error.contact_email"
                :value="orderFormDetails.contact_email"
                @input="syncData($event, 'contact_email')"
              ></v-text-field>
            </v-col>
            <v-col cols="12">
              <v-text-field
                outlined
                ref="customerAddressFormAddress"
                hide-details="auto"
                class="background-white"
                name="address"
                placeholder="Enter Address*"
                :rules="[
                  (v) => (!!v && v.trim().length > 0) || 'Address is required',
                ]"
                :error-messages="error.address"
                :value="orderFormDetails.address"
                @input="syncData($event, 'address')"
              ></v-text-field>
            </v-col>
            <v-col cols="4">
              <v-text-field
                outlined
                hide-details="auto"
                class="background-white"
                label="Latitude"
                type="number"
                step="0.000001"
                name="latitude"
                :error-messages="error.coordinates"
                :value="orderFormDetails.coordinates.latitude"
                @input="syncData($event, 'coordinates', 'latitude')"
              ></v-text-field>
            </v-col>
            <v-col cols="4">
              <v-text-field
                outlined
                hide-details="auto"
                class="background-white"
                label="Longitude"
                type="number"
                step="0.0000001"
                name="longitude"
                :error-messages="error.coordinates"
                :value="orderFormDetails.coordinates.longitude"
                @input="syncData($event, 'coordinates', 'longitude')"
              ></v-text-field>
            </v-col>
            <v-col cols="4">
              <v-text-field
                outlined
                type="time"
                hide-details="auto"
                class="background-white"
                label="Delivery Window Start"
                name="delivery_window_start"
                :error-messages="error.delivery_window_start"
                :value="orderFormDetails.delivery_window_start"
                @input="syncData($event, 'delivery_window_start')"
              ></v-text-field>
            </v-col>
            <v-col cols="4">
              <v-text-field
                outlined
                type="time"
                hide-details="auto"
                class="background-white"
                label="Delivery Window End"
                name="delivery_window_end"
                :error-messages="error.delivery_window_end"
                :value="orderFormDetails.delivery_window_end"
                @input="syncData($event, 'delivery_window_end')"
              ></v-text-field>
            </v-col>
          </v-row>

          <v-row v-if="orderFormDetails.status != 'cancelled'">
            <v-col cols="12" class="mt-4">
              <span class="font-weight-bold text-subtitle-1"> Add Item </span>
              <hr class="my-4" />
            </v-col>

            <v-col
              cols="12"
              class="px-6"
              v-if="orderItems && orderItems.length"
            >
              <v-row v-for="(item, i) in orderItems" :key="i">
                <v-col cols="3" class="pl-0">
                  <v-combobox
                    outlined
                    hide-details="auto"
                    dense
                    label="Item Code*"
                    class="background-white"
                    :loading="isLoading"
                    :search-input.sync="searchItem[i]"
                    :items="itemCode"
                    item-text="item_no"
                    item-value="item_no"
                    :rules="[(v) => !!v || 'Item code is required']"
                    :error-messages="error.item_no"
                    :value="item.item_no"
                    @focus="selectedItemIndex = i"
                    @change="setItemCode($event, i)"
                    return-object
                  >
                    <template v-slot:item="{ item }">
                      <v-list-item-content>
                        <v-list-item-title
                          v-text="item.item_no"
                        ></v-list-item-title>
                      </v-list-item-content>
                    </template>
                  </v-combobox>
                </v-col>
                <v-col cols="3">
                  <v-text-field
                    outlined
                    hide-details="auto"
                    dense
                    label="Item Name*"
                    :error-messages="error.item_description"
                    :rules="[
                      (v) =>
                        (!!v && v.trim().length > 0) || 'Item name is required',
                    ]"
                    :value="item.item_description"
                    @input="syncItemData($event, 'item_description', i)"
                  ></v-text-field>
                </v-col>
                <v-col cols="2">
                  <v-text-field
                    type="number"
                    min="1"
                    outlined
                    hide-details="auto"
                    dense
                    label="Quantity*"
                    :error-messages="error.quantity"
                    :rules="[
                      (v) => !!v || 'Quantity is required',
                      (v) => v > 0 || 'Quantity can not be 0',
                    ]"
                    :value="item.quantity"
                    @input="syncItemData($event, 'quantity', i)"
                  ></v-text-field>
                </v-col>
                <v-col cols="2">
                  <v-text-field
                    v-show="
                      formType != 'add' &&
                      orderFormDetails.status != 'unassigned' &&
                      orderFormDetails.status != 'assigned' &&
                      orderFormDetails.status != 'failed' &&
                      orderFormDetails.status != 'cancelled'
                    "
                    type="number"
                    min="1"
                    outlined
                    hide-details="auto"
                    dense
                    label="Delivered Quantity"
                    :error-messages="error.delivered_quantity"
                    :value="item.delivered_quantity"
                    @input="syncItemData( parseInt($event), 'delivered_quantity', i)"
                  ></v-text-field>
                </v-col>
                <v-col cols="2" class="d-flex justify-center">
                  <div class="pr-3">
                    <v-btn
                      :small="$vuetify.breakpoint.xl"
                      :x-small="$vuetify.breakpoint.lgAndDown"
                      v-if="orderItems.length > 1"
                      class="light_grey elevation-0 py-5"
                      @click="removeItem(i)"
                      :disabled="canRemoveItem(item)"
                    >
                      <v-icon>mdi-minus</v-icon>
                    </v-btn>
                  </div>
                  <v-btn
                    :small="$vuetify.breakpoint.xl"
                    :x-small="$vuetify.breakpoint.lgAndDown"
                    class="primary elevation-0 py-5"
                    @click="addItem()"
                  >
                    <v-icon>mdi-plus</v-icon>
                  </v-btn>
                </v-col>
              </v-row>
            </v-col>
          </v-row>
        </v-form>
      </v-card-text>
      <v-card-actions class="d-flex justify-center">
        <v-btn
          type="submit"
          :disabled="!isValid"
          width="9%"
          class="primary"
          @click.prevent="submitOrderForm()"
        >
          <span>Submit</span>
        </v-btn>
        <v-btn
          type="reset"
          v-if="formType == 'add'"
          width="9%"
          class="primary mr-4"
          @click="clear()"
        >
          <span>Reset</span>
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import authHeader from "~/store/authHeader.js";

export default {
  props: {
    value: Boolean,
    formType: {
      type: String,
      default: "add",
    },
  },
  watch: {
    async search(val) {
      // Items have already been loaded
      this.isLoading = true;
      // Lazily load input items
      if (val) {
        await this.$axios
          .get(`api/v1/customer_address/`, {
            headers: authHeader(),
            params: { search: val.toLowerCase() },
          })
          .then((res) => {
            this.customerCode = res.data.results;
          })
          .catch((err) => {})
          .finally(() => (this.isLoading = false));
      }
    },
    searchItem: {
      handler: function (val) {
        this.isLoadingItem = true;

        if (val && val != null) {
          this.$axios
            .get(`/api/v1/items/`, {
              headers: authHeader(),
              params: { search: val[this.selectedItemIndex] },
            })
            .then((res) => {
              this.itemCode = res.data.results;
            })
            .catch((err) => {})
            .finally(() => (this.isLoadingItem = false));
        }
      },
      deep: true,
    },
  },
  data() {
    return {
      uploadFiles: null,
      emailRules: [
        (v) =>
          /^(([^<>()[\]\\.,;:\s@']+(\.[^<>()\\[\]\\.,;:\s@']+)*)|('.+'))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/.test(
            v
          ) || "E-mail must be valid",
      ],
      // variables for autocomplete
      longitude: null,
      latitude: null,
      // variables for widgets
      menuFromTime: false,
      menuToTime: false,
      customerGroup: false,
      nonFieldError: [],
      isLoading: false,
      isLoadingItem: false,
      customerCode: [],
      documentList: [],
      itemCode: [],
      error: {
        customer_code: [],
      },
      search: "",
      searchItem: [],
      customerType: [
        { text: "Business", value: "B2B" },
        { text: "Individual", value: "B2C" },
      ],
      selectedItemIndex: 0,
      customerNotifications: [
        {
          name: "Yes",
          value: true,
        },
        {
          name: "No",
          value: false,
        },
      ],
      podRequired: [
        {
          name: "Yes",
          value: true,
        },
        {
          name: "No",
          value: false,
        },
      ],
      barcodeScanning: [
        {
          name: "Yes",
          value: true,
        },
        {
          name: "No",
          value: false,
        },
      ],
      orderType: [
        {
          name: "Delivery",
          value: "delivery",
        },
        {
          name: "Pickup",
          value: "pickup",
        },
      ],
      paymentType: [
        {
          name: "Prepaid",
          value: "prepaid",
        },
        {
          name: "Cash on delivery",
          value: "cod",
        },
        {
          name: "Credit",
          value: "credit",
        },
      ],
      orderStatus: [
        {
          name: "Unassigned",
          value: "unassigned",
        },
        {
          name: "Assigned",
          value: "assigned",
        },
        {
          name: "Shipped",
          value: "pickedup",
        },
        {
          name: "Partially Delivered",
          value: "partially_delivered",
        },
        {
          name: "Delivered",
          value: "successful",
        },
        {
          name: "Returned",
          value: "failed",
        },
        {
          name: "Cancelled",
          value: "cancelled",
        },
      ],
      DatePickerMenu1: false,
      isValid: false,
      date: null,
      nowDate: new Date().toISOString().slice(0, 10),
      executed: true,
    };
  },
  computed: {
    allProjects() {
      return this.$store.getters["project/PROJECT_LIST_FOR_DROPDOWN"];
    },
    orderFormDetails: {
      get() {
        return this.$store.state.order.orderFormStore.formOrder;
      },
      set(value) {
        this.$store.commit(
          "order/orderFormStore/SET_ORDER_FORM_DETAILS",
          value
        );
      },
    },
    orderItems: {
      get() {
        return this.$store.state.order.orderFormStore.items;
      },
      set(value) {
        this.$store.commit(
          "order/orderFormStore/SET_ORDER_ITEM_FORM_DETAILS",
          value
        );
      },
    },
    orderFormDialog: {
      get() {
        return this.value;
      },
      set(value) {
        this.$emit("input", value);
      },
    },
  },
  methods: {
    deleteFile(id, index) {
      let playload = {
        id: id,
        index: index,
      };
      this.$store
        .dispatch("order/orderFormStore/REMOVE_ATTACHMENT_INTO_ORDER", playload)
        .then((response) => {
          this.$notifier.showMessage({
            content: `Deleted Attachment Sucessfully`,
            color: "error",
          });
        });
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
    generateUrl(file) {
      return URL.createObjectURL(file);
    },
    getFileData(files) {
      if (files) {
        let l = files.length;
        let i = 0;
        while (l !== i) {
          const file = files[i];
          i++;
          if (this.imageFileCheck(file.name)) {
            this.documentList.push({
              file: file,
            });
          } else {
            this.clearFileSelection();
            return false;
          }
        }
      } else {
        this.clearFileSelection();
      }
    },
    clearFileSelection() {
      this.$refs.fileInput.reset();
      this.documentList = [];
    },
    getSize(bytes) {
      var sizes = ["Bytes", "KB", "MB", "GB", "TB"];
      if (bytes == 0) return "0 Byte";
      var i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)));
      return Math.round(bytes / Math.pow(1024, i), 2) + " " + sizes[i];
    },
    removeFile(index) {
      this.documentList.splice(index, 1);
    },
    canRemoveItem(item) {
      if (
        this.orderFormDetails.status == "unassigned" &&
        this.orderFormDetails.status == "assigned"
      ) {
        return false;
      } else {
        if (item.isNewItem) {
          return false;
        } else {
          return true;
        }
      }
    },
    customerTypeChange() {
      this.syncData(null, "customer_code");
      this.syncData(null, "customer_name");
      this.syncData(null, "contact_number");
      this.syncData(null, "contact_email");
      this.syncData(null, "contact_person");
      this.syncData(null, "customer_address");
      this.syncData(null, "address");
      this.syncData(null, "project");
      this.syncData(null, "coordinates", "latitude");
      this.syncData(null, "coordinates", "longitude");
      if (this.$refs.orderForm) {
        this.$refs.orderForm.resetValidation();
      }
      this.executed = true;
    },
    setItemCode(e, index) {
      if (e != null && e.item_description != null) {
      this.syncItemData(e.item_description, "item_description", index);
      this.syncItemData(e.item_no, "item_no", index);
      }
    },
    setCustomerCode(e) {
      this.syncData(e.customer_code, "customer_code");
      this.syncData(e.customer_name, "customer_name");
      this.syncData(e.contact_number, "contact_number");
      this.syncData(e.contact_email, "contact_email");
      this.syncData(e.contact_person, "contact_person");
      this.syncData(e.address, "customer_address");
      this.syncData(e.project, "project");
    },
    async closeDialog() {
      this.orderFormDialog = false;
      await this.clear();
    },
    syncData(input_value, key, subKey) {
      if (this.error[key]) {
        this.error[key] = null;
        delete this.error[key];
      }
      if (key && typeof input_value != typeof undefined) {
        this.$store.commit("order/orderFormStore/SYNC_ORDER_FORM_DETAILS", {
          key: key,
          value: input_value,
          subKey: subKey,
        });
        if (key == "address" && this.executed) {
          this.executed = false;
          this.autoCompleteAddress();
        }
      }
    },
    syncItemData(input_value, key, index) {
      this.$store.commit("order/orderFormStore/SYNC_ORDER_ITEMS_FORM_DETAILS", {
        key: key,
        value: input_value,
        index: index,
      });
      this.$forceUpdate();
    },
    addItem() {
      this.$store.commit("order/orderFormStore/ADD_ITEM_TO_LIST");
      let id = document.getElementById("orderFormCard");
      id.scrollTop = id.scrollHeight;
    },
    removeItem(index) {
      this.$store.commit("order/orderFormStore/REMOVE_ITEM_FROM_LIST", index);
      this.searchItem.splice(index, 1);
    },
    generateData() {
      let orderData = this.orderFormDetails;
      if (this.orderFormDetails.status == "failed") {
        orderData.order_items = this.orderItems.map((item) => {
          return {
            item_no: item.item_no,
            item_description: item.item_description,
            quantity: item.quantity,
            delivered_quantity: 0,
          };
        });
      } else {
        orderData.order_items = this.orderItems;
      }
      return orderData;
    },
    submitOrderForm() {
      this.checkCustomerType(this.customerGroup);
      let postData = this.generateData();

      if (this.formType == "add") {
        this.$store
          .dispatch("order/orderFormStore/ADD_ORDER", postData)
          .then((result) => {
            this.$parent.get_order_list(true);
            this.closeDialog();
            this.$notifier.showMessage({
              content: "Order successfully Added!",
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
          .dispatch("order/orderFormStore/UPDATE_ORDER_DETAILS", postData)
          .then((result) => {
            let postDate = new FormData();
            this.documentList.forEach((file, index) => {
              postDate.append("attachments", file.file);
            });
            postDate.append("attachment_type", "order")

            let playload = {
              id: result.id,
              data: postDate,
            };
            this.$store
              .dispatch(
                "order/orderFormStore/ADD_ATTACHMENT_INTO_ORDER",
                playload
              )
              .then((response) => {
                this.closeDialog();
                this.$notifier.showMessage({
                  content: "Order successfully Updated!",
                  color: "success",
                });
                this.$store.commit(
                  "order/orderListStore/UPDATE_ORDER_IN_THE_LIST",
                  result
                );
                this.$store.dispatch(
                  "order/orderDetailStore/GET_ORDER_DETAILS",
                  result.id
                );
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
    checkCustomerType(new_customer) {
      this.orderFormDetails.new_customer = new_customer;
      if (!new_customer && this.formType == "add") {
        delete this.orderFormDetails.coordinates;
      } else if (new_customer && this.formType == "add") {
        delete this.orderFormDetails.customer_address;
      } else {
        delete this.orderFormDetails.new_customer;
      }
    },
    clear() {
      // this.$refs.orderForm.reset();
      this.$store.commit("order/orderFormStore/EMPTY_ORDER_FORM_DETAILS");
      this.$store.commit("order/orderFormStore/EMPTY_ORDER_ITEM_FORM_DETAILS");
      this.error = {};
      this.nonFieldError = [];
      this.executed = true;
      this.documentList = [];
    },
    autoCompleteAddress() {
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

            setTimeout(() => {
              this.syncData(place.formatted_address, "address");
              this.syncData(
                place.geometry.location.lat(),
                "coordinates",
                "latitude"
              );
              this.syncData(
                place.geometry.location.lng(),
                "coordinates",
                "longitude"
              );
            }, 100);
          });
        }
      }, 100);
    },
  },
};
</script>
