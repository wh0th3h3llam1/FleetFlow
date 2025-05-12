import authHeader from "~/store/authHeader.js"

export default {
  ADD_ORDER(context, payload) {
    return new Promise((resolve, reject) => {
      this.$axios.post('/api/v1/order/', payload, { headers: { ...authHeader(), loader: true } })
        .then((result) => {
          context.commit("order/orderListStore/PUSH_ADDED_ORDER_TO_LIST", result.data, { root: true })
          resolve(result.data)
        })
        .catch((error) => {

          reject(error.response.data)
        })
    })
  },
  GET_ORDER_DETAILS_FOR_FORM({ commit }, id) {
    return new Promise((resolve, reject) => {
      this.$axios.get(`/api/v1/order/${id}/`, { headers: { ...authHeader(), loader: true } })
        .then((result) => {
          let _ = result.data
          let _items = result.data.items
          delete _.items
          if (!_.coordinates) {
            _.coordinates = {
              latitude: null,
              longitude: null
            }
          }
          commit("SET_ORDER_FORM_DETAILS", _)
          commit("SET_ORDER_ITEM_FORM_DETAILS", _items)
          resolve(result.data)
        })
        .catch((error) => {
          reject(error.response.data)
        })
    })
  },
  UPDATE_ORDER_DETAILS(context, payload) {
    return new Promise((resolve, reject) => {
      this.$axios.put(`/api/v1/order/${payload.id}/`, payload, { headers: { ...authHeader(), loader: true } })
        .then((result) => {
          resolve(result.data)
        })
        .catch((error) => {
          reject(error.response.data)
        })
    })
  },
  ADD_ATTACHMENT_INTO_ORDER(context, payload) {
    return new Promise((resolve, reject) => {
      this.$axios.post(`/api/v1/order/${payload.id}/upload_attachments/`, payload.data, { headers: { ...authHeader(), loader: true } })
        .then((result) => {
          resolve(result.data)
        })
        .catch((error) => {
          reject(error.response.data)
        })
    })
  },
  REMOVE_ATTACHMENT_INTO_ORDER({ commit }, payload) {
    return new Promise((resolve, reject) => {
      this.$axios.delete(`/api/v1/order-attachments/${payload.id}/`, { headers: { ...authHeader(), loader: true } })
        .then((result) => {
          commit('REMOVE_ATTACHMENT_INTO_ORDER_DETAILS', payload.index)
          resolve(result.data)
        })
        .catch((error) => {
          reject(error.response.data)
        })
    })
  }
}