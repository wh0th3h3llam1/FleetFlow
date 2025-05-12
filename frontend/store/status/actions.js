import authHeader from "../authHeader"

export default {
  GET_ALL_STATUS({ commit }) {
    return new Promise((resolve, reject) => {
      this.$axios.get('/api/v1/statuses/', { headers: { ...authHeader(), loader: true } })
        .then((response) => {
          commit('SET_ALL_STATUS', response.data.result)
          resolve(response.data)
        })
        .catch((error) => {

          reject(error.response.data)
        })
    })
  },
  GET_STATUS_DETAIL({ commit }, id) {
    return new Promise((resolve, reject) => {
      this.$axios.get(`/api/v1/statuses/${id}/`, { headers: { ...authHeader(), loader: true } })
        .then((response) => {
          commit('SET_STATUS_DETAILS', response.data);
          resolve(response.data)
        })
        .catch((error) => {

          reject(error.response.data);
        })
    })
  },
  DELETE_STATUS({ commit }, id) {
    return new Promise((resolve, reject) => {
      this.$axios.delete(`/api/v1/statuses/${id}/`, { headers: { ...authHeader(), loader: true } })
        .then((response) => {
          commit('DELETE_USER_DETAILS', id);
          resolve(response.data)
        })
        .catch((error) => {

          reject(error.response.data);
        })
    })
  },
  UPDATE_STATUS_DETAILS({ commit }, data) {
    return new Promise((resolve, reject) => {
      this.$axios.patch(`/api/v1/statuses/${data.id}/`, data, { headers: { ...authHeader(), loader: true } })
        .then((response) => {
          commit('UPDATE_STATUS_DETAILS_IN_LIST', response.data)
          resolve(response.data)
        })
        .catch((error) => {

          reject(error.response.data)
        })
    })
  },
  ADD_STATUS({ commit }, payload) {
    return new Promise((resolve, reject) => {
      this.$axios.post('/api/v1/statuses/', payload, { headers: { ...authHeader(), loader: true } })
        .then((response) => {
          commit('SET_STATUS_DETAIL_INTO_LIST', response.data)
          resolve(response.data)
        })
        .catch((error) => {

          reject(error.response.data)
        })
    })
  }
}