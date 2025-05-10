export default {
    SET_ALL_NOTIFICATIONS(state, data) {
        state.userNotifications = data.results
        state.totalCount = data.count
    },
    APPEND_NOTIFICATIONS(state, data) {
        state.userNotifications = [...state.userNotifications, ...data.results]
        state.totalCount = data.count
    },
    UPDATE_NOTIFICATIONS(state, id) {
        if (state.userNotifications.find((v) => v.id == id)) {
            state.userNotifications.splice(state.userNotifications.find((v) => v.id == id), 1)
        }
    },
    SET_WORKER_INSTANCE(state, data) {
        state.workerInstance = data
    }
}