import authHeader from "../authHeader"

export default {
  GET_ALL_ROLE({ commit }) {
    return new Promise((resolve, reject) => {
      this.$axios.get('/api/v1/role/', { headers: { ...authHeader(), loader: true } })
        .then((response) => {
          commit('SET_ALL_ROLES', response.data.results)
          resolve(response.data)
        })
        .catch((error) => {

          reject(error.data)
        })
    })
  },
  GET_ROLE_DETAILS({ commit }, id) {
    return new Promise((resolve, reject) => {
      this.$axios.get(`/api/v1/role/${id}/`, { headers: { ...authHeader(), loader: true } })
        .then((response) => {
          commit('SET_ROLE_DETAILS', response.data)
          resolve(response.data)
        })
        .catch((error) => {

          reject(error.response)
        })
    })
  },
  ADD_ROLE({ commit }, data) {
    return new Promise((resolve, reject) => {
      this.$axios.post('/api/v1/role/', data, { headers: { ...authHeader(), loader: true } })
        .then((response) => {
          commit('ADD_ROLE_DETAILS_IN_LIST', response.data);
          resolve(response.data);
        })
        .catch((error) => {

          reject(error.response.data)
        })
    })
  },
  DELETE_ROLE({ commit }, id) {
    return new Promise((resolve, reject) => {
      this.$axios.delete(`/api/v1/role/${id}/`, { headers: authHeader() })
        .then((response) => {
          commit('DELETE_USER_DETAILS', id)
          resolve(response.data)
        })
        .catch((error) => {

          reject(error.data);
        })
    })
  },
  UPDATE_ROLE_DETAILS({ commit }, data) {
    return new Promise((resolve, reject) => {
      this.$axios.patch(`api/v1/role/${data.id}/`, data, { headers: { ...authHeader(), loader: true } })
        .then((response) => {
          commit('UPDATE_ROLE_DETAILS_IN_LIST', response.data)
          resolve(response.data)
        })
        .catch((error) => {
        })
    })
  }
}