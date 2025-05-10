import authHeader from "~/store/authHeader.js"

export default {
  GET_ALL_VEHICLES({ commit }, params) {
    if (params && params.search && (params.search == null || params.search.trim().length == 0)) {
      delete params.search
    }
    return new Promise((resolve, reject) => {
      this.$axios.get('/api/v1/vehicle/', { headers: { ...authHeader(), loader: true }, params: params })
        .then((result) => {
          commit("FETCH_ALL_VEHICLES", result.data)
          resolve(result.data.results)
        })
        .catch((err) => {
          reject(err.response.data)
        })
    })
  },
  ADD_VEHICLE({ commit }, payload) {
    return new Promise((resolve, reject) => {
      this.$axios.post('/api/v1/vehicle/', payload, { headers: { ...authHeader(), loader: true } })
        .then((result) => {
          commit("PUSH_TO_VEHICLE_LIST", result.data)
          resolve(result.data)
        })
        .catch((err) => {
          reject(err.response.data)
        })
    })
  },
  UPLOAD_DOCUMENT({ commit }, payload) {
    return new Promise((resolve, reject) => {
      this.$axios.post(`/api/v1/vehicle/${payload.id}/upload/`, payload.data, { headers: { ...authHeader(), loader: true } })
        .then((result) => {
          resolve(result.data)
        })
        .catch((err) => {
          reject(err.response.data)
        })
    })
  },
  DELETE_DOCUMENT({ commit }, id) {
    return new Promise((resolve, reject) => {
      this.$axios.delete(`/api/v1/vehicle-document/${id}/`, { headers: { ...authHeader(), loader: true } })
        .then((result) => {
          resolve(result.data)
        })
        .catch((err) => {
          reject(err.response.data)
        })
    })
  },
  GET_VEHICLE_DETAILS({ commit }, id) {
    return new Promise((resolve, reject) => {
      this.$axios.get(`/api/v1/vehicle/${id}/`, { headers: { ...authHeader(), loader: true } })
        .then((result) => {
          commit("SET_VEHICLE_FORM_DETAILS", result.data)
          resolve(result.data)
        })
        .catch((err) => {
          reject(err.response.data)
        })
    })
  },
  UPDATE_VEHICLE_DETAILS({ commit }, data) {
    return new Promise((resolve, reject) => {
      this.$axios.patch(`/api/v1/vehicle/${data.id}/`, data.data, { headers: authHeader() })
        .then((result) => {
          commit("UPDATE_TO_VEHICLE_LIST", result.data)
          resolve(result.data)
        })
        .catch((err) => {
          reject(err.response.data)
        })
    })
  },
  DOWNLOAD_ALL_VEHICLES({ commit }, params) {
    return new Promise((resolve, reject) => {
      this.$axios.get(`/api/v1/vehicle/download/`, {
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
        commit('SET_TAGS', response.data);
        resolve(response.data)
      }).catch((error) => {
        reject(error)
      })
    })
  },
  Add_VEHICLE_TAG({ commit }, payload) {
    return new Promise((resolve, reject) => {
      this.$axios.post(`/api/v1/tags/`, payload, {
        headers: { ...authHeader(), loader: true }
      }).then((response) => {
        commit('SET_TAG_INTO_LIST', response.data);
        resolve(response.data)
      }).catch((error) => {
      reject(error.response.data)
      })
    })
  },
  DELETE_TAG({ commit }, id) {
    return new Promise((resolve, reject) => {
      this.$axios.delete(`/api/v1/tags/${id}/`, {
        headers: { ...authHeader(), loader: true }
      }).then((response) => {
        commit('REMOVE_TAG_INTO_LIST', id);
        resolve(response.data)
      }).catch((error) => {
        reject(error.response.data)
      })
    })
  }
}