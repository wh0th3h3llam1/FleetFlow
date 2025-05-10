import authHeader from "~/store/authHeader"

export default {
    GET_ORDER_DETAILS({ commit }, id) {
        return new Promise((resolve, reject) => {
            this.$axios.get(`/api/v1/order/${id}/`, { headers: { ...authHeader(), loader: true } })
                .then((result) => {
                    commit("SET_ORDER_DETAILS", result.data)
                    resolve(result.data)
                })
                .catch((error) => {
                    reject(error.response.data)
                })
        })
    },
    GET_ORDER_ITEMS({ commit }, id) {
        return new Promise((resolve, reject) => {
            this.$axios.get(`/api/v1/order-item/?order__id=${id}`, { headers: { ...authHeader(), loader: true } })
                .then((result) => {
                    commit("SET_ORDER_ITEM_DETAILS", result.data)
                    resolve(result.data)
                })
                .catch((error) => {
                    reject(error.response.data)
                })
        })
    },
    SHARE_DATA_TO_DRIVER({ commit }, id) {
        return new Promise((resolve, reject) => {
            this.$axios.post(`/api/v1/order/${id}/send_order_notification/`, id, { headers: authHeader() })
                .then((result) => {
                    resolve(result.data)
                })
                .catch((error) => {
                    reject(error.response.data)
                })
        })
    }
}