export default {
    SET_ALL_USERS(state, payload) {
        state.userlist = payload
    },
    DELETE_USER_DETAILS(state, id) {
        state.userlist.splice(state.userlist.indexOf(state.userlist.find(v => v.id == id)), 1)
    },
    SET_USER_DETAILS(state, payload) {
        state.userdetail = payload
    },
    SYNC_USER_FORM_DETAILS(state, payload) {
        state.userdetail[payload.key] = payload.value
    },
    ADD_USER_DETAILS_IN_LIST(state, data) {
        state.userlist.unshift(data)
    },
    UPDATE_USER_DETAILS_IN_LIST(state, data) {
        state.userlist.splice(state.userlist.indexOf(state.userlist.find(v => v.id == data.id)), 1, data)
    }
}