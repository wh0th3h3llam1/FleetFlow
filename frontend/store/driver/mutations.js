export default {
    SET_ALL_DRIVERS(state, data) {
        state.drivers = data.results
        state.totalItems = data.count
    },
    PUSH_DRIVER_TO_LIST(state, data) {
        state.drivers.push(data)
    },
    SET_TAGS(state, data) {
        state.taglist = data.filter(item => item.tag_type == 'driver_tag' );
    },
    SET_TAG_INTO_LIST(state, data) {
        state.taglist.push(data);
    },
    REMOVE_TAG_INTO_LIST(state,id){
        state.taglist.splice(state.taglist.indexOf(state.taglist.find((v) => v.id == id)), 1);
    },
    FIND_AND_PUSH_UPDATED_DRIVER_INTO_THE_LIST(state, payload) {
        state.drivers.splice(state.drivers.indexOf(state.drivers.find((v) => v.id == payload.id)), 1, payload)
    },
    SET_VEHICLE_LIST(state, data) {
        state.allVehicles = data
    },
    SET_ZONE_LIST(state, data) {
        state.allZones = data
    },
    SET_DRIVER_FORM_DETAILS(state, data) {
        state.driverForm = data
    },
    REMOVE_DRIVER_DOCUMENT(state,index){
        state.driverForm.driver_documents.splice(index, 1);
    },
    SYNC_DRIVER_FORM_DETAILS(state, data) {
        if (data.subKey) {
            state.driverForm[data.key][data.subKey] = data.value
        } else {
            state.driverForm[data.key] = data.value
        }
    },
    APPEND_ALL_DRIVERS(state, data) {
        state.drivers = [...state.drivers, ...data.results]
        state.driverTotalCount = data.count
    },
    SYNC_DRIVER_FILTER_DATA(state, data) {
        if (data.value != "" && data.value) {
            state.driverFilters[data.key] = data.value
        }
        else {
            if (state.driverFilters[data.key]) {
                delete state.driverFilters[data.key]
            }
        }
    }
}