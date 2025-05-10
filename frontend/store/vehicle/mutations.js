export default {
  FETCH_ALL_VEHICLES(state, payload) {
    state.vehiclList = payload.results
    state.totalItems = payload.count
  },
  SET_VEHICLE_FORM_DETAILS(state, data) {
    state.selectedVehicle = data
  },
  SYNC_VEHICLE_FORM_DETAILS(state, data) {
    if (data.subKey) {
      state.selectedVehicle[data.key][data.subKey] = data.value
    } else {
      state.selectedVehicle[data.key] = data.value
    }
  },
  REMOVE_VEHICLE_DOCUMENT(state, index) {
    state.selectedVehicle.vehicle_documents.splice(index, 1);
  },
  PUSH_TO_VEHICLE_LIST(state, data) {
    state.vehiclList.push(data)
  },
  UPDATE_TO_VEHICLE_LIST(state, data) {
    state.vehiclList.splice(state.vehiclList.indexOf(state.vehiclList.find(v => v.id == data.id)), 1, data)
  },
  SET_TAGS(state, data) {
    state.taglist = data.filter(item => item.tag_type == 'vehicle_tag' );
  },
  SET_TAG_INTO_LIST(state, data) {
    state.taglist.push(data);
  },
  REMOVE_TAG_INTO_LIST(state, id) {
    state.taglist.splice(state.taglist.indexOf(state.taglist.find((v) => v.id == id)), 1);
  },
}