export default {
    SET_ORDER_DETAILS(state, payload) {
        state.order = payload
    },
    SET_ORDER_ITEM_DETAILS(state, payload) {
        state.orderItems = payload
    }
}