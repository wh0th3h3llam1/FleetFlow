import authHeader from '~/store/authHeader'

export default {
  CHECK_ITEM_CODES({ commit }, payload) {
    return new Promise((resolve, reject) => [
      this.$axios
        .post(`api/v1/items/exists/`, payload, {
          headers: { ...authHeader(), loader: true },
        })
        .then((resp) => {
          resolve(resp)
        })
        .catch((err) => {
          reject(err)
        })
    ])
  },
  CHECK_CUSTOMER_CODES({ commit }, payload) {
    return new Promise((resolve, reject) => [
      this.$axios
        .post(`api/v1/customer_address/exists/`, payload, {
          headers: { ...authHeader(), loader: true },
        })
        .then((resp) => {
          resolve(resp)
        })
        .catch((err) => {
          reject(err)
        })
    ])
  },
  UPLOAD_ORDERS({ commit }, payload) {
    return new Promise((resolve, reject) => [
      this.$axios
        .post(`api/v1/orders/bulk_upload`, payload, {
          headers: { ...authHeader(), loader: true },
        })
        .then((resp) => {
          resolve(resp.data)
        })
        .catch((err) => {
          reject(err.response.data)
        })
    ])
  },
  UPDATE_ORDERS({ commit }, payload) {
    return new Promise((resolve, reject) => [
      this.$axios
        .post(`api/v1/orders/bulk_update`, payload, {
          headers: { ...authHeader(), loader: true },
        })
        .then((resp) => {
          resolve(resp.data)
        })
        .catch((err) => {
          reject(err.response.data)
        })
    ])
  },
  UPLOAD_B2C_ORDERS({ commit }, payload) {
    return new Promise((resolve, reject) => [
      this.$axios
        .post(`api/v1/orders/bulk_upload_b2c`, payload, {
          headers: { ...authHeader(), loader: true },
        })
        .then((resp) => {
          resolve(resp.data)
        })
        .catch((err) => {
          reject(err.response.data)
        })
    ])
  },
}