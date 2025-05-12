export default {
  SET_TRIP_PLANNING_TEMPLATES_LIST(state, data) {
    state.totalItems = data.count
    state.templatesList = data.results
  },
  SET_ALL_TEMPLATE_LIST(state, data) {
    state.newTemplatesList = data
  },
  SET_TEMPLATE_FORM_DATA(state, data) {
    state.templateDetails = data
  },
  SYNC_TEMPLATE_FORM_DATA(state, data) {
    state.templateDetails[data.key] = data.value
  },
  TOGGLE_READONLY(state, readOnly) {
    state.readOnly = readOnly
  },
  TOGGLE_EDIT_MODE(state, editMode) {
    state.editMode = editMode
  }
}
