<template>
  <div class="pa-6">
    <v-row no-gutters>
      <v-col cols="12">
        <div class="full-width background-white rounded-lg">
          <div
            class="
              pa-2
              background-light_grey
              rounded-t-lg
              border-x-light_black
              border-y-light_black
            "
          >
            <span
              class="px-3 text-grey text-h6 text-uppercase font-weight-bold"
            >
              Total Orders 
            </span>
          </div>
          <div
            class="
              rounded-b-lg
              pa-4
              border-x-light_black
              border-bottom-light_black
            "
          >
            <v-row no-gutters>
              <v-col cols="12" class="">
                <v-menu
                  ref="menu"
                  v-model="menu"
                  :close-on-content-click="false"
                  nudge-left="100"
                  transition="scale-transition"
                  offset-y
                  max-width="290px"
                  min-width="auto"
                >
                  <template v-slot:activator="{ on, attrs }">
                    <v-text-field
                      style="max-width: 350px"
                      v-model="orderMonth"
                      placeholder="Select Month"
                      prepend-inner-icon="mdi-calendar"
                      dense
                      outlined
                      hide-details
                      readonly
                      v-bind="attrs"
                      v-on="on"
                    ></v-text-field>
                  </template>
                  <v-date-picker
                    v-model="orderMonth"
                    :max="nowDate"
                    type="month"
                    no-title
                    scrollable
                    @change="
                      get_order_graph_data();
                      $refs.menu.save(orderMonth);
                    "
                  >
                  </v-date-picker>
                </v-menu>
              </v-col>
              <v-col cols="12">
                <div>
                  <CommonChartsStackedbarchart
                    v-if="chart3"
                    :labels="getOrderGraphData.keys"
                    :datasets="[
                      {
                        label: 'Returned',
                        backgroundColor: '#B71C1C',
                        data: getOrderGraphData.failed,
                      },
                      {
                        label: 'Partially Delivered',
                        backgroundColor: '#9C27B0',
                        data: getOrderGraphData.partial,
                      },
                      {
                        label: 'Delivered',
                        backgroundColor: '#2E7D32',
                        data: getOrderGraphData.successful,
                      },
                    ]"
                    :options="stackBarOptions"
                  />
                </div>
                <div
                  class="
                    d-flex
                    align-center
                    justify-center
                    loader-container
                    full-width
                  "
                  v-if="!chart2"
                >
                  <v-progress-circular
                    :size="100"
                    :width="7"
                    color="primary"
                    indeterminate
                  ></v-progress-circular>
                </div>
              </v-col>
            </v-row>
          </div>
        </div>
      </v-col>
      <v-col cols="4" class="border-top-light_black pt-4 d-flex mt-8">
        <v-menu
          v-model="toDate"
          :close-on-content-click="false"
          :nudge-right="40"
          transition="scale-transition"
          offset-y
          min-width="auto"
        >
          <template v-slot:activator="{ on, attrs }">
            <v-text-field
              v-model="getFromDate"
              label="From"
              class="mr-4"
              prepend-inner-icon="mdi-calendar"
              readonly
              outlined
              dense
              hide-details="auto"
              v-bind="attrs"
              v-on="on"
            ></v-text-field>
          </template>
          <v-date-picker
            @change="dateValidator"
            :max="nowDate"
            v-model="getFromDate"
            @input="toDate = false"
          ></v-date-picker>
        </v-menu>

        <v-menu
          v-model="fromDate"
          :close-on-content-click="false"
          :nudge-right="40"
          transition="scale-transition"
          offset-y
          min-width="auto"
        >
          <template v-slot:activator="{ on, attrs }">
            <v-text-field
              v-model="getToDate"
              label="To"
              prepend-inner-icon="mdi-calendar"
              readonly
              dense
              outlined
              hide-details="auto"
              v-bind="attrs"
              v-on="on"
            ></v-text-field>
          </template>
          <v-date-picker
            @change="dateValidator"
            v-model="getToDate"
            :max="nowDate"
            @input="fromDate = false"
          ></v-date-picker>
        </v-menu>
      </v-col>
      <v-col cols="8"></v-col>
      <v-col cols="6" class="pt-4 pr-2">
        <div class="full-width background-white rounded-lg">
          <div
            class="
              pa-2
              background-light_grey
              rounded-t-lg
              border-x-light_black
              border-y-light_black
            "
          >
            <span
              class="px-3 text-grey text-h6 text-uppercase font-weight-bold"
            >
              Fleet Utilization
            </span>
          </div>
          <div
            class="
              rounded-b-lg
              pa-4
              border-x-light_black
              border-bottom-light_black
            "
          >
            <CommonChartsTwoBarChart
              v-if="chart"
              ref="barChart"
              :labels="fleetUtilization.fleetUtilizationLabels"
              :datasets="fleetUtilization.fleetUtilization"
              :options="barOptions"
            />
            <div
              class="
                loader-container
                d-flex
                align-center
                justify-center
                full-width
              "
              v-if="!chart"
            >
              <v-progress-circular
                :size="70"
                :width="7"
                color="primary"
                indeterminate
              ></v-progress-circular>
            </div>
          </div>
        </div>
      </v-col>
      <v-col cols="6" class="pt-4 pl-2">
        <div class="full-width background-white rounded-lg">
          <div
            class="
              pa-2
              background-light_grey
              rounded-t-lg
              border-x-light_black
              border-y-light_black
            "
          >
            <span
              class="px-3 text-grey text-h6 text-uppercase font-weight-bold"
            >
              Drop Points per Day
            </span>
          </div>
          <div
            class="
              rounded-b-lg
              pa-4
              border-x-light_black
              border-bottom-light_black
            "
          >
            <div v-if="Object.keys(fleetUtilization.totalDropPoint).length > 0">
              <CommonChartsLineChart
                v-if="chart"
                :datasets="fleetUtilization.totalDropPoint"
                :options="barOptions"
              />
            </div>
            <div
              class="
                loader-container
                d-flex
                align-center
                justify-center
                full-width
              "
              v-if="!chart"
            >
              <v-progress-circular
                :size="70"
                :width="7"
                color="primary"
                indeterminate
              ></v-progress-circular>
            </div>
          </div>
        </div>
      </v-col>
      <v-col cols="12" class="mt-4">
        <v-row no-gutters>
          <v-col
            class="pb-4"
            v-cloak
            cols="3"
            v-for="(key, index) in Object.keys(orderScoreData)"
            :key="index"
            :class="
              index == 0 || index == 4
                ? 'pr-2'
                : index == 3 || index == 7
                ? 'pl-2'
                : 'px-2'
            "
          >
            <div class="full-width background-white rounded-lg">
              <div
                class="
                  pa-2
                  text-center
                  background-light_grey
                  rounded-t-lg
                  border-x-light_black
                  border-y-light_black
                "
              >
                <span
                  class="text-h6 text-grey font-weight-bold text-capitalize"
                >
                  {{ key.replace(/\_/g, " ") }}
                </span>
              </div>
              <div
                class="
                  px-4
                  py-6
                  rounded-b-lg
                  text-center text-h4
                  border-x-light_black
                  font-weight-bold
                  border-bottom-light_black
                "
              >
                {{ orderScoreData[key] }}
              </div>
            </div>
          </v-col>
        </v-row>
      </v-col>
    </v-row>
  </div>
