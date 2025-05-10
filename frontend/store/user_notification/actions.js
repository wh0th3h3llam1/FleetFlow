import authHeader from "../authHeader"

export default {
  GET_ALL_NOTIFICATIONS(context, reload) {
    let params = {}
    params.offset = 0
    if (!reload) {
      params.offset = context.state.userNotifications.length;
    }
    params.limit = 10;
    return new Promise((resolve, reject) => {
      this.$axios.get("/api/v1/notification/", { headers: authHeader(), params: params })
        .then((result) => {
          if (reload) {
            context.commit("SET_ALL_NOTIFICATIONS", result.data)
          } else {
            context.commit("APPEND_NOTIFICATIONS", result.data)
          }
          resolve(result.data)
        })
        .catch((err) => {
          reject(err.response.data)
        })
    })
  },
  MARK_AS_READ({ commit }, id) {
    return new Promise((resolve, reject) => {
      this.$axios.patch(`/api/v1/notification/${id}/mark_as_read/`, id, { headers: authHeader() })
        .then((result) => {
          resolve(result.data)
        })
        .catch((err) => {
          reject(err.response.data)
        })
    })
  },
  MARK_ALL_AS_READ({ commit }, ids) {
    return new Promise((resolve, reject) => {
      this.$axios.patch(`/api/v1/notification/mark_all_as_read/`, ids, { headers: authHeader() })
        .then((result) => {
          resolve(result.data)
        })
        .catch((err) => {
          reject(err.response.data)
        })
    })
  }
}