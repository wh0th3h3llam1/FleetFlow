<template>
  <v-row no-gutters>
    <v-col cols="12" :class="`background-${orderDetail.status} pa-4`">
      <v-row no-gutters class="text-h6 font-weight-bold text-white">
        <v-col cols="6">
          {{ orderDetail.reference_number }}
        </v-col>
        <v-col cols="6" class="text-right text-uppercase">
          <h5 class="text-body-1 font-weight-bold text-uppercase white--text">
            <v-tooltip bottom>
              <template v-slot:activator="{ on, attrs }">
                <span
                  class="text-capitalize"
                  v-bind="attrs"
                  v-on="on"
                  v-if="orderDetail.status == 'pickedup'"
                >
                  Shipped
                </span>
                <span
                  class="text-capitalize"
                  v-bind="attrs"
                  v-on="on"
                  v-else-if="orderDetail.status == 'successful'"
                >
                  delivered
                </span>
                <span
                  class="text-capitalize"
                  v-bind="attrs"
                  v-on="on"
                  v-else-if="orderDetail.status == 'failed'"
                >
                  returned
                </span>
                <span v-else class="text-capitalize" v-bind="attrs" v-on="on">
                  {{ orderDetail.status.replace(/\_/g, " ") }}
                </span>
              </template>
              <span>Order Status</span>
            </v-tooltip>
          </h5>
        </v-col>
      </v-row>
      <v-row no-gutters class="text-caption text-white">
        <v-col cols="6">
          <v-tooltip bottom>
            <template v-slot:activator="{ on, attrs }">
              <span
                v-if="
                  orderDetail.status !== 'failed' &&
                  orderDetail.status !== 'successful'
                "
                v-bind="attrs"
                v-on="on"
              >
                {{ orderDetail.execution_date }}
              </span>
            </template>
            <span>Expected Date</span>
          </v-tooltip>
          <v-tooltip bottom>
            <template v-slot:activator="{ on, attrs }">
              <span
                v-if="
                  orderDetail.status !== 'failed' &&
                  orderDetail.status !== 'successful'
                "
                v-bind="attrs"
                v-on="on"
              >
                | {{ orderDetail.delivery_window_start }} to
                {{ orderDetail.delivery_window_end }}
              </span>
            </template>
            <span>Delivery window</span>
          </v-tooltip>
        </v-col>
        <v-col cols="6" class="text-right">
          {{ orderDetail.project }}
        </v-col>
      </v-row>
    </v-col>
    <v-col cols="12" class="overflow-y-auto order-details-container">
      <v-row no-gutters class="mx-4 mt-4 pb-4 border-bottom-light_grey">
        <v-col cols="1" class="d-flex justify-center align-center">
          <v-icon :class="`text-${orderDetail.status}`">mdi-account</v-icon>
        </v-col>
        <v-col cols="6">
          <v-tooltip bottom>
            <template v-slot:activator="{ on, attrs }">
              <span
                class="text-body-1 font-weight-bold"
                v-bind="attrs"
                v-on="on"
              >
                {{ orderDetail.customer_name }}
              </span>
            </template>
            <span>Customer name</span>
          </v-tooltip>
          <v-spacer></v-spacer>
          <v-tooltip bottom>
            <template v-slot:activator="{ on, attrs }">
              <span class="text-caption" v-bind="attrs" v-on="on">
                {{ orderDetail.contact_email }}
              </span>
            </template>
            <span>Customer contact email</span>
          </v-tooltip>
        </v-col>
        <v-col cols="5" class="text-right">
          <v-tooltip bottom>
            <template v-slot:activator="{ on, attrs }">
              <span
                class="text-body-1 font-weight-bold"
                v-bind="attrs"
                v-on="on"
              >
                {{ orderDetail.contact_number }}
              </span>
            </template>
            <span>Customer contact number</span>
          </v-tooltip>
        </v-col>
      </v-row>
      <v-row no-gutters class="mx-4 mt-4 pb-4 border-bottom-light_grey">
        <v-col cols="1" class="d-flex justify-center align-center">
          <v-icon :class="`text-${orderDetail.status}`">mdi-truck-fast</v-icon>
        </v-col>
        <v-col cols="6">
          <v-tooltip bottom>
            <template v-slot:activator="{ on, attrs }">
              <span
                class="text-body-1 font-weight-bold"
                v-bind="attrs"
                v-on="on"
              >
                {{ orderDetail.driver_name }}
              </span>
            </template>
            <span>Driver name</span>
          </v-tooltip>
          <v-spacer></v-spacer>
          <v-tooltip bottom>
            <template v-slot:activator="{ on, attrs }">
              <span class="text-caption" v-bind="attrs" v-on="on">
                {{ orderDetail.trip.vehicle.vehicle_plate_no }}
              </span>
            </template>
            <span>Vehicle Assigned</span>
          </v-tooltip>
        </v-col>
        <v-col cols="5" class="text-right">
          <v-tooltip bottom>
            <template v-slot:activator="{ on, attrs }">
              <span
                class="text-body-1 font-weight-bold"
                v-bind="attrs"
                v-on="on"
              >
                {{ orderDetail.contact_number }}
              </span>
            </template>
            <span>Customer contact number</span>
          </v-tooltip>
          <v-spacer></v-spacer>
          <v-tooltip bottom>
            <template v-slot:activator="{ on, attrs }">
              <span class="text-caption" v-bind="attrs" v-on="on">
                {{ orderDetail.trip.driver.shift_start }} to
                {{ orderDetail.trip.driver.shift_end }}
              </span>
            </template>
            <span>Shift timeing</span>
          </v-tooltip>
        </v-col>
      </v-row>
      <!-- <v-row></v-row> Timeline will be here -->
      <v-row no-gutters>
        <v-col cols="6">
          <v-row no-gutters class="pl-4 py-4 pr-2">
            <v-col
              cols="12"
              class="
                border-y-light_grey
                border-x-light_grey
                px-3
                py-2
                rounded-t
                background-light_grey
                d-flex
                align-center
              "
            >
              <v-icon :class="`text-${orderDetail.status} mr-2`">
                mdi-flag-outline
              </v-icon>
              <span class="text-body-2 font-weight-bold">Source</span>
            </v-col>
            <v-col
              cols="12"
              class="
                border-bottom-light_grey
                border-x-light_grey
                px-3
                py-2
                rounded-b
                text-caption
              "
            >
              {{ orderDetail.pickup_address }}
            </v-col>
          </v-row>
        </v-col>
        <v-col cols="6">
          <v-row no-gutters class="pl-2 py-4 pr-4">
            <v-col
              cols="12"
              class="
                border-y-light_grey
                border-x-light_grey
                px-3
                py-2
                rounded-t
                background-light_grey
                d-flex
                align-center
              "
            >
              <v-icon :class="`text-${orderDetail.status} mr-2`">
                mdi-flag
              </v-icon>
              <span class="text-body-2 font-weight-bold">Destination</span>
            </v-col>
            <v-col
              cols="12"
              class="
                border-bottom-light_grey
                border-x-light_grey
                px-3
                py-2
                rounded-b
                text-caption
              "
            >
              {{ orderDetail.drop_address }}
            </v-col>
          </v-row>
        </v-col>
      </v-row>
      <v-row no-gutters class="px-4 pb-4">
        <v-col
          cols="12"
          class="
            border-y-light_grey
            border-x-light_grey
            px-3
            py-2
            rounded-t
            background-light_grey
            d-flex
            align-center
          "
        >
          <span class="text-body-2 font-weight-bold">Trip Details</span>
        </v-col>
        <v-col
          cols="12"
          class="
            border-bottom-light_grey
            border-x-light_grey
            px-3
            py-2
            rounded-b
            text-caption
          "
        >
          <v-row no-gutters>
            <v-col cols="6"> Trip Reference Number </v-col>
            <v-col cols="6" class="text-right font-weight-bold">
              {{ orderDetail.trip.reference_number }}
            </v-col>
            <v-col cols="6"> Trip Status </v-col>
            <v-col cols="6" class="text-uppercase text-right font-weight-bold">
              {{ orderDetail.trip.status.replace(/\_/g, " ") }}
            </v-col>
          </v-row>
        </v-col>
      </v-row>
      <v-row no-gutters class="px-4 pb-4">
        <v-col
          cols="12"
          class="
            border-y-light_grey
            border-x-light_grey
            px-3
            py-2
            rounded-t
            background-light_grey
            d-flex
            align-center
          "
        >
          <span class="text-body-2 font-weight-bold">Order Details</span>
        </v-col>
        <v-col
          cols="12"
          class="
            border-bottom-light_grey
            border-x-light_grey
            px-3
            py-2
            rounded-b
            text-caption
          "
        >
          <v-row no-gutters>
            <v-col cols="6"> Total Quantity </v-col>
            <v-col cols="6" class="text-right font-weight-bold">
              {{ orderDetail.no_of_items }}
            </v-col>
            <v-col cols="6"> POD required </v-col>
            <v-col cols="6" class="text-right font-weight-bold">
              {{ orderDetail.pod_required ? "Yes" : "No" }}
            </v-col>
            <v-col cols="6" v-if="orderDetail.order_value"> Order Value </v-col>
            <v-col
              cols="6"
              v-if="orderDetail.order_value"
              class="text-right font-weight-bold"
            >
              {{ orderDetail.order_value }}
            </v-col>
            <v-col cols="6" v-if="orderDetail.payment_collected">
              Payment Collected
            </v-col>
            <v-col
              cols="6"
              v-if="orderDetail.payment_collected"
              class="text-right font-weight-bold"
            >
              {{ orderDetail.payment_collected }}
            </v-col>
            <v-col cols="6" v-if="orderDetail.partially_delivered">
              Partially delivered
            </v-col>
            <v-col
              cols="6"
              v-if="orderDetail.partially_delivered"
              class="text-right font-weight-bold"
            >
              {{ orderDetail.partially_delivered }}
            </v-col>
            <v-col cols="6" v-if="orderDetail.failed_order_reason">
              Failed Order Reason
            </v-col>
            <v-col
              cols="6"
              v-if="orderDetail.failed_order_reason"
              class="text-right font-weight-bold"
            >
              {{ orderDetail.failed_order_reason }}
            </v-col>
            <v-col cols="6" v-if="orderDetail.eta"> ETA </v-col>
            <v-col
              cols="6"
              v-if="orderDetail.eta"
              class="text-right font-weight-bold"
            >
              {{ orderDetail.eta }}
            </v-col>
            <v-col cols="6" v-if="orderDetail.total_kg"> Weight(kg) </v-col>
            <v-col
              cols="6"
              v-if="orderDetail.total_kg"
              class="text-right font-weight-bold"
            >
              {{ orderDetail.total_kg }} kg
            </v-col>
            <v-col cols="6" v-if="orderDetail.total_cbm"> Volume(CBM) </v-col>
            <v-col
              cols="6"
              v-if="orderDetail.total_cbm"
              class="text-right font-weight-bold"
            >
              {{ orderDetail.total_cbm }} CBM
            </v-col>
            <v-col cols="6" v-if="orderDetail.payment_type">
              Payment Type
            </v-col>
            <v-col
              cols="6"
              v-if="orderDetail.payment_type"
              class="text-uppercase text-right font-weight-bold"
            >
              {{ orderDetail.payment_type }}
            </v-col>
            <v-col cols="6"> Order Notification </v-col>
            <v-col cols="6" class="text-right font-weight-bold">
              {{ orderDetail.customer_notifications ? "Yes" : "No" }}
            </v-col>
          </v-row>
        </v-col>
      </v-row>
    </v-col>
  </v-row>
</template>

<script>
export default {
  props: {
    orderDetail: {
      required: true,
      type: Object,
    },
  },
};
</script>

<style>
.order-details-container{
  max-height: 600px;
}
</style>