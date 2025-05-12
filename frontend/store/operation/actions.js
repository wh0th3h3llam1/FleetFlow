import authHeader from "../authHeader"

export default {
  GET_DRIVERS_LIST_FOR_OPERATIONS({ commit }, params) {
    return new Promise((resolve, reject) => {
      if (params && params.search && (params.search == null || params.search.trim().length == 0)) {
        delete params.search
      }
      this.$axios.get('api/v1/operations/drivers/', { headers: { ...authHeader(), loader: false }, params: params })
        .then((res) => {
          commit('SET_DRIVERS_LIST', res.data)
          resolve(res.data)
        }).catch(err => {
          reject(err)
        })
    })
  },
  GET_OPERATIONS_LIST({ commit }, params) {
    let url = 'api/v1/operations/overview/'

    if (params && params.trip) {
      url = params.trip
      delete params.trip
    }

    return new Promise((resolve, reject) => {
      this.$axios.get(url, { headers: { ...authHeader(), loader: true }, params: params })
        .then((res) => {
          commit('SET_OPERATIONS_LIST', res.data)
          if (res.data.trip_route) {
            commit("SET_MAP_DATA", res.data.trip_route)
            commit("SET_SELECTED_DRIVERS_TRIP_DATA", res.data)
          } else {
            commit("SET_MAP_DATA", null)
            commit("SET_SELECTED_DRIVERS_TRIP_DATA", null)
          }

          resolve(res.data)
        }).catch(err => {
          if (err.response && err.response.status == 404) {
            commit('SET_OPERATIONS_LIST', { results: [], count: 0 })
          }
          reject(err.response)
        })
    })
  },
  GET_CHAT_DATA({ commit }, id) {
    return new Promise((resolve, reject) => {
      this.$axios.get(`/api/v1/chat/${id}/`, { headers: authHeader() })
        .then((response) => {
          commit('SET_DRIVER_CHAT_DATA', response.data.results)
          resolve(response.data.results)
        }).catch((error) => {
          reject(error.response.data)
        })
    })
  },
  SEND_MESSAGE({ commit }, payload) {
    return new Promise((resolve, reject) => {
      this.$axios.post(`/api/v1/chat/${payload.id}/`, payload.data, { headers: authHeader() })
        .then((response) => {
          commit('SET_CHAT_DETAILS_IN_LIST', response.data);
          resolve(response.data)
        })
        .catch((error) => {
          reject(error.response.data)
        })
    })

  }
}