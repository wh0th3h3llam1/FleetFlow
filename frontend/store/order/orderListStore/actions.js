import authHeader from "~/store/authHeader"

export default {
  GET_ALL_ORDERS(context, reload) {
    let params = {}
    if (!reload) {
      params.offset = context.state.Orders.length
    }

    let filters = localStorage.getItem("orderFilters");
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
      this.$axios.get("/api/v1/order/", { headers: { ...authHeader(), loader: reload }, params: params })
        .then((result) => {
          if (reload) {
            context.commit("SET_ORDER_LIST", result.data)
          }
          else {
            context.commit("APPEND_ORDER_LIST", result.data)
          }
          resolve(result)
        })
        .catch((error) => {

          reject(error.response)
        })
    })
  },
  DELETE_ORDERS(context, ids) {
    return new Promise((resolve, reject) => {
      this.$axios.delete(`/api/v1/order/delete/`, { headers: { ...authHeader(), loader: true }, params: { order_ids: ids} })
        .then((result) => {

          resolve(result.data)
        })
        .catch((error) => {
          reject(error.response.data)
        })

    })
  }
}