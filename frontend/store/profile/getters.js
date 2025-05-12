export default {
    MENU(state) {
        if (Object.keys(state.permissions).length != 0) {
            return state.menu.filter((obj) => {
                if (obj.key) {
                    return state.permissions[obj.key]['view']
                } else {
                    return true
                }
            })
        } else {
            return []
        }
    }
}