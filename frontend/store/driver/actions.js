import authHeader from "~/store/authHeader.js"

export default {
  GET_ALL_DRIVERS(context, params) {
    if (params && params.search && (params.search == null || params.search.trim().length == 0)) {
      delete params.search
    }
    return new Promise((resolve, reject) => {
      this.$axios.get('/api/v1/driver/', { headers: { ...authHeader(), loader: true }, params: params })
        .then((result) => {
          context.commit("SET_ALL_DRIVERS", result.data)
          resolve(result.data.results)
        })
        .catch((error) => {
          reject(error.response.data)
        })
    })
  },
  ADD_DRIVER({ commit }, payload) {
    return new Promise((resolve, reject) => {
      this.$axios.post('/api/v1/driver/', payload.data, { headers: { ...authHeader(), loader: true } })
        .then((result) => {
          if (!payload.isBulkupload) {
            commit("PUSH_DRIVER_TO_LIST", result.data.data)
          }
          resolve(result.data.data)
        })
        .catch((err) => {
          reject(err.response.data)
        })
    })
  },
  UPLOAD_DOCUMENT({ commit }, payload) {
    return new Promise((resolve, reject) => {
      this.$axios.post(`/api/v1/driver/${payload.id}/upload/`, payload.data, { headers: { ...authHeader(), loader: true } })
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
      this.$axios.delete(`/api/v1/driver-document/${id}/`, { headers: { ...authHeader(), loader: true } })
        .then((result) => {
          resolve(result.data)
        })
        .catch((err) => {
          reject(err.response.data)
        })
    })
  },
  GET_DRIVER_DETAILS({ commit }, id) {
    return new Promise((resolve, reject) => {
      this.$axios.get(`/api/v1/driver/${id}/`, { headers: { ...authHeader(), loader: true } })
        .then((result) => {
          commit("SET_DRIVER_FORM_DETAILS", result.data)
          resolve(result.data)
        })
        .catch((err) => {
          reject(err.response.data)
        })
    })
  },
  UPDATE_DRIVER_DETAILS({ commit }, payload) {
    return new Promise((resolve, reject) => {
      this.$axios.put(`/api/v1/driver/${payload.id}/`, payload.data, { headers: { ...authHeader(), loader: true } })
        .then((result) => {
          commit("FIND_AND_PUSH_UPDATED_DRIVER_INTO_THE_LIST", result.data.data)
          resolve(result.data)
        })
        .catch((err) => {
          reject(err.response.data)
        })
    })
  },
  GET_VEHICLE_LIST_FOR_FORM({ commit }, project) {
    return new Promise((resolve, reject) => {

      this.$axios
        .get("/api/v1/vehicle/", {
          headers: { ...authHeader(), loader: true },
          params: {
            project_id: project,
            limit: "all",
          },
        })
        .then((result) => {
          let activeVehicleList = result.data.filter(v => v.status == "idle");
          commit("SET_VEHICLE_LIST", activeVehicleList)
          resolve(result.data)
        })
        .catch((err) => {
          reject(err.response.data)
        });
    })
  },
  GET_ZONE_LIST_FOR_FORM({ commit }, project) {
    return new Promise((resolve, reject) => {
      this.$axios
        .get("/api/v1/zones/", {
          headers: { ...authHeader(), loader: true },
          params: {
            project_id: project,
            limit: "all",
          },
        })
        .then((result) => {
          commit("SET_ZONE_LIST", result.data)
          resolve(result.data)
        })
        .catch((err) => {
          reject(err.response.data)
        });
    })
  },
  DOWNLOAD_ALL_DRIVERS({ commit }, params) {
    return new Promise((resolve, reject) => {
      this.$axios.get(`/api/v1/driver/download/`, {
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
        reject(error.response.data)
      })
    })
  },
  Add_DRIVER_TAG({ commit }, payload) {
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
        resolve(response)
      }).catch((error) => {
        reject(error.response)
      })
    })
  }
}