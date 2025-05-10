export default {
  SET_ORDER_LIST(state, payload) {
    state.Orders = payload.results
    state.totalOrdersCount = payload.count
  },
  APPEND_ORDER_LIST(state, payload) {
    state.Orders = [...state.Orders, ...payload.results]
    state.totalOrdersCount = payload.count
  },
  PUSH_ADDED_ORDER_TO_LIST(state, payload) {
    state.Orders.unshift(payload)
  },
  UPDATE_ORDER_IN_THE_LIST(state, data) {
    state.Orders.splice(state.Orders.indexOf(state.Orders.find((v) => v.id == data.id)), 1, data)
  },
  SET_ORDER_FILTER_DATA(state, data) {
    state.orderFilter = data
  },
  SYNC_ORDER_FILTER_DATA(state, data) {
    if (data.value != "" && data.value) {
      state.orderFilter[data.key] = data.value
    }
    else {
      if (state.orderFilter[data.key]) {
        delete state.orderFilter[data.key]
      }
    }
  },
  PUSH_UPLOADED_LIST(state, data) {
    state.Orders = [...state.Orders, ...data]
  }
}