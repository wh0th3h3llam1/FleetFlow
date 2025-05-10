<script>
import { Bar } from "vue-chartjs";

export default {
  extends: Bar,
  props: {
    labels: Array,
    datasets: Object,
    options: Object,
  },
  mounted() {
    this.renderChart(this.datasets,
      this.options
    );
  },
};
</script>