export default {
  getActiveFilterList: (state) => {
    return Object.keys(state.orderFilter).map((filter) => {
      return filter.replace(/\_/g, " ");
    });
  }
}