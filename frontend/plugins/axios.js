export default function ({ $axios, store, redirect }) {
  $axios.onRequest(req => {
    if (req.headers.loader) {
      store.commit("TOGGLE_LOADER", true)
    }
    delete req.headers.loader
  })
  $axios.onResponse(res => {
    store.commit("TOGGLE_LOADER", false)
  })
  $axios.onResponseError(res => {
    store.commit("TOGGLE_LOADER", false)
  })
  $axios.onResponseError(err => {
    if (err.response && err.response.status === 401) {
      localStorage.removeItem('user')
      redirect('/login/')
    }
  })
}