</template>

<script>
export default {
  data() {
    return {
      chart: true,
      chart2: true,
      chart3: true,
      orderMonth: new Date().toISOString().substr(0, 7),
      menu: false,
      toDate: false,
      fromDate: false,
      getFromDate: null,
      getToDate: null,
      menu2: false,
      nowDate: new Date().toISOString().slice(0, 10),
      selectedDates: [],
      stackBarOptions: {
        responsive: true,
        maintainAspectRatio: false,
        datasets: {
          bar: {
            categoryPercentage: 0.5,
            barPercentage: 1,
          },
        },
        scales: {
          xAxes: [
            {
              stacked: true,
            },
          ],
          yAxes: [
            {
              stacked: true,
            },
          ],
        },
      },
      barOptions: {
        scales: {
          yAxes: [
            {
              ticks: {
                stepSize: 50,
                beginAtZero: true,
              },
            },
          ],
        },
        responsive: true,
        maintainAspectRatio: false,
      },
    };
  },
  computed: {
    selectedDateText() {
      return this.selectedDates.join(" to ");
    },
    fleetUtilization() {
      return this.$store.getters["FLEET_UTILIZATION_DATA"];
    },
    orderGraphData() {
      return this.$store.getters["COMPLETED_ORDERS_DATA"];
    },
    getOrderGraphData() {
      let orders = this.$store.state.orderGraph;
      let keys = Object.keys(orders);
      let successful = [];
      let failed = [];
      let partial = [];
      for (const [key, value] of Object.entries(orders)) {
        successful.push(orders[key].successful);
        failed.push(orders[key].failed);
        partial.push(orders[key].partially_delivered);
      }
      return {
        keys: keys,
        successful: successful,
        failed: failed,
        partial: partial,
      };
    },
    orderScoreData() {
      return this.$store.state.orderScore;
    },
  },
  methods: {
    dateValidator() {
      if (
        this.getFromDate &&
        this.getToDate &&
        this.getFromDate > this.getToDate
      ) {
        let _ = this.getToDate;
        this.getToDate = this.getFromDate;
        this.getFromDate = _;
        this.get_fleet_data();
        this.get_dashboard_scorecard();
      } else {
        this.get_fleet_data();
        this.get_dashboard_scorecard();
      }
    },
    get_fleet_data() {
      this.chart = false;
      let params = {};
      if (this.getFromDate && this.getToDate) {
        params.start_date = this.getFromDate;
        params.end_date = this.getToDate;
      }
      this.$store
        .dispatch("GET_FLEET_UTILIZATION_DATA", params)
        .then((result) => {
          this.chart = true;
        })
        .catch((err) => {
          if (err.message) {
            this.$notifier.showMessage({
              content: err.message,
              color: "error",
            });
          }
          this.$notifier.showMessage({
            content: "Error fetching data",
            color: "error",
          });
        });
    },
    get_order_graph_data() {
      this.chart2 = false;
      this.chart3 = false;
      let params = {};
      if (this.orderMonth) {
        let date = new Date(this.orderMonth);
        params.year = date.getFullYear();
        params.month = date.getMonth() + 1;
      }
      this.$store
        .dispatch("GET_ORDER_GRAPH_DATA", params)
        .then((result) => {
          this.chart2 = true;
          this.chart3 = true;
        })
        .catch((err) => {
          if (err.message) {
            this.$notifier.showMessage({
              content: err.message,
              color: "error",
            });
          }
          this.$notifier.showMessage({
            content: "Error fetching data",
            color: "error",
          });
        });
    },
    get_dashboard_scorecard() {
      this.chart = false;
      let params = {};
      if (this.getFromDate && this.getToDate) {
        params.start_date = this.getFromDate;
        params.end_date = this.getToDate;
      }

      this.$store
        .dispatch("GET_DASHBOARD_SCORECARD", params)
        .then((result) => {})
        .catch((err) => {});
    },
  },
  mounted() {
    this.get_fleet_data();
    this.get_order_graph_data();
    this.get_dashboard_scorecard();
  },
};
</script>

<style scoped>
.loader-container {
  height: 400px;
}
</style>
