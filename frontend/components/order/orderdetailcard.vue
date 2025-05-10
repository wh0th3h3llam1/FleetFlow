<template>
  <div
    @click="$emit('selectOrder')"
    class="
      mb-4
      border-x-light_grey
      border-y-light_grey
      full-width
      background-white
      rounded-lg
    "
    :class="
      selectedOrder != null && selectedOrder.id == order.id
        ? 'selected-card'
        : null
    "
  >
    <div class="pa-2 background-light_grey rounded-t-lg">
      <v-row dense>
        <v-col cols="6">
          <v-tooltip right>
            <template v-slot:activator="{ on, attrs }">
              <span
                v-bind="attrs"
                v-on="on"
                class="text-subtitle-2 font-weight-bold"
              >
                <v-checkbox
                  class="ma-0 pa-0 float-left"
                  hide-details
                  color="primary"
                  :input-value="isSelectedOrder(order.id)"
                  @click.stop.prevent
                  @change="$emit('orderSelected', $event, order.id)"
                ></v-checkbox>
                {{ order.reference_number }}
              </span>
            </template>
            <span>Reference Number</span>
          </v-tooltip>
        </v-col>
        <v-col cols="6" class="d-flex justify-end">
          <div v-if="order.status">
            <span
              class="caption text-capitalize"
              v-if="order.status == 'pickedup'"
            >
              Shipped
            </span>
            <span
              class="caption text-capitalize"
              v-else-if="order.status == 'successful'"
            >
              delivered
            </span>
            <span
              class="caption text-capitalize"
              v-else-if="order.status == 'failed'"
            >
              returned
            </span>
            <span v-else class="caption text-capitalize">
              {{ order.status.replace(/\_/g, " ") }}
            </span>
            <v-avatar
              :class="`${order.status}`"
              size="16"
              class="ml-1"
            ></v-avatar>
          </div>
        </v-col>
      </v-row>
    </div>
    <div class="pa-2">
      <v-row no-gutters>
        <v-col cols="6" class="text-caption">
          <v-tooltip right>
            <template v-slot:activator="{ on, attrs }">
              <span v-on="on" v-bind="attrs">
                {{ order.customer_name }}
              </span>
            </template>
            <span>Customer Name</span>
          </v-tooltip>
        </v-col>
        <v-col cols="6" class="text-caption d-flex justify-end">
          <v-tooltip right>
            <template v-slot:activator="{ on, attrs }">
              <span v-on="on" v-bind="attrs">
                <b>{{ order.contact_number }}</b>
              </span>
            </template>
            <span>Customer Contact Number</span>
          </v-tooltip>
        </v-col>
      </v-row>
      <v-row no-gutters v-if="order && order.invoice_number">
        <v-col cols="6" class="text-caption"> Invoice Number </v-col>
        <v-col cols="6" class="text-caption d-flex justify-end">
          <b>{{ order.invoice_number }}</b>
        </v-col>
      </v-row>
      <v-row no-gutters>
        <v-col cols="6" class="text-caption d-flex align-center">
          <v-tooltip right>
            <template v-slot:activator="{ on, attrs }">
              <span v-on="on" v-bind="attrs" class="pr-1">
                <v-icon small>mdi-archive</v-icon>
                <span>{{ order.no_of_items }}</span>
              </span>
            </template>
            <span>Quantity</span>
          </v-tooltip>
          <v-tooltip right>
            <template v-slot:activator="{ on, attrs }">
              <span v-on="on" v-bind="attrs">
                <v-icon small>mdi-weight</v-icon>
                <span>{{ order.total_cbm }}</span>
              </span>
            </template>
            <span>Total CBM</span>
          </v-tooltip>
        </v-col>
        <v-col cols="6" class="d-flex justify-end text-caption">
          <v-tooltip right>
            <template v-slot:activator="{ on, attrs }">
              <span v-on="on" v-bind="attrs">
                <b>{{ order.execution_date }}</b>
              </span>
            </template>
            <span>Order Date</span>
          </v-tooltip>
          <span><b>&nbsp;|&nbsp;</b></span>
          <v-tooltip right>
            <template v-slot:activator="{ on, attrs }">
              <span v-on="on" v-bind="attrs" class="text-capitalize">
                <b>{{ order.order_type }}</b>
              </span>
            </template>
            <span>Order Type</span>
          </v-tooltip>
        </v-col>
      </v-row>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    order: {
      required: true,
    },
    selectedOrders: {
      required: true,
    },
  },
  computed: {
    selectedOrder() {
      return this.$store.state.order.orderDetailStore.order;
    },
  },
  methods: {
    isSelectedOrder(orderId) {
      return this.selectedOrders.indexOf(orderId) > -1;
    },
  },
};
</script>

<style>
</style>