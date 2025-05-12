export default {
  SET_SELECTED_PLAN_ID(state, planId) {
    state.planId = planId
  },
  SET_UNASSIGNED_ORDERS(state, orders) {
    state.unassignedOrderList = orders
  },
  SET_UNASSIGNED_DRIVERS(state, drivers) {
    state.unassignedDriverList = drivers
  },
  SET_PLAN_DETAILS(state, planDetails) {
    state.planDetails = planDetails
  },
  SET_PLANNED_TRIPS(state, tripList) {
    state.tripList = tripList
  },
  SET_SELECTED_ORDER_TO_MOVE(state, data) {
    const orderIndex = state.unassignedOrderList.indexOf(state.unassignedOrderList.find(v => v.id == data.orderId))
    state.tripIndexToMoveFrom = data.tripIndexToMoveFrom
    state.orderIndexToMove = orderIndex
  },
  PUSH_ORDER_TO_TRIP(state, data) {
    let order
    if (state.tripIndexToMoveFrom !== undefined) {
      order = state.tripList[state.tripIndexToMoveFrom].planned_orders.splice(state.orderIndexToMove, 1)[0]
    } else {
      order = state.unassignedOrderList.splice(state.orderIndexToMove, 1, {})[0]
      order.oldIndex = state.orderIndexToMove
    }

    if (data.orderIndexToMoveOn !== undefined) {
      state.tripList[data.tripIndexToMoveOn].planned_orders.splice(data.orderIndexToMoveOn, 0, order)
    } else {
      state.tripList[data.tripIndexToMoveOn].planned_orders.push(order)
    }

    state.tripIndexToMoveFrom = undefined
    state.orderIndexToMove = undefined
  },
  REMOVE_ORDER_FROM_TRIP(state, data) {
    let order = state.tripList[data.tripIndex]["planned_orders"].splice(data.currentOrderIndex, 1)[0]
    if (data.oldIndex !== undefined) {
      state.unassignedOrderList.splice(data.oldIndex, 1, order)
    } else {
      state.unassignedOrderList.push(order)
    }
  },
  REMOVE_TRIP(state, tripIndex) {
    state.tripList.splice(tripIndex, 1)
  },
  SET_TRIP_LOCATION_DATA(state, locationData) {
    state.drivingDirections = locationData.driving_directions
    state.tripOrdersList = locationData.order_details
    state.warehouseDetails = locationData.warehouse_details
  },
  SET_SELECTED_TRIP(state, selectedTrip) {
    state.selectedTrip = selectedTrip;
  },
  SET_PLAN_INFORMATION(state, data) {
    state.planinfo = data;
  },
  SET_SELECTED_INTERNAL_ORDER_TO_MOVE(state, data) {
    state.tripIndexToMoveFrom = data.tripIndexToMoveFrom
    state.orderIndexToMove = data.orderIndex
  },
  TOGGLE_SUBMIT_BUTTON(state, value) {
    state.planDetails.action_taken = value;
  }
}