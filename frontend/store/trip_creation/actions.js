import authHeader from "../authHeader"

export default {
  GET_UNASSIGNED_ORDERS({ commit }, params) {
    return new Promise((resolve, reject) => {
      this.$axios.get('/api/v1/filter_trip_orders/', { headers: { ...authHeader(), loader: true }, params: params })
        .then((result) => {
          commit('SET_UNASSIGNED_ORDERS_LIST', result.data)
          resolve(result.data)
        })
        .catch((err) => {
          reject(err)
        })
    })
  },
  GET_UNASSIGNED_DRIVERS({ commit }, params) {
    return new Promise((resolve, reject) => {
      this.$axios
        .get("/api/v1/driver/", {
          headers: { ...authHeader(), loader: true },
          params: params
        })
        .then((result) => {
          commit('SET_UNASSIGNED_DRIVERS_LIST', result.data)
          resolve(result);
        })
        .catch((err) => {
          reject(err);
        });
    });
  },

  /** plan_trips actions */
  GET_ALL_TRIP_PLANS({ commit }, params) {
    return new Promise((resolve, reject) => {
      this.$axios.get('/api/v1/trip_plan/', { headers: { ...authHeader(), loader: true }, params: params })
        .then((result) => {
          commit("SET_RECENTLY_PLANNED_TRIPS", result.data)
          resolve(result.data)
        })
        .catch((err) => {
          reject(err)
        })
    })
  },
  DELETE_PLANED_TRIP({ commit }, plan_id) {
    return new Promise((resolve, reject) => {
      this.$axios.delete(`/api/v1/trip_plan/${plan_id}/`, { headers: { ...authHeader(), loader: true } })
        .then((resp) => {
          commit('REMOVE_RECENTLY_PLANNED_TRIPS', plan_id)
          resolve(resp.data.results)
        })
        .catch((err) => {
          reject(err)
        })
    })
  },
  PLAN_NEW_TRIP({ commit }, payload) {
    return new Promise((resolve, reject) => {
      this.$axios.post('/api/v1/trip_plan/', payload, { headers: { ...authHeader(), loader: true } })
        .then((result) => {
          resolve(result.data)
        })
        .catch((err) => {
          reject(err.response)
        })
    })
  },
  GET_TRIP_RECOMMANDATION({ commit }, params) {
    return new Promise((resolve, reject) => {
      this.$axios.post(`/api/v1/order/get_trip_recommendations/`, params, { headers: authHeader() })
        .then((result) => {
          // commit("SET_TRIP_DETAILS", result.data)
          resolve(result.data)
        })
        .catch((err) => {
          reject(err.response.data)
        })
    })
  },
  GET_UNASSIGNED_ORDER_FOR_PLAN_TRIP({ commit }, params) {
    return new Promise((resolve, reject) => {
      let url = `/api/v1/project/${params.project_id}/validate_trip_plan/`
      delete params.project_id
      this.$axios.get(url, { headers: { ...authHeader(), loader: true }, params: params })
        .then((result) => {
          resolve(result.data)
        })
        .catch((err) => {
          reject(err.response.data)
        })
    })
  },
  RETRY_PLAN_TRIP({ commit }, id) {
    return new Promise((resolve, reject) => {
      this.$axios.patch(`/api/v1/trip_plan/${id}/retry_plan/`,{}, { headers: { ...authHeader(), loader: true }})
        .then((result) => {
          resolve(result.data)
        })
        .catch((err) => {
          reject(err.response.data)
        })
    })
  }
}