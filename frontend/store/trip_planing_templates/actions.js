import authHeader from "../authHeader"

export default {
  GET_ALL_PLANNING_TEMPLATES({ commit }, params) {
    return new Promise((resolve, reject) => {
      this.$axios.get('/api/v1/planning_template/', { headers: authHeader(), params: params })
        .then((result) => {
          commit("SET_TRIP_PLANNING_TEMPLATES_LIST", result.data)
          resolve(result.data)
        })
        .catch((err) => {
          reject(err)
        })
    })
  },

  GET_ALL_TEMPLATE_LIST({ commit }) {
    let params = {}
    params.limit = "all"
    this.$axios.get("/api/v1/planning_template/", {
      headers: { ...authHeader(), loader: true },
      params: params
    })
      .then((res) => {
          console.log(res.data)
        commit('SET_ALL_TEMPLATE_LIST', res.data)
      })
      .catch(err => {
      })
  },

  ADD_PLANNING_TEMPLATES({ commit }, params) {
    return new Promise((resolve, reject) => {
      this.$axios.post('/api/v1/planning_template/', params, { headers: authHeader() })
        .then((result) => {
          resolve(result.data)
        })
        .catch((err) => {
          reject(err.response.data)
        })
    })
  },
  GET_PLANNING_TEMPLATE_DETAILS({ commit }, id) {
    return new Promise((resolve, reject) => {
      this.$axios.get(`/api/v1/planning_template/${id}/`, { headers: { ...authHeader(), loader: true } })
        .then((result) => {
          commit("SET_TEMPLATE_FORM_DATA", result.data)
          resolve(result.data)
        })
        .catch((err) => {
          reject(err.response)
        })
    })
  },
  EDIT_PLANNING_TEMPLATES({ commit }, params) {
    return new Promise((resolve, reject) => {
      this.$axios.put(`/api/v1/planning_template/${params.id}/`, params, { headers: authHeader() })
        .then((result) => {
          resolve(result.data)
        })
        .catch((err) => {
          reject(err)
        })
    })
  },
}
