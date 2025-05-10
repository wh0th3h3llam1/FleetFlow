export default {
  SET_UNASSIGNED_ORDERS_LIST(state, data) {
    state.unassignedOrderList = data
  },
  APPEND_UNASSIGNED_ORDERS_LIST(state, data) {
    state.unassignedOrderList = [...state.unassignedOrderList, ...data.results]
    state.totalOrdersCount = data.count
  },
  SET_UNASSIGNED_DRIVERS_LIST(state, data) {
    state.unassignedDriverList = data
  },
  PUSH_TO_UNASSIGNED_DRIVERS_LIST(state, data) {
    state.unassignedDriverList.push(data)
  },
  SET_SELECTED_ORDER_TO_MOVE(state, data) {
    const orderIndex = state.unassignedOrderList.indexOf(state.unassignedOrderList.find(v => v.id == data.orderId))
    state.tripIndexToMoveFrom = data.tripIndexToMoveFrom
    state.orderIndexToMove = orderIndex
  },
  SET_SELECTED_INTERNAL_ORDER_TO_MOVE(state, data) {
    state.tripIndexToMoveFrom = data.tripIndexToMoveFrom
    state.orderIndexToMove = data.orderIndex
  },
  CREATE_EMPTY_TRIP(state, trip) {
    state.tripList.push(trip)
    state.mapData.push({})
  },
  PUSH_TO_MAP_DATA(state, data) {
    state.mapData.splice(data.index, 1, data.data)
  },
  CLEAR_MAP_DATA(state, index) {
    if (state.mapData.length >= index) {
      state.mapData.splice(index, 1)
    }
  },
  UPDATE_ORDER_SEQUANCE(state, data) {
    data.data.forEach((order) => {
      let obj = state.tripList[data.tripIndex]["orders"].find((v) => {
        return v.id == order.id
      })
      state.tripList[data.tripIndex]["orders"].splice(state.tripList[data.tripIndex]["orders"].indexOf(obj), 1)
      state.tripList[data.tripIndex]["orders"].splice(order.sequence_number - 1, 0, { ...obj, ...order })
    })
  },
  PUSH_ORDER_TO_TRIP(state, data) {
    let order
    if (state.tripIndexToMoveFrom !== undefined) {
      order = state.tripList[state.tripIndexToMoveFrom].orders.splice(state.orderIndexToMove, 1)[0]
    } else {
      order = state.unassignedOrderList.splice(state.orderIndexToMove, 1, {})[0]
      order.oldIndex = state.orderIndexToMove
    }
    if (data.orderIndexToMoveOn != undefined) {
      state.tripList[data.tripIndexToMoveOn].orders.splice(data.orderIndexToMoveOn, 0, order)
    } else {
      state.tripList[data.tripIndexToMoveOn].orders.push(order)
    }

    state.tripIndexToMoveFrom = undefined
    state.orderIndexToMove = undefined
  },
  REMOVE_ORDER_FROM_TRIP(state, data) {
    let order = state.tripList[data.tripIndex]["orders"].splice(data.currentOrderIndex, 1)[0]
    if (data.oldIndex != undefined) {
      state.unassignedOrderList.splice(data.oldIndex, 1, order)
    } else {
      state.unassignedOrderList.unshift(order)
    }
  },
  REMOVE_TRIP(state, tripIndex) {
    state.tripList.splice(tripIndex, 1)
    state.mapData.splice(tripIndex, 1)
  },
  SET_TRIP_LIST(state, data) {
    data['mode'] ? (state.isEditMode = data.mode, state.tripList = data.data) : (state.tripList = data, state.isEditMode = false)
  },

  /** plan_trips mutations */
  SET_RECENTLY_PLANNED_TRIPS(state, data) {
    state.recentlyPlannedTrips = data.results
    state.totalItems = data.count
  },
  REMOVE_RECENTLY_PLANNED_TRIPS(state, id) {
    state.recentlyPlannedTrips.splice(state.recentlyPlannedTrips.indexOf(state.recentlyPlannedTrips.find(v => v.id == id)), 1)
  },
  // EDIT TRIP MUTATIONS
  UPDATE_EDIT_TRIP_DATA(state, data) {
    state.tripList[data.index][data.key] = data.value
  },
  EMPTY_ALL_FIELDS(state, data) {
    state.unassignedOrderList = [];
    state.unassignedDriverList = [];
    state.tripList = [];
    state.mapData = [];

    //Edit Trip variables 
    state.isEditMode = false;
  }
}