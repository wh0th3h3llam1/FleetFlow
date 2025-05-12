<template>
  <v-dialog v-model="openFailedInfoDialog" scrollable width="80%">
    <v-card>
      <v-card-title
        class="background-primary text-white px-3 py-2"
        v-if="planinformation"
      >
        <span class="text-subtitle-2 text-uppercase">
          Plan Information &nbsp;&nbsp;</span
        >

        <span
          class="text-subtitle-1"
          v-if="
            planinformation &&
            planinformation.plan_name &&
            planinformation.planning_template_data &&
            planinformation.planning_template_data.template_name
          "
        >
          ( &nbsp; {{ planinformation.plan_name }} - {{ planinformation.planning_template_data.template_name }}
          &nbsp; )
        </span>

        <v-spacer></v-spacer>
        <v-btn
          depressed
          color="white"
          icon
          small
          @click="openFailedInfoDialog = false"
        >
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>
      <v-card-text class="overflow-x-hidden pa-0" v-if="planinformation">
        <v-row no-gutters class="pt-8 pr-12 text">
          <v-col cols="9"></v-col>
          <v-col cols="2">
            <v-select
              v-model="exportSelection"
              outlined
              dense
              label="Export"
              :items="exportOptions"
              class="background-white"
            ></v-select>
          </v-col>
          <v-col cols="1" class="text-right">
            <v-btn class="text-uppercase primary" @click="exportExcel()"
              >
              <v-icon>
                mdi-microsoft-excel
              </v-icon>
              Export
              </v-btn>
          </v-col>
        </v-row>
        <v-row no-gutters class="pb-8">
          <v-col cols="12">
            <v-row no-gutters justify="center" class="simple-title pt-6 mt-4">
              <v-col cols="2">
                <v-card
                  elevation="0"
                  class="border-x-light_grey border-bottom-light_grey mr-3"
                >
                  <v-card-title
                    class="
                      light_grey
                      px-4
                      py-1
                      d-flex
                      align-center
                      justify-center
                    "
                  >
                    <h6>planned orders</h6>
                  </v-card-title>
                  <v-card-text class="text-center py-6">
                    <span v-if="planinformation.planned_orders">
                      {{ planinformation.planned_orders }}
                    </span>
                    <span v-else> 0 </span>
                  </v-card-text>
                </v-card>
              </v-col>
              <v-col cols="2">
                <v-card
                  elevation="0"
                  class="border-x-light_grey border-bottom-light_grey mr-3"
                >
                  <v-card-title
                    class="
                      light_grey
                      px-4
                      py-1
                      d-flex
                      align-center
                      justify-center
                    "
                  >
                    <h6>Total Orders</h6>
                  </v-card-title>
                  <v-card-text class="pa-0 text-center py-6">
                    <span v-if="planinformation.total_orders">
                      {{ planinformation.total_orders }}
                    </span>
                  </v-card-text>
                </v-card>
              </v-col>
              <v-col cols="2">
                <v-card
                  elevation="0"
                  class="border-x-light_grey border-bottom-light_grey mr-3"
                >
                  <v-card-title
                    class="
                      light_grey
                      px-4
                      py-1
                      d-flex
                      align-center
                      justify-center
                    "
                  >
                    <h6>Unplanned Orders</h6>
                  </v-card-title>
                  <v-card-text class="pa-0 text-center py-6">
                    <span v-if="planinformation.unplanned_orders">
                      {{ planinformation.unplanned_orders }}
                    </span>
                    <span v-else> 0 </span>
                  </v-card-text>
                </v-card>
              </v-col>
              <v-col cols="2">
                <v-card
                  elevation="0"
                  class="border-x-light_grey border-bottom-light_grey mr-3"
                >
                  <v-card-title
                    class="
                      light_grey
                      px-4
                      py-1
                      d-flex
                      align-center
                      justify-center
                    "
                  >
                    <h6>Unused Drivers</h6>
                  </v-card-title>
                  <v-card-text class="pa-0 text-center py-6">
                    <span v-if="planinformation.unused_drivers">
                      {{ planinformation.unused_drivers }}
                    </span>
                    <span v-else> 0 </span>
                  </v-card-text>
                </v-card>
              </v-col>
              <v-col cols="2">
                <v-card
                  elevation="0"
                  class="border-x-light_grey border-bottom-light_grey mr-3"
                >
                  <v-card-title
                    class="
                      light_grey
                      px-4
                      py-1
                      d-flex
                      align-center
                      justify-center
                    "
                  >
                    <h6>Utilized Drivers</h6>
                  </v-card-title>
                  <v-card-text class="pa-0 text-center py-6">
                    <span v-if="planinformation.utilized_drivers">
                      {{ planinformation.utilized_drivers }}
                    </span>
                    <span v-else> 0 </span>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
          </v-col>
        </v-row>

        <v-row class="px-12 pb-12">
          <v-col cols="5">
            <v-row>
              <v-col cols="12 mb-6">
                <h2 class="text-black">Status Information</h2>
                <hr class="bg-light_black mt-6" style="opacity: 0.4" />
              </v-col>
              <v-col
                cols="4"
                class="
                  light_grey
                  border-x-light_grey
                  border-y-light_grey
                  text-center
                "
              >
                <span class="text-subtitle-1 text-primary"> Status </span>
              </v-col>
              <v-col
                cols="8"
                class="
                  light_grey
                  border-x-light_grey
                  border-y-light_grey
                  text-center
                "
              >
                <span class="text-subtitle-1 text-primary">Date and Time </span>
              </v-col>
            </v-row>
            <v-row v-for="(status, i) in planinformation.trip_events" :key="i">
              <v-col
                cols="4"
                class="border-x-light_grey border-y-light_grey text-center"
              >
                <span class="text-subtitle-2 text-ligth_grey">
                  {{ Object.keys(status)[0].toString().replace("_", " ") }}
                </span>
              </v-col>
              <v-col
                cols="8"
                class="border-x-light_grey border-y-light_grey text-center"
              >
                <span class="text-subtitle-2 text-ligth_grey">
                  {{ Object.values(status)[0] }}
                </span>
              </v-col>
            </v-row>
          </v-col>
          <v-col cols="1"></v-col>
          <v-col cols="6">
            <v-row>
              <v-col cols="12 mb-6">
                <h2 class="text-black">Loading / Offloading time</h2>
                <hr class="bg-light_black mt-6" style="opacity: 0.4" />
              </v-col>
              <v-col
                cols="3"
                class="
                  light_grey
                  border-x-light_grey
                  border-y-light_grey
                  text-center
                "
              >
                <span class="text-subtitle-1 text-primary"> Name </span>
              </v-col>
              <v-col
                cols="3"
                class="
                  light_grey
                  border-x-light_grey
                  border-y-light_grey
                  text-center
                "
              >
                <span class="text-subtitle-1 text-primary"> Start Time </span>
              </v-col>
              <v-col
                cols="3"
                class="
                  light_grey
                  border-x-light_grey
                  border-y-light_grey
                  text-center
                "
              >
                <span class="text-subtitle-1 text-primary"> End Time </span>
              </v-col>
              <v-col
                cols="3"
                class="
                  light_grey
                  border-x-light_grey
                  border-y-light_grey
                  text-center
                "
              >
                <span class="text-subtitle-1 text-primary">Time (In Minutes) </span>
              </v-col>
            </v-row>
            <v-row>
              <v-col
                cols="3"
                class="border-x-light_grey border-y-light_grey text-center"
              >
                <span class="text-subtitle-2 text-ligth_grey">
                  Loading Time
                </span>
              </v-col>
              <v-col
                cols="3"
                class="border-x-light_grey border-y-light_grey text-center"
              >
                <span
                  class="text-subtitle-2 text-ligth_grey"
                  v-if="
                    planinformation.planning_template_data &&
                    planinformation.planning_template_data.loading_time &&
                    planinformation.planning_template_data.loading_time
                      .start_time
                  "
                >
                  {{
                    planinformation.planning_template_data.loading_time
                      .start_time
                  }}
                </span>
              </v-col>
              <v-col
                cols="3"
                class="border-x-light_grey border-y-light_grey text-center"
                v-if="
                  planinformation.planning_template_data &&
                  planinformation.planning_template_data.loading_time &&
                  planinformation.planning_template_data.loading_time.start_time
                "
              >
                <span class="text-subtitle-2 text-ligth_grey">
                  {{
                    planinformation.planning_template_data.loading_time.end_time
                  }}
                </span>
              </v-col>
              <v-col
                cols="3"
                class="border-x-light_grey border-y-light_grey text-center"
                v-if="
                  planinformation.planning_template_data &&
                  planinformation.planning_template_data.loading_time &&
                  planinformation.planning_template_data.loading_time.time_in_minutes
                "
              >
                <span class="text-subtitle-2 text-ligth_grey">
                  {{
                    planinformation.planning_template_data.loading_time.time_in_minutes
                  }}
                </span>
              </v-col>
              <v-col
                cols="3"
                class="border-x-light_grey border-y-light_grey text-center"
              >
                <span class="text-subtitle-2 text-ligth_grey">
                  OffLoading Time
                </span>
              </v-col>
              <v-col
                cols="3"
                class="border-x-light_grey border-y-light_grey text-center"
              >
                <span
                  class="text-subtitle-2 text-ligth_grey"
                  v-if="
                    planinformation.planning_template_data &&
                    planinformation.planning_template_data.offloading_time &&
                    planinformation.planning_template_data.offloading_time
                      .start_time
                  "
                >
                  {{
                    planinformation.planning_template_data.offloading_time
                      .start_time
                  }}
                </span>
              </v-col>
              <v-col
                cols="3"
                class="border-x-light_grey border-y-light_grey text-center"
                v-if="
                  planinformation.planning_template_data &&
                  planinformation.planning_template_data.offloading_time &&
                  planinformation.planning_template_data.offloading_time
                    .end_time
                "
              >
                <span class="text-subtitle-2 text-ligth_grey">
                  {{
                    planinformation.planning_template_data.offloading_time
                      .end_time
                  }}
                </span>
              </v-col>
              <v-col
                cols="3"
                class="border-x-light_grey border-y-light_grey text-center"
                v-if="
                  planinformation.planning_template_data &&
                  planinformation.planning_template_data.offloading_time &&
                  planinformation.planning_template_data.offloading_time
                    .time_in_minutes
                "
              >
                <span class="text-subtitle-2 text-ligth_grey">
                  {{
                    planinformation.planning_template_data.offloading_time
                      .time_in_minutes
                  }}
                </span>
              </v-col>
            </v-row>
          </v-col>
        </v-row>

        <v-row
          class="px-12 mb-12"
          v-if="planinformation.planning_template_data"
        >
          <v-col cols="6">
            <v-row>
              <v-col cols="4">
                <span class="text-subtitle-2 text-ligth_grey">
                  Round Trip
                </span>
              </v-col>
              <v-col cols="6">
                <v-icon
                  v-if="planinformation.planning_template_data.round_trip"
                  class="text-light_green"
                  >mdi-check-circle</v-icon
                >
                <v-icon v-else class="text-light_red">mdi-close-circle</v-icon>
              </v-col>
              <v-col cols="4">
                <span class="text-subtitle-2 text-ligth_grey">
                  Tag Validations
                </span>
              </v-col>
              <v-col cols="6">
                <v-icon
                  v-if="
                    planinformation.planning_template_data.tag_validations
                  "
                  class="text-light_green"
                  >mdi-check-circle</v-icon
                >
                <v-icon v-else class="text-light_red">mdi-close-circle</v-icon>
              </v-col>
              <v-col cols="4">
                <span class="text-subtitle-2 text-ligth_grey">
                  Zone Constraint
                </span>
              </v-col>
              <v-col cols="6">
                <v-icon
                  v-if="planinformation.planning_template_data.zone_constraint"
                  class="text-light_green"
                  >mdi-check-circle</v-icon
                >
                <v-icon v-else class="text-light_red">mdi-close-circle</v-icon>
              </v-col>
              <v-col cols="4">
                <span class="text-subtitle-2 text-ligth_grey">
                  Disabled Time Windows
                </span>
              </v-col>
              <v-col cols="6">
                <v-icon
                  v-if="planinformation.planning_template_data.disable_time_windows"
                  class="text-light_green"
                  >mdi-check-circle</v-icon
                >
                <v-icon v-else class="text-light_red">mdi-close-circle</v-icon>
              </v-col>
            </v-row>
          </v-col>

          <v-col cols="6">
            <v-row>
              <v-col cols="4">
                <span class="text-subtitle-2 text-ligth_grey">
                  Template Name
                </span>
              </v-col>
              <v-col cols="6">
                <span>
                  {{ planinformation.planning_template_data.template_name }}
                </span>
              </v-col>
              <v-col cols="4">
                <span class="text-subtitle-2 text-ligth_grey">
                  Optimization Option
                </span>
              </v-col>
              <v-col cols="6">
                <span>
                  {{ planinformation.planning_template_data.configuration | titlecase }}
                </span>
              </v-col>
              <v-col cols="4">
                <span class="text-subtitle-2 text-ligth_grey">
                  Fill Ratio
                </span>
              </v-col>
              <v-col cols="6">
                <span>
                  {{ planinformation.planning_template_data.fill_ratio }} %
                </span>
              </v-col>
            </v-row>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>


