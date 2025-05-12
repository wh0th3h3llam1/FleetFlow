export default {
  AUTH_SUCCESS(state, data) {
    state.token = data.token
  },
  AUTH_ERROR(state) {
    state.authenticated = false
  },
  LOGOUT(state) {
    state.token = ''
  },
  REFRESH_USER_DATA(state) {
    state.token = localStorage.getItem('user')
  },
}
