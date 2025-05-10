export default {
    SET_ALL_ZONE(state, payload) {
        state.zonelist = payload.results
        state.totalCount = payload.count
    },
    DELETE_ZONE_DETAILS(state, id) {
        state.zonelist.splice(state.zonelist.indexOf(state.zonelist.find(v => v.id == id)), 1)
    },
    SET_ZONE_DETAILS(state, payload) {
        state.zonedetail = payload
    },
    ADD_ZONE_DETAILS_IN_LIST(state, data) {
        state.zonelist.unshift(data)
    },
    SYNC_ZONE_FORM_DETAILS(state, payload) {
        state.zonedetail[payload.key] = payload.value
    },
    UPDATE_ZONE_DETAILS_IN_LIST(state, data) {
        state.zonelist.splice(state.zonelist.indexOf(state.zonelist.find(v => v.id == data.id)), 1, data)
    },
    SET_GEOJSON_DATA(state, data) {
        state.geoJSON = data
    }
}
