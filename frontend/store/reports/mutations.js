export default {
    SET_REPORTS_DATA(state, data) {
        state.headers = data[0],
            state.reportData = data
    },
    SET_ALL_DRIVERS(state, data) {
        state.allDrivers = data
    },
    SET_ALL_VEHICLES(state, data) {
        state.allVehicles = data
    },
    EMPTY_REPORT_DATA(state) {
        state.headers = [],
            state.reportData = []
    },
    EMPTY_VEHICLE_DATA(state) {
        state.allVehicles = []
    },
    EMPTY_DRIVER_DATA(state) {
        state.allDrivers = []
    }
}