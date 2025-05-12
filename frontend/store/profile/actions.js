import authHeader from "../authHeader"

export default {
  async GET_USER_PROFILE_INFO({ commit }) {
    return new Promise((resolve, reject) => {
      this.$axios.get(`/api/v1/profile/`, { headers: { ...authHeader(), loader: true } })
        .then((result) => {
          commit("SET_USER_DETAILS", result.data.data)
          resolve(result.data)
        })
        .catch((err) => {
          reject(err.response)
        })
    })
  },
  UPDATE_USER_DETAILS({ commit }, payload) {
    return new Promise((resolve, reject) => {
      this.$axios.post(`/api/v1/profile/`, payload, { headers: { ...authHeader(), loader: true } })
        .then((result) => {
          commit("SET_USER_DETAILS", result.data.data)
          resolve(result.data)
        })
        .catch((err) => {
          reject(err.response.data)
        })
    })
  },
  UPDATE_USER_PASSWORD({ commit }, payload) {
    return new Promise((resolve, reject) => {
      this.$axios.put(`/change_password/`, payload, { headers: { ...authHeader(), loader: true } })
        .then((result) => {
          // commit("SET_USER_DETAILS", result.data.data)
          resolve(result.data)
        })
        .catch((err) => {
          reject(err.response.data)
        })
    })
  }
}