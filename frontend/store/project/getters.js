export default {
  PROJECT_LIST_FOR_DROPDOWN: (state) => {
    return state.allProjects.map(project => {
      return {
        text: project.project_name,
        value: project.project_id,
      }
    })
  },
  PROJECT_LIST_FOR_FILTER: (state) => {
    return state.allProjects.map(project => {
      return {
        text: project.project_name,
        value: project.id,
      }
    })
  }
}