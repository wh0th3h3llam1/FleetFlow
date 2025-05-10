export default {
    SET_ALL_TRIPS(state, data) {
        state.Trips = data.results
        state.tripTotalCount = data.count
    },
    APPEND_TRIPS_TO_LIST(state, data) {
        state.Trips = [...state.Trips, ...data]
    },
    SET_TRIP_DETAILS(state, data) {
        state.currentTrip = data
    },
    SYNC_TRIP_FILTER_DATA(state, data) {
        if (data.value != "" && data.value) {
            state.tripFilters[data.key] = data.value
        }
        else {
            if (state.tripFilters[data.key]) {
                delete state.tripFilters[data.key]
            }
        }
    },
    SET_TRIP_FILTER_DATA(state, data) {
        state.orderFilter = data
    },
    SET_TEMPRATURE_DATA(state, data) {
        state.chilledTempratureData = data.chilled;
        state.frozenTempratureData = data.frozen;
        state.dryTempratureData = data.dry;
    },
    SET_LOAD_SHEET_ITEM_LIST(state, payload) {
        state.loaditemlist = payload;
    },
    SET_TRIP_SHEET_ITEM_LIST(state, payload) {
        state.tripitemlist = payload;
    },
    SET_ACTUAL_DRIVER_ROUTE(state, payload) {
        state.actualroute = payload.driver_route.features[0].geometry.coordinates;
    }
}