export default {
    ROLE_LIST_FOR_DROPDOWN: (state) => {
      return state.rolelist.map(role => {
        return {
          text: role.role_name,
          value: role.id,
        }
      })
    },
  }