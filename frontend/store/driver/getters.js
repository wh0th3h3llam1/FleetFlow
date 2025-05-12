export default {
  driverByStatus: (state) => (status) => {
    return state.drivers.filter((driver) => driver.status.toLowerCase() == status)
  }
}