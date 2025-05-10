import authHeader from "../authHeader"

export default {
  GET_REPORT_DATA({ commit }, params) {
    return new Promise((resolve, reject) => {
      this.$axios.get(params.url, { headers: { ...authHeader(), loader: true }, params: params.params })
        .then((result) => {
          let data = result.data.report_data;
          data.map((item, index) => {
            if (index == 0) {
              return item;
            }
          })
          commit("SET_REPORTS_DATA", data)
          resolve(result.data)
        })
        .catch((err) => {
          commit("EMPTY_REPORT_DATA")
          reject(err.response)
        })
    })
  },
  GET_ALL_DRIVERS({ commit }, params) {
    if (!params) {
      let params
    }
    params.limit = "all"
    return new Promise((resolve, reject) => {
      this.$axios.get('/api/v1/driver/', { headers: { ...authHeader(), loader: true }, params: params })
        .then((result) => {
          commit("SET_ALL_DRIVERS", result.data)
          resolve(result.data)
        })
        .catch((err) => {
          reject(err.response.data)
        })
    })
  },
  GET_ALL_VEHICLES({ commit }, params) {
    if (!params) {
      let params
    }
    params.limit = "all"
    return new Promise((resolve, reject) => {
      this.$axios.get('/api/v1/vehicle/', { headers: { ...authHeader(), loader: true }, params: params })
        .then((result) => {
          commit("SET_ALL_VEHICLES", result.data)
          resolve(result.data)
        })
        .catch((err) => {
          reject(err.response.data)
        })
    })
  }
}