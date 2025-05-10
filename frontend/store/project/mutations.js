export default {
  SET_PROJECT_LIST(state, data) {
    state.projects = data.results
    state.totalItems = data.count
  },
  SET_ALL_PROJECT_LIST(state,data){
    state.allProjects = data
  },
  SET_PROJECT_DETAILS(state, data) {
    state.projectForm = data
  },
  SYNC_PROJECT_FORM_DETAILS(state, data) {
    if (data.subKey) {
      state.projectForm[data.key][data.subKey] = data.value
    }
    else {
      state.projectForm[data.key] = data.value
    }
  },
  UPDATE_PROJECT_DETAILS_IN_LIST(state, data) {
    state.projects.splice(state.projects.indexOf(state.projects.find(v => v.id == data.id)), 1, data)
  },
  ADD_PROJECT_DETAILS_IN_LIST(state, data) {
    state.projects.unshift(data)
  },
}
