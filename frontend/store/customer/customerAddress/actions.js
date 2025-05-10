import authHeader from '~/store/authHeader'

export default {
  GET_ALL_CUSTOMER_ADDRESS({ commit }, params) {
    if (params && params.search && (params.search == null || params.search.trim().length == 0)) {
      delete params.search
    }
    return new Promise((resolve, reject) => {
      this.$axios
        .get(`api/v1/customer_address/`, {
          headers: { ...authHeader(), loader: true }, params: params
        })
        .then((resp) => {
          commit('SET_CUSTOMER_ADDRESS_LIST', resp.data)
          resolve(resp.data)
        })
        .catch((err) => {
          reject(err.response.data)
        })
    })
  },
  GET_CUSTOMER_ADDRESS_DETAILS({ commit }, customerCode) {
    return new Promise((resolve, reject) => {
      this.$axios
        .get(`api/v1/customer_address/${customerCode}/`, {
          headers: { ...authHeader(), loader: true },
        })
        .then((resp) => {
          let data = resp.data
          commit('SET_TIME_SLOT', data.time_slots)
          delete data.time_slots
          commit('SET_CUSTOMER_ADDRESS_DETAILS', data)
          resolve(resp.data)
        })
        .catch((err) => {
          reject(err.response.data)
        })
    })
  },
  ADD_CUSTOMER_ADDRESS_DETAILS({ commit }, param) {
    return new Promise((resolve, reject) => {
      this.$axios
        .post(`api/v1/customer_address/`, param.data, {
          headers: { ...authHeader(), loader: true },
        })
        .then((resp) => {
          param.data = resp.data
          commit('PUSH_CUSTOMER_ADDRESS_DETAILS', param)
          resolve(resp.data)
        })
        .catch((err) => {
          reject(err.response.data)
        })
    })
  },
  UPDATE_CUSTOMER_ADDRESS_DETAILS({ commit }, param) {
    return new Promise((resolve, reject) => {
      this.$axios
        .put(`api/v1/customer_address/${param.id}/`, param, {
          headers: { ...authHeader(), loader: true },
        })
        .then((resp) => {
          commit('UPDATE_CUSTOMER_ADDRESS_DETAILS', resp.data)
          resolve(resp.data)
        })
        .catch((err) => {
          reject(err.response.data)
        })
    })
  },
  DOWNLOAD_ALL_CUSTOMERS({ commit }, params) {
    return new Promise((resolve, reject) => {
      this.$axios.get(`/api/v1/customer_address/download/`, {
        responseType: 'blob',
        headers: { ...authHeader(), loader: true }, params: params
      }).then((success) => {
        resolve(success.data)
      }).catch((error) => {
        reject(error.response.data)
      })
    })
  },
  GET_TAG_LIST({ commit }) {
    return new Promise((resolve, reject) => {
      this.$axios.get(`/api/v1/tags/`, {
        headers: { ...authHeader(), loader: true }
      }).then((response) => {
        commit('SET_TAGS',response.data);
        resolve(response.data)
      }).catch((error) => {
        reject(error)
      })
    })
  }
}