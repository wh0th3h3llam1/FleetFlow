self.onmessage = function (e) {
  if (e.data && e.data.event == 'get_unread_notification') {
    checkForUnreadNotifications(e.data.url, e.data.token)
  } else if (e.data && e.data.event == 'get_trip_plan_list') {
    checkForTripPlans(e.data.url, e.data.token, e.data.params)
  }
}

function checkForUnreadNotifications(url, token) {
  notificationCall()
  setInterval(function () { notificationCall() }, 60000)
  function notificationCall() {
    fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `token ${token}`
      }
    })
      .then(response => response.json())
      .then(data => {
        let tempData = data
        self.postMessage({ 'event': 'unread_notification_count', 'unreadNotificationCount': tempData.data })
      })
      .catch((error) => {
        console.error('Error:', error);
      });
  }
}
function checkForTripPlans(url, token, params) {
  let param = cusntructParams(params)
  fetch(`${url}?${param}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `token ${token}`
    }
  })
    .then(response => response.json())
    .then(data => {
      let tempData = data
      self.postMessage({ 'event': 'set_trip_plan_list', 'trip_plan_list': tempData })
    })
    .catch((error) => {
      console.error('Error:', error);
    });
}

function cusntructParams(params) {
  let esc = encodeURIComponent;
  let query = Object.keys(params)
    .map(k => esc(k) + '=' + esc(params[k]))
    .join('&');
  return query
}
