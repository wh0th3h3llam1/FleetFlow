export default ({ app, store }, inject) => {
    inject('notifier', {
        showMessage({ content = '', color = '', right = false, }) {
            store.commit('notification/showMessage', { content, color, right })
        }
    })
}