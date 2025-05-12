export default {
  SET_DRIVERS_LIST(state, payload) {
    state.drivers_list = payload
  },
  SET_OPERATIONS_LIST(state, payload) {
    state.orders = payload.orders
  },
  SET_SELECTED_DRIVERS_TRIP_DATA(state, payload) {
    delete payload.orders
    delete payload.trip_route
    state.selectedDriversTripDetails = payload
  },
  SET_DRIVER_CHAT_DATA(state, payload) {
    state.chatList = payload.reverse()
  },
  SET_CHAT_DETAILS_IN_LIST(state, payload) {
    state.chatList.push(payload)
  },
  SET_MAP_DATA(state, payload) {
    state.mapData = payload
  }
}