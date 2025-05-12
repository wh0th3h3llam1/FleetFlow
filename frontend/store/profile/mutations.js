export default {
    SET_USER_DETAILS(state, data) {
        state.permissions = data.permissions
        state.userProfile = data
    },
    SYNC_USER_DETAILS(state, data) {
        if (data.value) {
            state.userProfile[data.key] = data.value
        }
    }
}