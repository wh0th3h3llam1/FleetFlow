export default {
  SET_CUSTOMER_ADDRESS_LIST(state, data) {
    state.customerAddress = data.results
    state.totalItems = data.count
  },
  SET_CUSTOMER_ADDRESS_DETAILS(state, data) {
    state.customerAddressDetails = data
  },
  SYNC_CUSTOMER_ADDRESS_DETAILS(state, data) {
    if (data.subKey) {
      state.customerAddressDetails[data.key][data.subKey] = data.value
    } else {
      state.customerAddressDetails[data.key] = data.value
    }
  },
  SET_TIME_SLOT(state, data) {
    if (data.length != 0) {
      state.time_slots = data
    }
    else {
      state.time_slots = [
        {
          from_time: null,
          to_time: null
        }
      ]
    }
  },
  SYNC_TIME_SLOT(state, data) {
    state.time_slots[data.index][data.key] = data.value
  },
  ADD_TIME_SLOT(state) {
    state.time_slots.push({})
  },
  REMOVE_TIME_SLOT(state, index) {
    if (state.time_slots.length > 1) {
      state.time_slots.splice(index, 1)
    }
  },
  SET_TAGS(state, data) {
    let driverTag = data.filter(item => item.tag_type == "driver_tag");
    state.drivertaglist = driverTag.map(item => {
      return { title: item.tag, value: item.id }
    });
    let vehicleTag = data.filter(item => item.tag_type == "vehicle_tag");
    state.vehicletaglist = vehicleTag.map((item, i) => {
      return { title: item.tag, value: item.id }
    });
  },
  SET_EDIT_MODE(state, data) {
    state.editMode = data
  },
  PUSH_CUSTOMER_ADDRESS_DETAILS(state, resp) {
    if (resp.isBulkupload) {
      state.customerAddress = [...state.customerAddress, ...resp.data]
    } else {
      state.customerAddress.unshift(resp.data)
    }
  },
  UPDATE_CUSTOMER_ADDRESS_DETAILS(state, data) {
    let index = state.customerAddress.indexOf(state.customerAddress.find(address => address.id === data.id))
    state.customerAddress.splice(index, 1, data)
  },
}