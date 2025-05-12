export default {
  GET_HEADERS: (state) => {
    return state.headers.map((header) => {
      return {
        headerName: header,
        field: header,
        resizable: true
      }
    })
  },
  GET_REPORT_DATA: (state) => {
    return state.reportData.map((data, i) => {
      if (i != 0) {
        let _ = {}
        data.forEach((d, index) => {
          _[state.headers[index]] = d
        })
        return _
      } else {
        return null
      }
    }).filter((v) => v != null)
  }
}