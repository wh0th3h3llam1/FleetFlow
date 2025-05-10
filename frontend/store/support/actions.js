import authHeader from "~/store/authHeader.js"

export default {
  GET_TICKETS_DATA({ commit }, params) {
    return new Promise((resolve, reject) => {
      this.$axios.get('/api/v1/support/', { headers: { ...authHeader() }, params: params }).then((response) => {
        commit('SET_TICKETS_DATA', response.data);
        resolve(response.data.results);
      })
        .catch((error) => {
          console.error(error.response);
          reject(error.response);
        })
    })
  },
  ADD_TICKET({ commit }, payload) {
    return new Promise((resolve, reject) => {
      this.$axios.post('api/v1/support/', payload, { headers: { ...authHeader() } }).then((response) => {
        commit('ADD_TICKET_DETAILS', response.data)
        resolve(response.data)
      }).catch((error) => {
        console.log(error.response)
        reject(error.response)
      })
    })
  },
  UPDATE_TICKET({ commit }, payload) {
    return new Promise((resolve, reject) => {
      this.$axios.put(`api/v1/support/${payload.id}/`, payload.data, { headers: { ...authHeader() } }).then((response) => {
        commit('SET_TICKET_DETAILS_INTO_LIST', response.data)
        resolve(response.data)
      }).catch((error) => {
        console.log(error.response)
        reject(error.response)
      })
    })
  },
  GET_TICKET_DETAILS({ commit }, id) {
    return new Promise((resolve, reject) => {
      this.$axios.get(`api/v1/support/${id}/`, { headers: { ...authHeader() } }).then((response) => {
        commit('SET_TICKET_DETAILS', response.data)
        resolve(response.data)
      }).catch((error) => {
        console.log(error.response)
        reject(error.response)
      })
    })
  },
  ADD_COMMENT_IN_TICKET_DETAILS({ commit }, payload) {
    return new Promise((resolve, reject) => {
      this.$axios.post(`api/v1/support/${payload.id}/comment/`, payload.data, { headers: { ...authHeader() } }).then((response) => {
        commit('SET_COMMENT_INTO_TICKET_DETAILS', response.data.data)
        resolve(response.data)
      }).catch((error) => {
        console.log(error.response)
        reject(error.response)
      })
    })
  },
  GET_TICKET_LOGS({ commit }, id) {
    return new Promise((resolve, reject) => {
        this.$axios.get(`/api/v1/support/${id}/logs/`, { headers: { ...authHeader() }}).then((response) => {
          commit('SET_TICKET_LOGS', response.data);
          resolve(response.data);
        }
      ).catch((error) => {
          console.error(error.response);
          reject(error.response);
        })
    })
  }

}