<script>
import XLSX from "xlsx";
import PieChart from "@/components/common/charts/PieChart.vue";
import { downloadBlobData } from "~/assets/utils";
export default {
  data() {
    return {
      options: {
        responsive: true,
        legend: {
          display: true,
          position: "right",
        },
      },
      exportOptions: [
        "Plan Summary",
        "Unassigned Orders"
      ],
      exportSelection: "Plan Summary"
    };
  },
  components: {
    PieChart,
  },
  props: {
    value: Boolean,
    info: Object,
  },
  methods: {
    planInformationExport() {
      this.$store
        .dispatch("trip_planning/GET_PLAN_SUMMARY", this.planinformation.id)
        .then((response) => {
          let newData = [];
          response.trip_plan_summary.summary.forEach((element) => {
            newData.push({
              'Drivers':  element.drivers ,
              'Vehicles': element.vehicles,
              'Zone': element.zone,
              'Orders': element.orders,
              'Total Cases': element.total_cases,
              'Boxes': element.boxes,
              'Frozen': element.frozen,
              'Chilled': element.chilled,
              'Dry': element.dry,
              'Rejected Orders': element.rejected_orders,
              'Trip Duration': element.trip_duration,
              'Working Time': element.working_time,
              'Driving Time': element.driving_time,
              'Planned Start Time': element.planned_start_time,
              'Planned End Time': element.planned_end_time,
              'Distance': element.distance,
              'Tonnage Utilization': element.tonnage_utilization,
              'Volume Utilization': element.volume_utilization
            });
          });
          const data = XLSX.utils.json_to_sheet(newData);
          const wb = XLSX.utils.book_new();
          wb.Props = {
            Title: " Trip Plan information excel sheet",
            Subject: "Plan Inforamation",
            Author: "chefme",
            CreatedDate: new Date(),
          };

          XLSX.utils.book_append_sheet(wb, data, "data");
          XLSX.writeFile(wb, `${response.trip_plan_summary.plan_name}.xlsx`);
        });
    },
    exportExcel() {
      if(this.exportSelection == "Plan Summary") {
        this.downloadSummary();
      } else {
        this.downloadUnplannedReasons();
      }
    },
    downloadSummary() {
      this.$store
        .dispatch("trip_planning/GET_PLAN_SUMMARY", this.planinformation.id)
        .then((response) => {
          let file_name = "Trip Plan"
          if (this.planinformation.plan_name) {
            file_name = this.planinformation.plan_name
          }
         downloadBlobData(response, `${file_name} Summary.xls`);
        }
      )
    },
    downloadUnplannedReasons() {
      this.$store
        .dispatch("trip_planning/GET_UNPLANNED_ORDER_REASONS", this.planinformation.id)
        .then((response) => {
          let file_name = "Trip Plan"
          if (this.planinformation.plan_name) {
            file_name = this.planinformation.plan_name
          }
         downloadBlobData(response, `${file_name} Unassigned Order Reasons.xls`);
        }
      )
    },
  },
  mounted() {},
  computed: {
    openFailedInfoDialog: {
      get() {
        return this.value;
      },
      set(value) {
        this.$emit("input", value);
      },
    },
    planinformation: {
      get() {
        return this.$store.state.trip_planning.planinfo;
      },
      set(value) {
        this.$store.dispatch("trip_planning/GET_PLAN_INFORMATION", value);
      },
    },
  },
  filters: {
    titlecase: function (text) {
      try {
        let string = text.replaceAll("_", " ").replaceAll("-", " ");
        return string.replace(/(^|\s)\S/g, function(t) { return t.toUpperCase() });
      }
      catch(TypeError) {
        return text
      }
    }
  }
};
</script>

<style scoped lang="scss">
@import "@/assets/scss/variables.scss";
.simple-title h6 {
  font-size: 14px;
  text-transform: uppercase !important;
  color: black;
}
.simple-title span {
  font-size: 49px;
  font-weight: 900;
  color: map-get($colors-custom, "solid", "primary");
}
</style>
