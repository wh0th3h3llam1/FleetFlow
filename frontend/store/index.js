import authHeader from "./authHeader"

export default {
  state: () => ({
    showLoader: false,
    fleetUtilization: {},
    orderGraph: {},
    orderScore: {}
  }),
  mutations: {
    TOGGLE_LOADER(state, showLoader) {
      state.showLoader = showLoader
    },
    SET_FLEET_UTILIZATION_DATA(state, data) {
      state.fleetUtilization = data
    },
    SET_ORDER_GRAPH_DATA(state, data) {
      state.orderGraph = data.order_graph
    },
    SET_ORDER_SCORE_DATA(state, data) {
      state.orderScore = data
    }
  },
  getters: {
    FLEET_UTILIZATION_DATA: (state) => {
      let fleetUtilizationLabels = []
      let fleetUtilization = [
        {
          label: "No. of Trucks",
          backgroundColor: "#9b182f",
          data: [],
        },
      ];
      let totalDropPoint = {
        labels: [],
        datasets: [
          {
            label: "Drop Points per Day",
            backgroundColor: "#f97d9d",
            data: [],
          },
        ],
      };
      for (const key in state.fleetUtilization) {
        fleetUtilizationLabels.push(key)
        totalDropPoint.labels.push(key)
        if (Object.keys(state.fleetUtilization[key]).length > 0) {
          totalDropPoint.datasets[0]['data'].push(state.fleetUtilization[key]['drop_points_per_day'])
          fleetUtilization[0].data.push(state.fleetUtilization[key]['utilized_vehicle_count'])
        } else {
          totalDropPoint.datasets[0]['data'].push(0)
          fleetUtilization[0].data.push(0)
        }
      }
      return { fleetUtilizationLabels, fleetUtilization, totalDropPoint }
    },
    COMPLETED_ORDERS_DATA: (state) => {
      let completedOrders = {
        labels: [],
        datasets: [
          {
            label: "Orders",
            backgroundColor: "#9b182f",
            data: [],
          },
        ],
      }
      for (const key in state.orderGraph) {
        completedOrders.labels.push(key)
        completedOrders.datasets[0].data.push(state.orderGraph[key])
      }
      return completedOrders
    }
  },
  actions: {
    GET_FLEET_UTILIZATION_DATA({ commit }, params) {
      return new Promise((resolve, reject) => {
        this.$axios.get("/api/v1/dashboard/fleet_utlization/", { headers: authHeader(), params: Object.keys(params).length > 0 ? params : '' })
          .then((result) => {
            commit("SET_FLEET_UTILIZATION_DATA", result.data)
            resolve(result.data)
          })
          .catch((err) => {
            reject(err.response.data)
          })
      })
    },
    GET_ORDER_GRAPH_DATA({ commit }, params) {
      return new Promise((resolve, reject) => {
        this.$axios.get("/api/v1/dashboard/orders/", { headers: authHeader(), params: Object.keys(params).length > 0 ? params : '' })
          .then((result) => {
            commit("SET_ORDER_GRAPH_DATA", result.data)
            resolve(result.data)
          })
          .catch((err) => {
            reject(err.response.data)
          })
      })
    },
    GET_DASHBOARD_SCORECARD({ commit }, params) {
      return new Promise((resolve, reject) => {
        this.$axios.get("/api/v1/dashboard/scorecard/", { headers: authHeader(), params: params })
          .then((result) => {
            commit("SET_ORDER_SCORE_DATA", result.data)
            resolve(result.data)
          })
          .catch((err) => {
            reject(err.response.data)
          })
      })
    }
  }
}