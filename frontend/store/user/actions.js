import authHeader from "../authHeader"

export default {
    GET_ALL_USERS({ commit }) {
        return new Promise((resolve, reject) => {
            this.$axios.get('/api/v1/user/', { headers: { ...authHeader(), loader: true } })
                .then((response) => {
                    // context.commit('order/orderListStore/SET_ORDER_LIST',result.data,{root : true})
                    commit('SET_ALL_USERS', response.data.results)
                    resolve(response.data)
                })
                .catch((error) => {

                    reject(error.response.data)
                })
        })
    },

    GET_USER_DETAILS({ commit }, id) {
        return new Promise((resolve, reject) => {
            this.$axios.get(`/api/v1/user/${id}/`, { headers: { ...authHeader(), loader: true } })
                .then((response) => {
                    commit('SET_USER_DETAILS', response.data)
                    resolve(response.data)
                })
                .catch((error) => {

                    reject(error.response.data)
                })
        })
    },
    ADD_USER({ commit }, payload) {
        return new Promise((resolve, reject) => {
            this.$axios.post('/api/v1/user/', payload, { headers: { ...authHeader(), loader: true } })
                .then((response) => {
                    commit('ADD_USER_DETAILS_IN_LIST', response.data)
                    resolve(response.data)
                })
                .catch((error) => {

                    reject(error.response.data)
                })
        })
    },
    UPDATE_USER_DETAILS({ commit }, data) {
        return new Promise((resolve, reject) => {
            this.$axios.patch(`/api/v1/user/${data.id}/`, data, { headers: { ...authHeader(), loader: true } })
                .then((response) => {
                    commit("UPDATE_USER_DETAILS_IN_LIST", response.data)
                    resolve(response.data)
                })
                .catch((error) => {
                    reject(error.response.data)
                })
        })
    },
    DELETE_USER({ commit }, id) {
        return new Promise((resolve, reject) => {
            this.$axios.delete(`/api/v1/user/${id}/`, { headers: { ...authHeader(), loader: true } })
                .then((response) => {
                    commit("DELETE_USER_DETAILS", id)
                    resolve(response.data)
                })
                .catch((error) => {
                    reject(error.response.data)
                })
        })
    }
}