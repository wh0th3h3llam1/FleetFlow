export default {
  SET_ITEMS_LIST(state, payload) {
    state.items = payload.results
    state.totalItems = payload.count
  },
  UPDATE_ITEM_DETAILS_IN_ITEM_LIST(state, item_obj) {
    state.items.splice(state.items.indexOf(state.items.find(v => v.item_no == item_obj.item_no)), 1, item_obj)
  },
  ADD_ITEM_IN_ITEM_LIST(state, item_obj) {
    state.items.unshift(item_obj)
  },
  SET_ITEM_FORM_DETAILS(state, data) {
    state.formItem = data
  },
  SYNC_ITEM_FORM_DETAILS(state, data) {
    state.formItem[data.key] = data.value
  },
}