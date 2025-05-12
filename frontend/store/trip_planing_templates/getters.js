export default {
  GET_TEMPLATE_LIST_FOR_DROPDOWN: (state) => {
    return state.newTemplatesList.map(template => {
      return {
        text: template.template_name,
        value: template.template_name,
      }
    })
  }
}
