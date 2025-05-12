import authHeader from "../authHeader"

export default {
  GET_TRIP_PLAN_DATA({ commit }, plan_id) {
    this.$axios.get(`/api/v1/trip_plan/${plan_id}/`, { headers: { ...authHeader(), loader: true } })
      .then((resp) => {
        commit('SET_UNASSIGNED_ORDERS', resp.data.unassigned_orders)
        commit('SET_UNASSIGNED_DRIVERS', resp.data.unassigned_drivers)
        commit('SET_PLANNED_TRIPS', resp.data.planned_trips)
        delete resp.data.unassigned_orders
        delete resp.data.unassigned_drivers
        delete resp.data.planned_trips

        commit('SET_PLAN_DETAILS', resp.data)

      }).catch((err) => { })
  },
  GET_PLANNED_TRIPS({ commit }, plan_id) {
    return new Promise((resolve, reject) => {
      this.$axios.get(`/api/v1/trip_plan/${plan_id}/planned_trips/`, { headers: { ...authHeader(), loader: true } })
        .then((resp) => {
          commit('SET_PLANNED_TRIPS', resp.data.results)
          resolve(resp.data.results)
        })
        .catch((err) => {
          reject(err)
        })
    })
  },
  GET_LOCATION_DATA({ commit }, param) {
    return new Promise((resolve, reject) => {
      this.$axios.get(`/api/v1/trip_plan/${param.plan_id}/planned_trips/${param.trip_id}/trip_route/`, { headers: { ...authHeader(), loader: true } })
        .then((resp) => {
          commit("SET_TRIP_LOCATION_DATA", resp.data.data)
          resolve(resp.data)
        })
        .catch((err) => {
          reject(err)
        })
    })
  },
  CONFIRM_TRIP({ commit }, payload) {
    return new Promise((resolve, reject) => [
      this.$axios.post(`/api/v1/trip_plan/${payload.plan_id}/create_trips/`, payload.data, { headers: { ...authHeader(), loader: true } })
        .then((resp) => {
          resolve(resp)
        })
        .catch((err) => {
          reject(err.response.data)
        })
    ])
  },
  GET_PLAN_INFORMATION({ commit }, id) {
    return new Promise((resolve, reject) => {
      this.$axios.get(`/api/v1/trip_plan/${id}/plan_info/`, { headers: { ...authHeader(), loader: true } })
        .then((result) => {
          commit('SET_PLAN_INFORMATION',result.data)
          resolve(result.data)
        })
        .catch((err) => {
          reject(err.response.data)
        })
    })
  },
  GET_PLAN_SUMMARY({ commit }, id) {
    return new Promise((resolve, reject) => {
      this.$axios.get(`/api/v1/trip_plan/${id}/summary/`, { responseType: 'blob', headers: { ...authHeader(), loader: true } })
        .then((result) => {
          resolve(result.data)
        })
        .catch((err) => {
          reject(err.response.data)
        })
    })
  },
  GET_UNPLANNED_ORDER_REASONS({ commit }, id) {
    return new Promise((resolve, reject) => {
      this.$axios.get(`/api/v1/trip_plan/${id}/unplanned_order_reasons/`, { responseType: 'blob', headers: { ...authHeader(), loader: true } })
        .then((result) => {
          resolve(result.data)
        })
        .catch((err) => {
          reject(err.response.data)
        })
    })
  }
}