export default function ({ store, redirect }) {
  // If the user is not authenticated
  store
    .dispatch('auth/CHECK_LOGIN')
    .then(() => {
    })
    .catch(() => {
      return redirect('/login')
    })
}
