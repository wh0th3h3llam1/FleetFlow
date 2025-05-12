import authHeader from '~/store/authHeader.js'

export default {
  GET_ALL_ITEMS({ commit }, params) {
    return new Promise((resolve, reject) => {
      if (params && params.search && (params.search == null || params.search.trim().length == 0)) {
        delete params.search
      }
      this.$axios.get('/api/v1/items/', {
        headers: { ...authHeader(), loader: true },
        params: params
      })
        .then((success) => {
          commit("SET_ITEMS_LIST", success.data)
          resolve(success.data)
        })
        .catch((error) => {
          reject(error.response.data)
        })
    })
  },
  ADD_ITEM(context, payload) {
    return new Promise((resolve, reject) => {
      this.$axios.post(`/api/v1/items/`, payload.data, {
        headers: { ...authHeader(), loader: true },
      })
        .then((success) => {
          if (!payload.isBulkupload) {
            context.commit("item/ADD_ITEM_IN_ITEM_LIST", success.data, { root: true })
          }
          resolve(success.data)
        })
        .catch((error) => {
          reject(error.response.data)
        })
    })
  },
  GET_ITEM_DETAILS({ commit }, id) {
    return new Promise((resolve, reject) => {
      this.$axios.get(`/api/v1/items/${id}/`, {
        headers: { ...authHeader(), loader: true },
      })
        .then((success) => {

          commit("SET_ITEM_FORM_DETAILS", success.data)
          resolve(success.data)
        })
        .catch((error) => {

          reject(error.response.data)
        })
    })
  },
  UPDATE_ITEM_DETAILS(context, obj) {
    return new Promise((resolve, reject) => {
      this.$axios.put(`/api/v1/items/${obj.id}/`, obj.payload, {
        headers: authHeader(),
      })
        .then((success) => {
          context.commit("item/UPDATE_ITEM_DETAILS_IN_ITEM_LIST", success.data, { root: true })
          resolve(success.data)
        })
        .catch((error) => {

          reject(error.response.data)
        })
    })
  },
  DOWNLOAD_ALL_ITEMS(context) {
    return new Promise((resolve, reject) => {
      this.$axios.get(`/api/v1/items/download/`, {
        responseType: 'blob',
        headers: { ...authHeader(), loader: true },
      }).then((success) => {
        resolve(success.data)
      }).catch((error) => {
        reject(error.response.data)
      })
    })
  }
}