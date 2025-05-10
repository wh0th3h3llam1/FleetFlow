export default {
  SET_TRIP_DETAILS(state, data) {
    state.tripDetails = data;
    state.orderList = data.trip_orders;
  },
  SET_ORDER_LIST(state, data) {
    state.tripDetails = data;
  },
  SET_DRIVER_DETAILS(state, data) {
    state.driverDetails = data;
    state.tripid = data.trip;
  },
  SET_ORDER_DETAILS(state, data) {
    state.orderDetails = data;
  },
  syncData(state, data) {
    state.driverDetails[data.key] = data.value
  },
  SYNC_DELIVERY_DATA(state, data) {
    state.orderDetails
  },
  SET_PARTIALLY_REASON(state, data) {
    state.partiallyReason = data;
  },
  SET_FAILED_REASONS(state, data) {
    state.failedReasons = data;
  },
  SYNC_ORDER_ITEM(state, data) {
    state.orderDetails.order_items[data.index][data.key] = data.value
  },
  SET_TRIP_ROUTE(state, data) {
    state.tripRoute = data;
    state.orderlocation = data.trip_info;
  }
}