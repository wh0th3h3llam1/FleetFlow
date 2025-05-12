import authHeader from '~/store/authHeader'

export default {
  GET_PROJECT_LIST({ commit }, params) {
    if (params && params.search && (params.search == null || params.search.trim().length == 0)) {
      delete params.search
    }
    this.$axios.get("api/v1/project/", {
      headers: { ...authHeader(), loader: true },
      params: params
    })
      .then((res) => {
        commit('SET_PROJECT_LIST', res.data)
      })
      .catch(err => {
      })
  },
  GET_ALL_PROJECT_LIST({ commit }) {
    let params = {}
    params.limit = "all"
    this.$axios.get("api/v1/project/", {
      headers: { ...authHeader(), loader: true },
      params: params
    })
      .then((res) => {
        commit('SET_ALL_PROJECT_LIST', res.data)
      })
      .catch(err => {
      })
  },
  ADD_PROJECT({ commit }, payload) {
    return new Promise((resolve, reject) => {
      this.$axios.post(`/api/v1/project/`, payload, { headers: { ...authHeader(), loader: true } })
        .then((result) => {

          commit("ADD_PROJECT_DETAILS_IN_LIST", result.data)
          resolve(result.data)
        })
        .catch((error) => {

          reject(error.response.data)
        })
    })
  },
  GET_PROJECT_DETAILS({ commit }, id) {
    return new Promise((resolve, reject) => {
      this.$axios.get(`/api/v1/project/${id}/`, { headers: { ...authHeader(), loader: true } })
        .then((result) => {
          commit("SET_PROJECT_DETAILS", result.data)
          resolve(result.data)
        })
        .catch((error) => {
          reject(error.response.data)
        })
    })
  },
  UPDATE_PROJECT_DETAILS({ commit }, data) {
    return new Promise((resolve, reject) => {
      this.$axios.put(`/api/v1/project/${data.id}/`, data, { headers: { ...authHeader(), loader: true } })
        .then((result) => {

          commit("UPDATE_PROJECT_DETAILS_IN_LIST", result.data)
          resolve(result.data)
        })
        .catch((error) => {

          reject(error.response.data)
        })
    })
  },
  VIEW_PROJECTS_ZONES({ commit }, params) {
    return new Promise((resolve, reject) => {
      this.$axios.get(`/api/v1/customer_address/get_zone_wise_address/`, { headers: { ...authHeader(), loader: true }, params: params })
        .then((result) => {
          resolve(result.data)
        })
        .catch((error) => {
          reject(error.response.data)
        })
    })
  }
}