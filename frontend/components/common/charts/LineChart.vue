<script>
import { Line } from 'vue-chartjs'

export default {
  extends: Line,
  props: {
    datasets: Object,
    options: Object
  },
  mounted () {
    this.renderChart(this.datasets, this.options)
  }
}
</script>