<script>
import { Bar } from "vue-chartjs";

export default {
  extends: Bar,
  props: {
    labels: Array,
    datasets: Array,
    options: Object,
  },
  mounted() {
    this.renderChart({
      labels: this.labels,
      datasets: this.datasets
    }, this.options)
  },
};
</script>
