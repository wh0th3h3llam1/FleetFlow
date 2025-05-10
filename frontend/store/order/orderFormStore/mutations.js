export default {
  SET_ORDER_FORM_DETAILS(state, data) {
    state.formOrder = data
  },
  SYNC_ORDER_FORM_DETAILS(state, data) {
    if (data.key && data.subKey) {
      state.formOrder[data.key][data.subKey] = data.value
    } else {
      state.formOrder[data.key] = data.value
    }
  },
  SET_ORDER_ITEM_FORM_DETAILS(state, data) {
    if (data.length != 0) {
      state.items = data
    }
  },
  EMPTY_ORDER_FORM_DETAILS(state) {
    state.formOrder = {
      execution_date: new Date().toISOString().slice(0, 10),
      order_type: "delivery",
      barcode_scanning: false,
      pod_required: true,
      customer_notifications: true,
      payment_type: "prepaid",
      customer_name: null,
      customer_code: null,
      customer_type: null,
      contact_number: null,
      project: null,
      address: null,
      contact_email: null,
      contact_person: null,
      remarks: null,
      processing_time: null,
      coordinates: {
        latitude: null,
        longitude: null,
      },
    }
  },
  EMPTY_ORDER_ITEM_FORM_DETAILS(state) {
    state.items = [
      {
        item_no: null,
        item_description: null,
        quantity: null,
        delivered_quantity: null,
      }
    ]
  },
  SYNC_ORDER_ITEMS_FORM_DETAILS(state, data) {
    if ('index' in data && 'key' in data) {
      state.items[data.index][data.key] = data.value
    }
  },
  ADD_ITEM_TO_LIST(state) {
    state.items.push({
      item_no: null,
      item_description: null,
      quantity: null,
      delivered_quantity: null,
      isNewItem: true,
    })
  },
  REMOVE_ITEM_FROM_LIST(state, index) {
    if (state.items.length > 1) {
      state.items.splice(index, 1)
    }
  },
  REMOVE_ATTACHMENT_INTO_ORDER_DETAILS(state, index) {
    state.formOrder.order_attachments.splice(index, 1);
  },
}