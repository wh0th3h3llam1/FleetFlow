export default {
    SET_ALL_STATUS(state, payload) {
        state.statusList = payload;
    },
    SET_STATUS_DETAILS(state, payload) {
        state.statusDetail = payload;
    },
    SET_STATUS_DETAIL_INTO_LIST(state, payload) {
        state.statusList.unshift(payload);
    },
    SYNC_STATUS_FORM_DETAILS(state, payload) {
        state.statusDetail[payload.key] = payload.value;
    },
    DELETE_USER_DETAILS(state, id) {
        state.statusList.splice(state.statusList.indexOf(state.statusList.find(v => v.id == id)), 1)
    },
    UPDATE_STATUS_DETAILS_IN_LIST(state, data) {
        state.statusList.splice(state.statusList.indexOf(state.statusList.find(v => v.id == data.id)), 1, data)
    }
}