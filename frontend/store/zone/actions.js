import authHeader from "../authHeader"

export default {
  GET_ALL_ZONES({ commit }, params) {
    return new Promise((resolve, reject) => {
      this.$axios.get('/api/v1/zones/', { headers: { ...authHeader(), loader: true }, params: params })
        .then((response) => {
          commit('SET_ALL_ZONE', response.data)
          resolve(response.data)
        })
        .catch((error) => {

          reject(error.response.data)
        })
    })
  },
  GET_ZONE_DETAILS({ commit }, id) {
    return new Promise((resolve, reject) => {
      this.$axios.get(`/api/v1/zones/${id}/`, { headers: { ...authHeader(), loader: true } })
        .then((response) => {
          commit('SET_ZONE_DETAILS', response.data);
          resolve(response.data)
        })
        .catch((error) => {

          reject(error.response.data)
        })
    })
  },
  ADD_ZONE({ commit }, payload) {
    return new Promise((resolve, reject) => {
      this.$axios.post('/api/v1/zones/', payload, { headers: { ...authHeader(), loader: true } })
        .then((response) => {
          commit('ADD_ZONE_DETAILS_IN_LIST', response.data)
          resolve(response.data);
        })
        .catch((error) => {
          reject(error.response.data);
        })
    })
  },
  DELETE_ZONE({ commit }, id) {
    return new Promise((resolve, reject) => {
      this.$axios.delete(`/api/v1/zones/${id}/`, { headers: authHeader() })
        .then((response) => {
          commit('DELETE_ZONE_DETAILS', id)
          resolve(response.data)
        })
        .catch((error) => {

          reject(error.response.data);
        })
    })
  },
  UPDATE_ZONE_DETAILS({ commit }, data) {
    return new Promise((resolve, reject) => {
      this.$axios.put(`/api/v1/zones/${data.id}/`, data, { headers: authHeader() })
        .then((response) => {
          commit('UPDATE_ZONE_DETAILS_IN_LIST', response.data)
          resolve(response.data)
        })
        .catch((error) => {

          reject(error.response.data);
        })
    })
  },
}