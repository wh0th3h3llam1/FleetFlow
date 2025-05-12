export default {
    TEMRATURE_DATA: (state) => {
        let timeStamps = []
        let datasets = []
        for (let key in state.tempratureData) {
            if (state.tempratureData[key].length > 0) {
                if (timeStamps.length) {
                    continue
                } else {
                    timeStamps = state.tempratureData[key].map((obj) => {
                        return obj;
                    })
                }
            }
        }
        return {
            labels: timeStamps, datasets:
                Object.keys(state.tempratureData).map(key => {
                    if (state.tempratureData[key].length) {
                        return {
                            label: key.toUpperCase(),
                            data: state.tempratureData[key].map(t => {
                                return t.temperature
                            }),
                            fill: false,
                            borderColor: key == 'dry' ? '#fab079' : key == 'chilled' ? '#f97d9d' : key == 'frozen' ? '#13b6cf' : ''
                        }
                    } else {
                        return null
                    }
                }).filter(a => a != null)
        }
    }
}