export default {
    SET_ALL_ROLES(state, payload) {
        state.rolelist = payload
    },
    DELETE_USER_DETAILS(state, id) {
        state.rolelist.splice(state.rolelist.indexOf(state.rolelist.find(v => v.id == id)), 1)
    },
    ADD_ROLE_DETAILS_IN_LIST(state, payload) {
        state.rolelist.unshift(payload)
    },
    SET_ROLE_DETAILS(state, payload) {
        state.roledetail = payload
    },
    SYNC_ROLE_FORM_DETAILS(state, payload) {
        state.roledetail[payload.key] = payload.value
    },
    UPDATE_ROLE_DETAILS_IN_LIST(state, data) {
        state.rolelist.splice(state.rolelist.indexOf(state.rolelist.find(v => v.id == data.id)), 1, data)
    }

}