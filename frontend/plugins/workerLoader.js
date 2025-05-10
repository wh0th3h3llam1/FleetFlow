import NotificationWorker from '~/assets/js/notification.worker.js'

export default (context, inject) => {
    inject('notiWorker', {
        createWorker() {
            return new NotificationWorker()
        }
    })
}