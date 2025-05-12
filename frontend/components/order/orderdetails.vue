<template>
  <div
    class="white pos-rel"
    style="height: 92vh; display: flex; flex-direction: column"
  >
    <v-card-title
      class="dark_solo_grey"
      :class="orderStatusDarkColor(order.status)"
    >
      <div style="width: 100%">
        <div class="d-flex justify-space-between" style="width: 100%">
          <h5
            class="
              text-caption text-lg-body-1
              font-weight-bold
              text-uppercase
              white--text
            "
          >
            <v-tooltip bottom>
              <template v-slot:activator="{ on, attrs }">
                <span v-bind="attrs" v-on="on">{{
                  order.reference_number
                }}</span>
              </template>
              <span>Reference number </span>
            </v-tooltip>
          </h5>
          <h5
            class="
              text-caption text-lg-body-1
              font-weight-bold
              text-uppercase
              white--text
            "
          >
            <v-tooltip bottom>
              <template v-slot:activator="{ on, attrs }">
                <span
                  class="text-capitalize"
                  v-bind="attrs"
                  v-on="on"
                  v-if="order.status == 'pickedup'"
                >
                  shipped
                </span>
                <span
                  class="text-capitalize"
                  v-bind="attrs"
                  v-on="on"
                  v-else-if="order.status == 'successful'"
                >
                  delivered
                </span>
                <span
                  class="text-capitalize"
                  v-bind="attrs"
                  v-on="on"
                  v-else-if="order.status == 'failed'"
                >
                  returned
                </span>
                <span v-else class="text-capitalize" v-bind="attrs" v-on="on">
                  {{ order.status.replace(/\_/g, " ") }}
                </span>
              </template>
              <span>Order Status</span>
            </v-tooltip>
          </h5>
        </div>
        <div
          class="d-lg-flex justify-space-between text-left text-lg-center"
          style="width: 100%"
        >
          <h5
            class="
              text-caption text-lg-body-2
              font-weight-normal
              text-uppercase
              white--text
              order-head-wrap
            "
          >
            <div>
              <v-tooltip bottom>
                <template v-slot:activator="{ on, attrs }">
                  <span small v-bind="attrs" v-on="on">
                    <span class="mx-1 hider">|</span>
                    {{ order.delivery_window_start }} to
                    {{ order.delivery_window_end }}
                  </span>
                </template>
                <span>Delivery Window Start Time</span>
              </v-tooltip>
            </div>
          </h5>

          <h5
            class="
              text-caption text-lg-body-2
              font-weight-normal
              text-uppercase
              white--text
              order-head-wrap
            "
          >
            <div>
              <v-tooltip bottom v-if="order.project">
                <template v-slot:activator="{ on, attrs }">
                  <span small v-if="order.project" v-bind="attrs" v-on="on">
                    {{ order.project_name }}
                  </span>
                </template>
                <span>Project Id</span>
              </v-tooltip>
            </div>
            <div>
              <v-tooltip bottom v-if="order.invoice_number">
                <template v-slot:activator="{ on, attrs }">
                  <span
                    class="ml-1"
                    small
                    v-if="order.invoice_number"
                    v-bind="attrs"
                    v-on="on"
                  >
                    <span class="mx-1 hider">|</span>
                    {{ order.invoice_number }}
                  </span>
                </template>
                <span>Invoice Number</span>
              </v-tooltip>
            </div>
          </h5>
        </div>
      </div>
      <div class="d-flex justify-center">
        <v-tooltip bottom v-if="closable">
          <template v-slot:activator="{ on, attrs }">
            <v-btn
              class="white"
              style="width: 30px !important"
              depressed
              tile
              :small="$vuetify.breakpoint.lgAndDown"
              v-bind="attrs"
              v-on="on"
              @click="closeOrderDetails()"
            >
              <v-icon
                class="primary--text"
                :small="$vuetify.breakpoint.lgAndDown"
                >mdi-close</v-icon
              >
            </v-btn>
          </template>
          <span>Close Details</span>
        </v-tooltip>
      </div>
    </v-card-title>
    <v-card-text
      ref="orderDetailsContainer"
      class="px-0 overflow-y-auto"
      @scroll="containerScroll"
      style="position: relative"
    >
      <div
        :class="orderStatusLightColor(order.status)"
        class="d-flex justify-space-between py-5 px-3"
        style="position: sticky; top: 0; z-index: 2"
      >
        <v-row no-gutters class="pa-0 ma-0">
          <v-col cols="12" lg="8" class="pa-0 ma-0">
            <div>
              <v-btn
                small
                :class="`${orderStatusDarkColor(order.status)}--text`"
                class="mr-2"
                @click="showOrderItems(order.id)"
              >
                <span>View Items</span>
              </v-btn>
              <v-btn
                small
                :class="`${orderStatusDarkColor(order.status)}--text`"
                class="mr-2"
                @click="showPODItems(order.id)"
              >
                <span>POD</span>
              </v-btn>
            </div>
          </v-col>
          <v-col
            cols="12"
            lg="4"
            class="pt-5 pa-lg-0 ma-0 d-lg-flex justify-end"
          >
            <div class="">
              <v-tooltip bottom v-if="!closable">
                <template v-slot:activator="{ on, attrs }">
                  <v-btn
                    depressed
                    :class="`${orderStatusDarkColor(order.status)}--text`"
                    class="mr-2 py-3"
                    x-small
                    v-bind="attrs"
                    v-show="
                      order.status == 'successful' ||
                      order.status == 'cancelled' ||
                      order.status == 'partially_delivered' ||
                      order.status == 'failed'
                    "
                    v-on="on"
                    @click="openViewRemarkDialog = true"
                  >
                    <v-icon small>mdi-information-outline</v-icon>
                  </v-btn>
                </template>
                <span>View Remarks</span>
              </v-tooltip>
              <v-tooltip bottom v-if="!closable">
                <template v-slot:activator="{ on, attrs }">
                  <v-btn
                    depressed
                    :class="`${orderStatusDarkColor(order.status)}--text`"
                    class="mr-2 py-3"
                    v-if="userPermissions.order && userPermissions.order.change"
                    v-show="order.status !== 'cancelled'"
                    x-small
                    v-bind="attrs"
                    v-on="on"
                    @click="get_order_details(order.id)"
                  >
                    <v-icon x-small>mdi-pencil</v-icon>
                  </v-btn>
                </template>
                <span>Edit Details</span>
              </v-tooltip>
              <!---------------------------------- share sheet with driver feature ---------------------------------->
              <v-tooltip bottom>
                <template v-slot:activator="{ on, attrs }">
                  <v-btn
                    v-show="order.status == 'unassigned'"
                    :class="`${orderStatusDarkColor(order.status)}--text`"
                    class="py-3"
                    depressed
                    v-bind="attrs"
                    x-small
                    v-on="on"
                    @click="shareLinkToDriver(order.id)"
                  >
                    <v-icon x-small> mdi-share-variant </v-icon>
                  </v-btn>
                </template>
                <span>Share</span>
              </v-tooltip>
            </div>
          </v-col>
        </v-row>
      </div>

      <!---------------------------- Customer details ---------------------------->
      <v-row no-gutters>
        <v-col cols="12">
          <v-row no-gutters class="px-4">
            <v-col cols="12" class="pt-6 d-flex justify-space-between">
              <h5
                class="
                  text-caption text-lg-body-1
                  font-weight-bold
                  text-uppercase
                  pr-3
                "
              >
                <v-tooltip bottom>
                  <template v-slot:activator="{ on, attrs }">
                    <span small v-bind="attrs" v-on="on" class="d-flex">
                      <v-icon
                        class="mr-5 mt-n1"
                        :color="orderStatusDarkColor(order.status)"
                      >
                        mdi-account
                      </v-icon>
                      {{ order.customer_name }}
                    </span>
                  </template>
                  <span>Customer Name</span>
                </v-tooltip>
              </h5>
              <h5
                class="
                  text-caption text-lg-body-1
                  font-weight-bold
                  text-uppercase
                "
              >
                <v-tooltip bottom>
                  <template v-slot:activator="{ on, attrs }">
                    <span small v-bind="attrs" v-on="on">
                      {{ order.contact_number }}
                    </span>
                  </template>
                  <span>Customer Contact Number</span>
                </v-tooltip>
              </h5>
            </v-col>
            <v-col
              cols="12"
              class="d-flex flex-column flex-lg-row justify-space-between"
            >
              <v-tooltip bottom>
                <template v-slot:activator="{ on, attrs }">
                  <span small v-bind="attrs" v-on="on" class="pl-12">
                    {{ order.contact_email }}
                  </span>
                </template>
                <span>Customer Contact Email</span>
              </v-tooltip>
              <v-tooltip bottom>
                <template v-slot:activator="{ on, attrs }">
                  <span
                    small
                    v-bind="attrs"
                    v-on="on"
                    v-show="order.planned_processing_time"
                  >
                    Planned Processing Time -
                    {{ order.planned_processing_time }}
                  </span>
                </template>
                <span>Planned_Processing Time</span>
              </v-tooltip>
            </v-col>
          </v-row>
        </v-col>
      </v-row>

      <!-------------------------- Driver Details -------------------------------->
      <hr
        class="light_grey my-3"
        style="opacity: 0.3"
        v-if="order.trip && order.trip.driver"
      />

      <v-row no-gutters class="py-3" v-if="order.trip && order.trip.driver">
        <v-col cols="12">
          <v-row no-gutters class="px-4">
            <v-col cols="12" class="d-flex justify-space-between">
              <h5
                class="
                  text-caption text-lg-body-1
                  font-weight-bold
                  text-uppercase
                "
              >
                <v-tooltip bottom>
                  <template v-slot:activator="{ on, attrs }">
                    <span small v-bind="attrs" v-on="on">
                      <v-icon
                        class="mr-5"
                        :color="orderStatusDarkColor(order.status)"
                      >
                        mdi-truck-fast
                      </v-icon>
                      {{ order.trip.driver.first_name }}
                    </span>
                  </template>
                  <span>Driver Name</span>
                </v-tooltip>
              </h5>
              <h5
                class="
                  text-caption text-lg-body-1
                  font-weight-bold
                  text-uppercase
                "
              >
                <v-tooltip bottom>
                  <template v-slot:activator="{ on, attrs }">
                    <span small v-bind="attrs" v-on="on">
                      {{ order.trip.driver.contact_number }}
                    </span>
                  </template>
                  <span>Driver Contact Number</span>
                </v-tooltip>
              </h5>
            </v-col>
            <v-col cols="12" class="d-flex justify-space-between">
              <v-tooltip bottom>
                <template v-slot:activator="{ on, attrs }">
                  <span small v-bind="attrs" v-on="on" class="pl-12">
                    {{ order.trip.vehicle.vehicle_plate_no }}
                  </span>
                </template>
                <span>Vehicle Assigned</span>
              </v-tooltip>
              <v-tooltip bottom>
                <template v-slot:activator="{ on, attrs }">
                  <span small v-bind="attrs" v-on="on">
                    {{ order.trip.driver.shift_start }} to
                    {{ order.trip.driver.shift_end }}
                  </span>
                </template>
                <span>Shift Timings</span>
              </v-tooltip>
            </v-col>
          </v-row>
        </v-col>
      </v-row>

      <!-------------------------- Order Timeline view -------------------------->
      <hr class="light_grey my-3" style="opacity: 0.3" />
      <v-row no-gutters class="px-5">
        <v-col cols="3" class="text-center">
          <span class="text-caption font-weight-bold">Created</span>
        </v-col>
        <v-col cols="3" class="text-center">
          <span class="text-caption font-weight-bold"> Assigned</span>
        </v-col>
        <v-col cols="3" class="text-center">
          <span class="text-caption font-weight-bold">Shipped</span>
        </v-col>
        <v-col cols="3" class="text-center">
          <span class="text-caption font-weight-bold">
            {{
              order.status == "partially_delivered"
                ? "Partially Delivered"
                : order.status == "successful"
                ? "Delivered"
                : order.status == "cancelled"
                ? "Cancelled"
                : order.status == "failed"
                ? "Returned"
                : "Unattempted"
            }}
          </span>
        </v-col>
        <v-col cols="12" class="pt-2">
          <v-row>
            <v-col cols="3" class="d-flex justify-center">
              <v-tooltip bottom>
                <template v-slot:activator="{ on, attrs }">
                  <span small v-bind="attrs" v-on="on">
                    <v-btn
                      x-small
                      :color="orderStatusDarkColor(order.status)"
                      fab
                      class="timeline-btn"
                      depressed
                      :ripple="false"
                    ></v-btn>
                  </span>
                </template>
                <span>{{ order.execution_date }}</span>
              </v-tooltip>
            </v-col>
            <v-col cols="3" class="d-flex justify-center">
              <v-tooltip bottom>
                <template v-slot:activator="{ on, attrs }">
                  <span small v-bind="attrs" v-on="on">
                    <v-btn
                      x-small
                      class="timeline-btn"
                      :color="
                        order.assigned_time
                          ? orderStatusDarkColor(order.status)
                          : 'grey lighten-1'
                      "
                      fab
                      depressed
                      :ripple="false"
                    ></v-btn>
                  </span>
                </template>
                <span v-if="order.assigned_time">{{
                  order.assigned_time
                }}</span>
                <span v-else>Order not Assigned</span>
              </v-tooltip>
            </v-col>
            <v-col cols="3" class="d-flex justify-center">
              <v-tooltip bottom>
                <template v-slot:activator="{ on, attrs }">
                  <span small v-bind="attrs" v-on="on">
                    <v-btn
                      x-small
                      fab
                      depressed
                      class="timeline-btn"
                      :ripple="false"
                      :color="
                        order.picked_up_time
                          ? orderStatusDarkColor(order.status)
                          : 'grey lighten-1'
                      "
                    ></v-btn>
                  </span>
                </template>
                <span v-if="order.picked_up_time">{{
                  order.picked_up_time
                }}</span>
                <span v-else>Order not shipped</span>
              </v-tooltip>
            </v-col>

            <v-col cols="3" class="d-flex justify-center">
              <v-tooltip bottom>
                <template v-slot:activator="{ on, attrs }">
                  <span small v-bind="attrs" v-on="on">
                    <v-btn
                      x-small
                      fab
                      class="timeline-btn"
                      :color="
                        order.cancelled_time ||
                        order.completed_time ||
                        order.failed_time
                          ? orderStatusDarkColor(order.status)
                          : 'grey lighten-1'
                      "
                    ></v-btn>
                  </span>
                </template>
                <span v-if="order.cancelled_time">{{
                  order.cancelled_time
                }}</span>
                <span v-else-if="order.completed_time">{{
                  order.completed_time
                }}</span>
                <span v-else-if="order.failed_time">{{
                  order.failed_time
                }}</span>
                <span v-else>Order not completed</span>
              </v-tooltip>
            </v-col>
          </v-row>
          <div style="width: 100%" class="d-flex justify-center">
            <div style="width: 82%">
              <v-progress-linear
                :color="orderStatusDarkColor(order.status)"
                class="timeline"
                :value="progressValue"
                :buffer-value="100"
              ></v-progress-linear>
            </div>
          </div>
        </v-col>
      </v-row>

      <v-row no-gutters class="px-4 mt-8">
        <v-col cols="6">
          <v-card outlined class="mr-2 pa-0" style="height: 100%">
            <v-card-title class="light_grey pa-1">
              <span class="cf-info-title font-weight-bold" style="opacity: 0.7">
                <v-icon class="mr-1" :color="orderStatusDarkColor(order.status)"
                  >mdi-truck-fast</v-icon
                >
                Source
              </span>
            </v-card-title>
            <v-card-text class="py-0">
              <span class="text-caption">
                {{ order.pickup_address }}
              </span>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="6">
          <v-card outlined class="ml-2 pa-0" style="height: 100%">
            <v-card-title class="light_grey pa-1">
              <span class="cf-info-title font-weight-bold" style="opacity: 0.7">
                <v-icon class="mr-1" :color="orderStatusDarkColor(order.status)"
                  >mdi-flag</v-icon
                >
                Destination
              </span>
            </v-card-title>
            <v-card-text class="py-0">
              <span class="text-caption">
                {{ order.drop_address }}
              </span>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- ------------------- Trip Details--------------------------------------- -->

      <v-card outlined class="mx-4 mt-3" v-if="order.trip">
        <v-card-title class="light_grey px-4 py-1">
          <span
            class="cf-info-title font-weight-bold text-uppercase"
            style="opacity: 0.7"
          >
            Trip Details
          </span>
        </v-card-title>
        <v-card-text>
          <v-row no-gutters class="px-4 pt-4">
            <v-col cols="6" class="py-1">
              <span class="cf-info-title font-weight-regular"
                >Trip reference number</span
              ></v-col
            >
            <v-col cols="6" class="d-flex justify-end py-1">
              <span class="cf-info-title font-weight-bold">
                {{ order.trip.reference_number }}
              </span>
            </v-col>
            <v-col cols="6" class="py-1">
              <span class="cf-info-title font-weight-regular">Trip Status</span>
            </v-col>
            <v-col cols="6" class="d-flex justify-end py-1">
              <span class="cf-info-title font-weight-bold">
                {{ order.trip.status }}
              </span>
            </v-col>
            <v-col cols="6" class="py-1" v-if="order.status == 'pickedup'">
              <span class="cf-info-title font-weight-regular">ETA Time</span>
            </v-col>
            <v-col
              cols="6"
              class="d-flex justify-end py-1"
              v-if="order.status == 'pickedup'"
            >
              <span class="cf-info-title font-weight-bold">
                {{ order.etc }}
              </span>
            </v-col>
            <v-col
              cols="6"
              class="py-1"
              v-if="order.status == 'pickedup' || order.status == 'failed'"
            >
              <span class="cf-info-title font-weight-regular"
                >Processing Time
              </span>
            </v-col>
            <v-col
              cols="6"
              class="d-flex justify-end py-1"
              v-if="order.status == 'pickedup' || order.status == 'failed'"
            >
              <span class="cf-info-title font-weight-bold">
                {{ order.processing_time }}
              </span>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>

      <v-card outlined class="mx-4 mt-3">
        <v-card-title class="light_grey px-4 py-1">
          <span
            class="cf-info-title font-weight-bold text-uppercase"
            style="opacity: 0.7"
          >
            Order Details
          </span>
        </v-card-title>
        <v-card-text>
          <v-row no-gutters class="px-4 pt-4">
            <v-col cols="6" v-if="order.no_of_items">
              <span class="cf-info-title font-weight-regular"
                >Total Quantity
              </span>
            </v-col>
            <v-col
              cols="6"
              class="d-flex justify-end py-1"
              v-if="order.no_of_items"
            >
              <span class="cf-info-title font-weight-bold">
                {{ order.no_of_items }}
              </span>
            </v-col>

            <v-col cols="6">
              <span class="cf-info-title font-weight-regular">
                POD required
              </span>
            </v-col>
            <v-col cols="6" class="d-flex justify-end py-1">
              <span
                class="cf-info-title font-weight-bold"
                v-if="order.pod_required"
              >
                Yes
              </span>
              <span class="cf-info-title font-weight-bold" v-else>No</span>
            </v-col>

            <v-col v-if="order.order_value" cols="6">
              <span class="cf-info-title font-weight-regular">
                Order Value
              </span>
            </v-col>
            <v-col
              v-if="order.order_value"
              cols="6"
              class="d-flex justify-end py-1"
            >
              <span class="cf-info-title font-weight-bold">
                {{ order.order_value }}
              </span>
            </v-col>

            <v-col v-if="order.partially_delivered" cols="6">
              <span class="cf-info-title font-weight-regular">
                Partially delivered
              </span>
            </v-col>
            <v-col
              v-if="order.partially_delivered"
              cols="6"
              class="d-flex justify-end py-1"
            >
              <span class="cf-info-title font-weight-bold">
                {{ order.partially_delivered }}
              </span>
            </v-col>

            <!-- <v-col v-if="order.actual_delivery_location" cols="6">
              <span class="cf-info-title font-weight-regular">
                Actual Delivery Location
              </span>
            </v-col> -->
            <!-- <v-col
              v-if="order.actual_delivery_location"
              cols="6"
              class="d-flex justify-end py-1"
            >
              <span class="cf-info-title font-weight-bold">
                {{ order.actual_delivery_location }}
              </span>
            </v-col> -->

            <v-col v-if="order.eta" cols="6">
              <span class="cf-info-title font-weight-regular"> ETA</span>
            </v-col>
            <v-col v-if="order.eta" cols="6" class="d-flex justify-end py-1">
              <span class="cf-info-title font-weight-bold">{{
                order.eta
              }}</span>
            </v-col>

            <v-col cols="6" v-if="order.total_kg">
              <span class="cf-info-title font-weight-regular"
                >Weight (in KG)</span
              >
            </v-col>
            <v-col
              cols="6"
              class="d-flex justify-end py-1"
              v-if="order.total_kg"
            >
              <span class="cf-info-title font-weight-bold">
                {{ order.total_kg }} Kg
              </span>
            </v-col>

            <v-col cols="6" v-if="order.total_cbm">
              <span class="cf-info-title font-weight-regular"
                >Volume (in CBM)</span
              >
            </v-col>
            <v-col
              cols="6"
              class="d-flex justify-end py-1"
              v-if="order.total_cbm"
            >
              <span class="cf-info-title font-weight-bold">
                {{ order.total_cbm }} cbm
              </span>
            </v-col>

            <v-col cols="6">
              <span class="cf-info-title font-weight-regular">
                Payment type
              </span>
            </v-col>
            <v-col cols="6" class="d-flex justify-end py-1">
              <span class="cf-info-title font-weight-bold">
                {{ order.payment_type }}</span
              >
            </v-col>

            <v-col
              v-if="order.payment_type == 'cod' || order.payment_collected"
              cols="6"
            >
              <span class="cf-info-title font-weight-regular">
                Payment Collected</span
              >
              <v-icon
                small
                color="primary"
                @click="showCODRemarks"
                class="ml-2"
              >
                mdi-information
              </v-icon>
            </v-col>
            <v-col
              cols="6"
              class="d-flex justify-end py-1"
              v-if="order.payment_type == 'cod' || order.payment_collected"
            >
              <span class="cf-info-title font-weight-bold">
                {{ order.payment_collected }}
              </span>
            </v-col>

            <v-col cols="6">
              <span class="cf-info-title font-weight-regular">
                Order Notification</span
              >
            </v-col>
            <v-col cols="6" class="d-flex justify-end py-1">
              <span
                class="cf-info-title font-weight-bold"
                v-if="order.customer_notifications"
                >Yes</span
              >
              <span class="cf-info-title font-weight-bold" v-else>No</span>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>

      <v-card outlined class="mx-4 mt-3" v-if="(order.status == 'partially_delivered' || order.status == 'failed') && order.status_keyword">
        <v-card-title class="light_grey px-4 py-1 d-flex justify-space-between">
          <span
            class="cf-info-title font-weight-bold text-uppercase"
            style="opacity: 0.7"
            >Status Details</span
          >
        </v-card-title>
        <v-card-text>
          <v-row no-gutters class="mt-3">
            <v-col cols="12">
              <v-row no-gutters class="px-4 pt-4">
                <v-col cols="6" v-if="(order.status == 'partially_delivered' || order.status == 'failed') && order.status_keyword">
                  <span class="cf-info-title font-weight-regular">Status </span>
                </v-col>
                <v-col
                  cols="6"
                  class="d-flex justify-end py-1"
                  v-if="order.status"
                >
                  <span class="cf-info-title font-weight-bold">
                    {{
                      order.status == "partially_delivered"
                        ? "Partially Delivered"
                        : order.status == "successful"
                        ? "Delivered"
                        : order.status == "cancelled"
                        ? "Cancelled"
                        : order.status == "failed"
                        ? "Returned"
                        : "Unattempted"
                    }}
                  </span>
                </v-col>
                <v-col cols="6" v-if="order.completed_time">
                  <span class="cf-info-title font-weight-regular"
                    >Delivered On
                  </span>
                </v-col>
                <v-col
                  cols="6"
                  class="d-flex justify-end py-1"
                  v-if="order.completed_time"
                >
                  <span class="cf-info-title font-weight-bold">
                    {{ order.completed_time }}
                  </span>
                </v-col>
                <v-col
                  cols="6"
                  v-if="order.status == 'failed' && order.failed_time"
                >
                  <span class="cf-info-title font-weight-regular"
                    >Returned On
                  </span>
                </v-col>
                <v-col
                  cols="6"
                  class="d-flex justify-end py-1"
                  v-if="order.status == 'failed' && order.failed_time"
                >
                  <span class="cf-info-title font-weight-bold">
                    {{ order.failed_time }}
                  </span>
                </v-col>
                <v-col cols="6" v-if="order.status_keyword">
                  <span class="cf-info-title font-weight-regular">Reason </span>
                </v-col>
                <v-col
                  cols="6"
                  class="d-flex justify-end py-1"
                  v-if="order.status_keyword"
                >
                  <span class="cf-info-title font-weight-bold">
                    {{ order.status_keyword }}
                  </span>
                </v-col>
              </v-row>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>

      <v-card outlined class="mx-4 mt-3" v-if="order.logs && order.logs.length">
        <v-card-title class="light_grey px-4 py-1 d-flex justify-space-between">
          <span
            class="cf-info-title font-weight-bold text-uppercase"
            style="opacity: 0.7"
            >logs</span
          >
          <v-btn
            small
            dark
            :class="orderStatusDarkColor(order.status)"
            elevation="0"
            @click="showLogs = !showLogs"
          >
            View Logs
          </v-btn>
        </v-card-title>
        <v-card-text>
          <v-row no-gutters class="mt-3">
            <v-col cols="12" v-if="showLogs">
              <v-timeline dense>
                <v-timeline-item
                  small
                  v-for="(log, index) in order.logs"
                  :key="index"
                  class="ma-0 pa-0"
                  :color="orderStatusDarkColor(order.status)"
                >
                  <v-card class="elevation-0 pa-lg-3" outlined>
                    <v-card-text class="pt-1">
                      <v-row>
                        <v-col class="ma-0 pb-0" cols="12" lg="6">
                          <span
                            :class="`${orderStatusDarkColor(
                              order.status
                            )}--text`"
                            class="font-weight-bold"
                          >
                            {{ log.added_by }}
                          </span>
                        </v-col>
                        <v-col
                          class="ma-0 pb-0 d-flex justify-end"
                          cols="12"
                          lg="6"
                        >
                          <span class="caption font-weight-bold">{{
                            log.created
                          }}</span>
                        </v-col>
                        <v-col
                          class="ma-0 pt-0 pb-0 text-caption text-body-2"
                          cols="12"
                        >
                          <span> {{ log.message }} </span>
                        </v-col>
                      </v-row>
                    </v-card-text>
                  </v-card>
                </v-timeline-item>
              </v-timeline>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
    </v-card-text>
    <v-btn
      v-if="showScrollTopButton"
      class="floating-btn-br elevation-2 background-white"
      icon
      @click="scrollToTop"
    >
      <v-icon> mdi-arrow-up </v-icon>
    </v-btn>
    <LazyOrderOrderform v-model="openOrderForm" formType="edit" />
    <LazyOrderOrderitem v-model="showItemDetails" />
    <LazyOrderOrderpodlist v-model="showPodDetails" />
    <LazyOrderOrderremark
      v-model="openViewRemarkDialog"
      :orderDetails="order"
    />
    <LazyOrderOrdercodremark
      v-model="openViewCODRemarkDialog"
      :orderDetails="order"
    />
  </div>
</template>

<script>
import { makeInstance, encryptLocal } from "~/assets/js/encryptLocal";

export default {
  props: {
    closable: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      showLogs: true,
      containerHeight: null,
      openOrderForm: false,
      showItemDetails: false,
      showPodDetails: false,
      showScrollTopButton: false,
      openViewRemarkDialog: false,
      openViewCODRemarkDialog: false,
      userPermissions: encryptLocal.getItem("permissions"),
    };
  },
  computed: {
    order() {
      return this.$store.state.order.orderDetailStore.order;
    },
    progressValue() {
      if (
        this.order.completed_time ||
        this.order.cancelled_time ||
        this.order.failed_time
      ) {
        return 100;
      }

      if (this.order && this.order.picked_up_time) {
        return 66.66;
      }

      if (this.order && this.order.assigned_time) {
        return 33.33;
      }
      return 0;
    },
    // progressBufferValue() {
    //   if (
    //     this.order &&
    //     this.order.assigned_time &&
    //     !this.order.picked_up_time
    //   ) {
    //     return 50;
    //   } else if (
    //     this.order.assigned_time &&
    //     this.order.picked_up_time &&
    //     !(
    //       this.order.cancelled_time ||
    //       this.order.completed_time ||
    //       this.order.failed_time
    //     )
    //   ) {
    //     return 100;
    //   } else {
    //     return 0;
    //   }
    // },
  },
  methods: {
    showCODRemarks() {
      console.log("higgi");
      this.openViewCODRemarkDialog = true;
    },
    coloredOrderStatus(status) {
      switch (status) {
        case "unassigned":
          return "#90A4AE";
        case "assigned":
          return "#90CAF9";
        case "pickedup":
          return "#FFB300";
        case "partially_delivered":
          return "#CE93D8";
        case "successful":
          return "#66BB6A";
        case "failed":
          return "#E53935";
        case "cancelled":
          return "#880E4F";
      }
    },
    orderStatusDarkColor(status) {
      switch (status) {
        case "unassigned":
          return "unassigned";
        case "assigned":
          return "assigned";
        case "pickedup":
          return "pickedup";
        case "partially_delivered":
          return "partially_delivered";
        case "successful":
          return "successful";
        case "failed":
          return "failed";
        case "cancelled":
          return "cancelled";
      }
    },
    orderStatusLightColor(status) {
      switch (status) {
        case "unassigned":
          return "light_unassigned";
        case "assigned":
          return "light_assigned";
        case "pickedup":
          return "light_pickedup";
        case "partially_delivered":
          return "light_partially_delivered";
        case "successful":
          return "light_successful";
        case "failed":
          return "light_failed";
        case "cancelled":
          return "light_cancelled";
      }
    },
    shareLinkToDriver(id) {
      this.$store
        .dispatch("order/orderDetailStore/SHARE_DATA_TO_DRIVER", id)
        .then((result) => {
          this.$notifier.showMessage({
            content: result.message,
            color: "success",
          });
        })
        .catch((err) => {
          this.$notifier.showMessage({
            content: err.message,
            color: "error",
          });
        });
    },
    closeOrderDetails() {
      this.$emit("closeOrderDetails", false);
    },
    get_order_details(id) {
      if (id) {
        this.$store
          .dispatch("order/orderFormStore/GET_ORDER_DETAILS_FOR_FORM", id)
          .then((result) => {
            this.openOrderForm = true;
          })
          .catch((err) => {
            this.$notifier.showMessage({
              content: "Couldn't fetch Data",
              color: "error",
            });
          });
      }
    },
    containerScroll() {
      if (
        this.$refs.orderDetailsContainer &&
        this.$refs.orderDetailsContainer.scrollTop > 0
      ) {
        this.showScrollTopButton = true;
      } else {
        this.showScrollTopButton = false;
      }
    },
    scrollToTop() {
      this.$refs.orderDetailsContainer.scrollTo({ top: 0, behavior: "smooth" });
    },
    showOrderItems(id) {
      this.$store
        .dispatch("order/orderDetailStore/GET_ORDER_ITEMS", id)
        .then((result) => {
          this.showItemDetails = true;
        })
        .catch((err) => {});
    },
    showPODItems() {
      this.showPodDetails = true;
    },
  },
  mounted() {
    if (process.browser) {
      if (this.$vuetify.breakpoint.xl) {
        this.containerHeight =
          ((window.innerHeight / 100) * 77.5).toFixed() + "px";
      } else if (this.$vuetify.breakpoint.lg) {
        this.containerHeight =
          ((window.innerHeight / 100) * 73.9).toFixed() + "px";
      }
    }
  },
  beforeCreate() {
    if (encryptLocal == null) {
      makeInstance(localStorage.getItem("user"));
    }
  },
};
</script>

<style>
.timeline {
  bottom: 11.5px;
}
.timeline-btn {
  height: 20px !important;
  width: 20px !important;
  z-index: 1 !important;
}

.order-head-wrap {
  display: flex;
}

@media screen and (max-width: 1600px) {
  .order-head-wrap {
    display: block;
  }
  .hider {
    display: none;
  }
}
</style>

