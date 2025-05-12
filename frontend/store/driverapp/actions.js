import authHeader from "~/store/authHeader.js"

export default {
  GET_TRIP_DETAILS({ commit }, id) {
    return new Promise((resolve, reject) => {
      this.$axios.get(`/api/v2/app/trip/${id}/`, { headers: { ...authHeader() } }).then((response) => {
        commit("SET_TRIP_DETAILS", response.data);
        resolve(response.data)
      }).catch((err) => {
        reject(err)
        console.log(err);
      });
    })
  },
  GET_ORDER_LIST({ commit }) {
    return new Promise((resolve, reject) => {
      this.$axios.get('/api/v1/orders/', { headers: { ...authHeader() } }).then((response) => {
        commit("SET_ORDER_LIST", response.data);
        resolve(response.data)
      }).catch((err) => {
        reject(err)
        console.log(err);
      });
    })
  },
  GET_DRIVER_DETAILS({ commit }) {
    return new Promise((resolve, reject) => {
      this.$axios.get('/api/v2/app/driver/profile/', { headers: { ...authHeader() } }).then((response) => {
        commit("SET_DRIVER_DETAILS", response.data);
        resolve(response.data)
      }).catch((err) => {
        reject(err)
        console.log(err);
      });
    })
  },
  GET_TRIP_ROUTE({ commit },id) {
    return new Promise((resolve, reject) => {
      this.$axios.get(`/api/v2/app/trip/${id}/map_route/`, { headers: { ...authHeader() } }).then((response) => {
        commit("SET_TRIP_ROUTE", response.data.data);
        resolve(response.data)
      }).catch((err) => {
        reject(err)
        console.log(err);
      });
    })
  },
  GET_PARTIALLY_REASON({ commit }) {
    return new Promise((resolve, reject) => {
      this.$axios.get('/api/v2/app/statuses/successful/', { headers: { ...authHeader() } }).then((response) => {
        commit("SET_PARTIALLY_REASON", response.data.data);
        resolve(response.data)
      }).catch((err) => {
        reject(err)
        console.log(err);
      });
    })
  },
  GET_FAILED_REASONS({ commit }) {
    return new Promise((resolve, reject) => {
      this.$axios.get('/api/v2/app/statuses/failed/', { headers: { ...authHeader() } }).then((response) => {
        commit("SET_FAILED_REASONS", response.data.data);
        resolve(response.data)
      }).catch((err) => {
        reject(err)
        console.error(err);
      });
    })
  },
  DRIVER_DUTY({ commit }, payload) {
    return new Promise((resolve, reject) => {
      this.$axios.post(`/api/v2/app/driver/${payload.id}/status/`, payload.data, { headers: { ...authHeader() } }).then((response) => {
        resolve(response)
      }).catch((err) => {
        reject(err);
        console.error(err);
      });
    })
  },
  DELIVERED_ORDER({ commit }, payload) {
    return new Promise((resolve, reject) => {
      this.$axios.patch(`/api/v2/app/order/${payload.id}/`, payload.data, { headers: { ...authHeader() } }).then((response) => {
        resolve(response)
      }).catch((err) => {
        reject(err);
        console.error(err);
      });
    })
  },
  GET_ORDER_DETAILS({ commit }, id) {
    return new Promise((resolve, reject) => {
      this.$axios.get(`/api/v2/app/order/${id}/`, { headers: { ...authHeader() } }).then((response) => {
        commit("SET_ORDER_DETAILS", response.data);
        resolve(response.data)
      }).catch((err) => {
        reject(err)
        console.log(err);
      });
    })
  },
  ACTIVE_TRIP({ commit }, payload) {
    return new Promise((resolve, reject) => {
      this.$axios.post(`/api/v2/app/trip/${payload.id}/status/`, payload.data, { headers: { ...authHeader() } }).then((response) => {
        if(response.data.status == 'completed')
        {
           commit("SET_TRIP_DETAILS", response.data);
        }
        resolve(response.data)
      }).catch((err) => {
        reject(err)
        console.log(err);
      });
    })
  },
  DRIVER_ATTACHMENT_UPLOAD({ commit }, payload) {
    return new Promise((resolve, reject) => {
      this.$axios.post(`/api/v2/app/order/${payload.id}/attachments/`, payload.data, { headers: { ...authHeader() } }).then((response) => {
        resolve(response.data)
      }).catch((err) => {
        reject(err)
        console.log(err);
      });
    })
  }
}
