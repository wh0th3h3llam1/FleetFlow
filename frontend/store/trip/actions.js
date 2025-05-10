import authHeader from "~/store/authHeader.js"

export default {
  GET_ALL_TRIPS(context, reload) {
    let params = {}
    if (!reload) {
      params.offset = context.state.Trips.length
    }

    let filters = localStorage.getItem("tripFilters");
    if (!filters) {
      filters = {};
    }
    if (typeof filters == typeof "string") {
      filters = JSON.parse(filters);
    }
    if (filters && "ordering" in filters && "sorting" in filters) {
      if (filters.sorting == "descending") {
        filters.ordering = "-" + filters.ordering;
      }
    }

    Object.assign(params, filters)
    if ('project' in params && params.project != null) {
      params.project = params.project.toString()
    }
    if ('status' in params && params.status != null) {
      params.status = params.status.toString()
    }
    return new Promise((resolve, reject) => {
      this.$axios.get('/api/v1/trip/', { headers: { ...authHeader(), loader: true }, params: params })
        .then((result) => {

          if (reload) {
            context.commit("SET_ALL_TRIPS", result.data)
          } else {
            context.commit("APPEND_TRIPS_TO_LIST", result.data.results)
          }
          resolve(result.data)
        })
        .catch((err) => {

          reject(err.response.data)
        })
    })
  },
  GET_TRIP_DETAILS({ commit }, id) {
    return new Promise((resolve, reject) => {
      this.$axios.get(`/api/v1/trip/${id}/`, { headers: { ...authHeader(), loader: true } })
        .then((result) => {
          commit("SET_TRIP_DETAILS", result.data)
          resolve(result.data)
        })
        .catch((err) => {

          reject(err.response.data)
        })
    })
  },
  GET_LOAD_SHEET_ITEM_LIST({ commit }, id) {
    return new Promise((resolve, reject) => {
      this.$axios.get(`/api/v1/trip/${id}/load_sheet/`, { headers: { ...authHeader(), loader: true } })
        .then((result) => {
          commit("SET_LOAD_SHEET_ITEM_LIST", result.data)
          resolve(result.data)
        })
        .catch((err) => {

          reject(err.response.data)
        })
    })
  },
  GET_TRIP_LOAD_SHEET_DATA({ commit }, payload) {
    return new Promise((resolve, reject) => {
      this.$axios.get(`/api/v1/trip/trip_load_sheet?start_date=${payload.toDate}&end_date=${payload.fromDate}`, { headers: { ...authHeader(), loader: true } })
        .then((result) => {
          resolve(result.data)
        })
        .catch((err) => {

          reject(err.response.data)
        })
    })
  },
  GET_TRIP_SHEET_ITEM_LIST({ commit }, id) {
    return new Promise((resolve, reject) => {
      this.$axios.get(`/api/v1/trip/${id}/trip_sheet/`, { headers: { ...authHeader(), loader: true } })
        .then((result) => {
          commit("SET_TRIP_SHEET_ITEM_LIST", result.data)
          resolve(result.data)
        })
        .catch((err) => {

          reject(err.response.data)
        })
    })
  },
  GET_TRIP_TEMPRATURE_DATA({ commit }, id) {
    return new Promise((resolve, reject) => {
      this.$axios.get(`/api/v1/trip/${id}/temperature_log/`, { headers: { ...authHeader(), loader: true } })
        .then((result) => {
          commit("SET_TEMPRATURE_DATA", result.data)
          resolve(result.data)
        })
        .catch((err) => {

          reject(err.response.data)
        })
    })
  },
  SET_TEMPRATURE_DATA({ commit }, payload) {
    return new Promise((resolve, reject) => {
      this.$axios.post(`/api/v1/trip/bulk_upload_temperature_sheet/`, payload, { headers: { ...authHeader(), loader: true } })
        .then((result) => {
          resolve(result.data)
        })
        .catch((err) => {
          reject(err.response.data)
        })
    })
  },
  GET_ACTUAL_DRIVER_ROUTE({ commit }, id) {
    return new Promise((resolve, reject) => {
      this.$axios.get(`/api/v1/trip/${id}/map_route`, { headers: { ...authHeader() } })
        .then((response) => {
          commit('SET_ACTUAL_DRIVER_ROUTE',response.data.data);
          resolve(response.data)
        })
        .catch((err) => {
          reject(err)
        })
    })
  }
}