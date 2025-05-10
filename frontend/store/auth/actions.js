export default {
  LOGIN({ commit }, payload) {
    return new Promise((resolve, reject) => {
      this.$axios
        .post('login/', payload)
        .then((res) => {
          localStorage.setItem('user', res.data.token)
          commit('AUTH_SUCCESS', res.data)
          resolve(res)
        })
        .catch((err) => {
          commit('AUTH_ERROR')
          reject(err.response.data)
        })
    })
  },
  LOGOUT({ commit }) {
    commit('LOGOUT')
    localStorage.clear();
    this.$router.push('/login')
  },
  CHECK_LOGIN({ commit }) {
    return new Promise((resolve, reject) => {
      if (localStorage.getItem('user') !== null) {
        resolve(localStorage.getItem('user'))
      } else {
        reject(new Error('Session out'))
      }
    })
  },
}
