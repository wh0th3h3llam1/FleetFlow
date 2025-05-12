<template>
  <div style="height: 92vh; display: flex; flex-direction: column">
    <v-card-title
      class="dark_solo_grey"
      :class="tripStatusDarkColor(currentTrip.status)"
    >
      <div style="width: 100%">
        <div class="d-flex justify-space-between" style="width: 100%">
          <h5
            class="
              text-caption text-lg-body-1
              font-weight-bold
              text-uppercase
              white--text
            "
          >
            <v-tooltip top>
              <template v-slot:activator="{ on, attrs }">
                <span v-on="on" v-bind="attrs">
                  {{ currentTrip.reference_number }}
                </span>
              </template>
              <span>Trip Reference Number</span>
            </v-tooltip>
          </h5>
          <h5
            class="
              text-caption text-lg-body-1
              font-weight-bold
              text-uppercase
              white--text
            "
          >
            <v-tooltip top>
              <template v-slot:activator="{ on, attrs }">
                <span class="text-capitalize" v-on="on" v-bind="attrs">
                  {{ currentTrip.status }}
                </span>
              </template>
              <span>Trip Status</span>
            </v-tooltip>
          </h5>
        </div>
        <div class="d-flex justify-space-between" style="width: 100%">
          <h5
            v-if="currentTrip.trip_date"
            class="
              text-caption text-lg-body-1
              font-weight-normal
              text-uppercase
              white--text
            "
          >
            <v-tooltip top>
              <template v-slot:activator="{ on, attrs }">
                <span small v-bind="attrs" v-on="on">
                  {{ currentTrip.trip_date }}
                </span>
              </template>
              <span>Last Trip updated on</span>
            </v-tooltip>
          </h5>

          <h5
            class="
              text-caption text-lg-body-1
              font-weight-normal
              text-uppercase
              white--text
            "
            v-if="currentTrip.project_name"
          >
            <v-tooltip top>
              <template v-slot:activator="{ on, attrs }">
                <span small v-on="on" v-bind="attrs">
                  {{ currentTrip.project_name }}
                </span>
              </template>
              <span>Project Name</span>
            </v-tooltip>
          </h5>
        </div>
      </div>
    </v-card-title>

    <v-card-text
      class="px-0 overflow-y-auto"
      style="position: relative"
      id="tripdetails"
    >
      <div
        :class="tripStatusLightColor(currentTrip.status)"
        class="d-flex justify-space-between py-5 px-3"
        style="position: sticky; top: 0; z-index: 3"
      >
        <div class="d-flex justify-start">
          <v-tooltip bottom>
            <template v-slot:activator="{ on, attrs }">
              <v-btn
                depressed
                :class="`${tripStatusDarkColor(currentTrip.statusc)}--text`"
                class="py-3 mr-2"
                small
                v-show="
                  currentTrip.status == 'completed' &&
                  currentTrip.pod_attachments.length !== 0
                "
                v-bind="attrs"
                v-on="on"
                @click="openTripAttachmentDialog = true"
              >
                POD
              </v-btn>
            </template>
            <span>Print Preview of Trip Attachments</span>
          </v-tooltip>
        </div>
        <div class="d-flex align-center">
          <v-tooltip bottom>
            <template v-slot:activator="{ on, attrs }">
              <v-btn
                depressed
                :class="`${tripStatusDarkColor(currentTrip.status)}--text`"
                class="py-3 mr-2"
                v-show="
                  (currentTrip.status == 'scheduled' ||
                    currentTrip.status == 'active') &&
                  userPermissions.trip &&
                  userPermissions.trip.change
                "
                small
                v-bind="attrs"
                v-on="on"
                @click="editTrip(currentTrip)"
              >
                <v-icon small>mdi-pencil</v-icon>
              </v-btn>
            </template>
            <span>Edit Trip</span>
          </v-tooltip>

          <v-tooltip bottom>
            <template v-slot:activator="{ on, attrs }">
              <v-btn
                depressed
                :class="`${tripStatusDarkColor(currentTrip.status)}--text`"
                class="py-3 mr-2"
                small
                @click="openLoadSheetDialog(currentTrip.id)"
                v-bind="attrs"
                v-on="on"
              >
                <v-icon small> mdi-microsoft-excel </v-icon>
              </v-btn>
            </template>
            <span>Download Excel Trip Load Sheet</span>
          </v-tooltip>

          <v-tooltip bottom>
            <template v-slot:activator="{ on, attrs }">
              <v-btn
                depressed
                :class="`${tripStatusDarkColor(currentTrip.status)}--text`"
                class="py-3"
                small
                @click="openTripSheetDialog(currentTrip.id)"
                v-bind="attrs"
                v-on="on"
              >
                <v-icon small class="red--text"> mdi-file-pdf-box </v-icon>
              </v-btn>
            </template>
            <span>Print Preview of trip PDF</span>
          </v-tooltip>
        </div>
      </div>

      <!-------------------------- Driver Details -------------------------------->

      <v-row no-gutters class="py-3">
        <v-col cols="12">
          <v-row no-gutters class="px-4">
            <v-col cols="12" class="d-flex justify-space-between">
              <h5
                class="
                  text-caption text-lg-body-1
                  font-weight-bold
                  text-uppercase
                "
              >
                <v-tooltip bottom>
                  <template v-slot:activator="{ on, attrs }">
                    <span small v-bind="attrs" v-on="on" class="d-flex mr-2">
                      <v-icon
                        class="mr-5"
                        :color="tripStatusDarkColor(currentTrip.status)"
                      >
                        mdi-truck-fast
                      </v-icon>
                      <span> {{ currentTrip.driver }}</span>
                    </span>
                  </template>
                  <span>Trip Driver</span>
                </v-tooltip>
              </h5>
              <h5
                class="
                  text-caption text-lg-body-1
                  font-weight-bold
                  text-uppercase
                "
              >
                <v-tooltip bottom>
                  <template v-slot:activator="{ on, attrs }">
                    <span small v-bind="attrs" v-on="on">
                      {{ currentTrip.driver_number }}
                    </span>
                  </template>
                  <span>Driver Contact Number</span>
                </v-tooltip>
              </h5>
            </v-col>
            <v-col cols="12" class="d-flex justify-space-between">
              <v-tooltip bottom>
                <template v-slot:activator="{ on, attrs }">
                  <span
                    small
                    v-bind="attrs"
                    v-on="on"
                    class="pl-12 text-caption text-lg-body-1"
                  >
                    {{ currentTrip.vehicle_info.vehicle_plate_no }}
                  </span>
                </template>
                <span>Vehicle Assigned</span>
              </v-tooltip>
              <v-tooltip bottom>
                <template v-slot:activator="{ on, attrs }">
                  <span
                    small
                    v-bind="attrs"
                    v-on="on"
                    class="pl-12 text-caption text-lg-body-1"
                  >
                    {{ currentTrip.helper_name }}
                  </span>
                </template>
                <span>Helper Name</span>
              </v-tooltip>
            </v-col>
          </v-row>
        </v-col>
      </v-row>

      <v-row no-gutters class="px-4 mt-4">
        <v-col cols="12">
          <v-card outlined class="mr-2 pa-0">
            <div class="d-flex" outlined>
              <v-card-title
                class="light_grey py-1 pl-6 pr-1"
                style="width: 100%"
              >
                <span class="text-caption"> Delivered </span>
              </v-card-title>
              <v-card-text class="py-2 text-center" style="width: 100%">
                <span class="cf-info-title font-weight-bold">
                  {{ currentTrip.order_count.successful }}
                </span>
              </v-card-text>
            </div>
          </v-card>
          <v-card outlined class="mr-2 pa-0">
            <div class="d-flex">
              <v-card-title
                class="light_grey py-1 pl-6 pr-1"
                style="width: 100%"
              >
                <span class="text-caption"> Partially Delivered </span>
              </v-card-title>
              <v-card-text class="py-2 text-center" style="width: 100%">
                <span class="cf-info-title font-weight-bold">
                  {{ currentTrip.order_count.partially_delivered }}
                </span>
              </v-card-text>
            </div>
          </v-card>
          <v-card outlined class="mr-2 pa-0">
            <div class="d-flex">
              <v-card-title
                class="light_grey py-1 pl-6 pr-1"
                style="width: 100%"
              >
                <span class="text-caption"> Returned </span>
              </v-card-title>
              <v-card-text class="py-2 text-center" style="width: 100%">
                <span class="cf-info-title font-weight-bold">
                  {{ currentTrip.order_count.failed }}
                </span>
              </v-card-text>
            </div>
          </v-card>
          <v-card outlined class="mr-2 pa-0">
            <div class="d-flex">
              <v-card-title
                class="light_grey py-1 pl-6 pr-1"
                style="width: 100%"
              >
                <span class="text-caption"> Total </span>
              </v-card-title>
              <v-card-text class="py-2 text-center" style="width: 100%">
                <span class="cf-info-title font-weight-bold">
                  {{ currentTrip.order_count.total }}
                </span>
              </v-card-text>
            </div>
          </v-card>
        </v-col>
      </v-row>

      <!---------------- Trip Time ----------------------------------------------------------->

      <v-row
        no-gutters
        class="px-4 mt-4"
        v-if="currentTrip.trip_start && currentTrip.trip_end"
      >
        <v-col cols="6">
          <v-card outlined class="mr-2 pa-0" style="height: 100%">
            <v-card-title class="light_grey pa-1 d-flex justify-center">
              <span class="cf-info-title font-weight-bold" style="opacity: 0.7">
                Trip Start Time
              </span>
            </v-card-title>
            <v-card-text class="py-2 text-center">
              <span class="text-caption">
                {{ currentTrip.trip_start }}
              </span>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="6">
          <v-card outlined class="ml-2 pa-0" style="height: 100%">
            <v-card-title class="light_grey pa-1 d-flex justify-center">
              <span class="cf-info-title font-weight-bold" style="opacity: 0.7">
                Trip End Time
              </span>
            </v-card-title>
            <v-card-text class="py-2 text-center">
              <span class="text-caption">
                {{ currentTrip.trip_end }}
              </span>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!---------------- Trip Details ----------------------------------------------------------->

      <v-card outlined class="mx-4 mt-3">
        <v-card-title
          class="light_grey px-4 py-1 d-flex justify-space-between align-center"
        >
          <span
            class="cf-info-title font-weight-bold text-uppercase"
            style="opacity: 0.7"
          >
            Trip Details
          </span>

          <v-btn
            small
            dark
            style="font-size: 11px"
            :class="`${tripStatusDarkColor(currentTrip.status)}`"
            elevation="0"
            @click="showOrderListDialog = true"
            >View Orders</v-btn
          >
        </v-card-title>
        <v-card-text>
          <v-row no-gutters class="pt-4">
            <v-col
              cols="6"
              class="d-flex justify-end text-right py-1"
              v-if="currentTrip.total_item_quantity"
            >
              <span class="cf-info-title font-weight-bold">
                {{ currentTrip.total_item_quantity }}
              </span>
            </v-col>
            <v-col cols="6" class="py-1" v-if="currentTrip.planned_distance">
              <span class="cf-info-title font-weight-regular"
                >Planned Trip Distance
              </span>
            </v-col>
            <v-col
              cols="6"
              class="d-flex justify-end text-right py-1"
              v-if="currentTrip.planned_distance"
            >
              <span class="cf-info-title font-weight-bold">
                {{ currentTrip.planned_distance }} Km
              </span>
            </v-col>
            <v-col cols="6" class="py-1" v-if="currentTrip.trip_start_km">
              <span class="cf-info-title font-weight-regular"
                >Starting Vehicle KM
              </span>
            </v-col>
            <v-col
              cols="6"
              class="d-flex justify-end text-right py-1"
              v-if="currentTrip.trip_start_km"
            >
              <span class="cf-info-title font-weight-bold">
                {{ currentTrip.trip_start_km }}
              </span>
            </v-col>
            <v-col cols="6" class="py-1" v-if="currentTrip.trip_end_km">
              <span class="cf-info-title font-weight-regular"
                >Ending Vehicle KM
              </span>
            </v-col>
            <v-col
              cols="6"
              class="d-flex justify-end text-right py-1"
              v-if="currentTrip.trip_end_km"
            >
              <span class="cf-info-title font-weight-bold">
                {{ currentTrip.trip_end_km }}
              </span>
            </v-col>
            <v-col
              cols="6"
              class="py-1"
              v-if="
                currentTrip.actual_distance &&
                currentTrip.trip_start_km &&
                currentTrip.trip_end_km
              "
            >
              <span class="cf-info-title font-weight-regular"
                >Actual Trip Distance
              </span>
            </v-col>
            <v-col
              cols="6"
              class="d-flex justify-end text-right py-1"
              v-if="
                currentTrip.actual_distance &&
                currentTrip.trip_start_km &&
                currentTrip.trip_end_km
              "
            >
              <span class="cf-info-title font-weight-bold">
                {{ currentTrip.actual_distance }} Km
              </span>
            </v-col>
            <v-col
              cols="6"
              class="py-1"
              v-if="currentTrip.planned_trip_duration"
            >
              <span class="cf-info-title font-weight-regular"
                >Planned Trip Duration
              </span>
            </v-col>
            <v-col
              cols="6"
              class="d-flex justify-end text-right py-1"
              v-if="currentTrip.planned_trip_duration"
            >
              <span class="cf-info-title font-weight-bold">
                {{ currentTrip.planned_trip_duration }}
              </span>
            </v-col>
            <v-col
              cols="6"
              class="py-1"
              v-if="currentTrip.actual_trip_duration"
            >
              <span class="cf-info-title font-weight-regular">
                Actual Trip Duration
              </span>
            </v-col>
            <v-col
              cols="6"
              class="d-flex justify-end text-right py-1"
              v-if="currentTrip.actual_trip_duration"
            >
              <span class="cf-info-title font-weight-bold">
                {{ currentTrip.actual_trip_duration }}
              </span>
            </v-col>
            <v-col
              cols="6"
              class="py-1"
              v-if="currentTrip.trip_statistics.total_items"
            >
              <span class="cf-info-title font-weight-regular">
                Total Items
              </span>
            </v-col>
            <v-col
              cols="6"
              class="d-flex justify-end text-right py-1"
              v-if="currentTrip.trip_statistics.total_items"
            >
              <span class="cf-info-title font-weight-bold">
                {{ currentTrip.trip_statistics.total_items }}
              </span>
            </v-col>
          </v-row>
          <v-card
            class="mt-3 elevation-0"
            v-if="
              currentTrip.status === 'completed' &&
              currentTrip.trip_statistics.timings &&
              (currentTrip.trip_statistics.timings.break_time ||
                currentTrip.trip_statistics.timings.processing_time ||
                currentTrip.trip_statistics.timings.travelling_time)
            "
          >
            <v-card-text class="pa-lg-12">
              <PieChart
                v-if="reloadChart"
                :data="{
                  labels: ['Break Time', 'Processing Time', 'Travelling Time'],
                  datasets: [
                    {
                      backgroundColor: ['#607d8b', '#c6c6c6', '#90a4ae'],
                      data: [
                        currentTrip.trip_statistics.timings.break_time,
                        currentTrip.trip_statistics.timings.processing_time,
                        currentTrip.trip_statistics.timings.travelling_time,
                      ],
                    },
                  ],
                }"
                :options="options2"
                :height="320"
              />
            </v-card-text>
          </v-card>
        </v-card-text>
      </v-card>

      <!---------------- Vehicle Information ----------------------------------------------------------->

      <v-card outlined class="mx-4 mt-3">
        <v-card-title class="light_grey px-4 py-1 d-flex justify-space-between">
          <span
            class="cf-info-title font-weight-bold text-uppercase"
            style="opacity: 0.7"
          >
            Vehicle Details
          </span>

          <v-btn
            v-if="currentTrip.status == 'completed'"
            small
            :class="`${tripStatusDarkColor(currentTrip.status)}`"
            class="mr-2 white--text"
            elevation="0"
            @click="getTempratureData(currentTrip.id)"
            >temperature data</v-btn
          >
        </v-card-title>
        <v-card-text>
          <v-row no-gutters class="pt-4">
            <v-col cols="6" class="py-1" v-if="currentTrip.vehicle_info">
              <span class="cf-info-title font-weight-regular"
                >Vehicle No</span
              ></v-col
            >
            <v-col
              cols="6"
              class="d-flex justify-end py-1"
              v-if="currentTrip.vehicle_info.vehicle_plate_no"
            >
              <span class="cf-info-title font-weight-bold">
                {{ currentTrip.vehicle_info.vehicle_plate_no }}
              </span>
            </v-col>
            <v-col
              cols="6"
              class="py-1"
              v-if="currentTrip.vehicle_info.vehicle_cost"
            >
              <span class="cf-info-title font-weight-regular"
                >Vehicle Cost</span
              ></v-col
            >
            <v-col
              cols="6"
              class="d-flex justify-end py-1"
              v-if="currentTrip.vehicle_cost"
            >
              <span class="cf-info-title font-weight-bold">
                {{ currentTrip.vehicle_cost }}
              </span>
            </v-col>
            <v-col
              cols="6"
              class="py-1"
              v-if="currentTrip.vehicle_info.vehicle_make"
            >
              <span class="cf-info-title font-weight-regular"
                >Vehicle Make</span
              ></v-col
            >
            <v-col
              cols="6"
              class="d-flex justify-end py-1"
              v-if="currentTrip.vehicle_info.vehicle_make"
            >
              <span class="cf-info-title font-weight-bold">
                {{ currentTrip.vehicle_info.vehicle_make }}
              </span>
            </v-col>
            <v-col
              cols="6"
              class="py-1"
              v-if="currentTrip.vehicle_info.vehicle_model"
            >
              <span class="cf-info-title font-weight-regular"
                >Vehicle Model</span
              ></v-col
            >
            <v-col
              cols="6"
              class="d-flex justify-end py-1"
              v-if="currentTrip.vehicle_info.vehicle_model"
            >
              <span class="cf-info-title font-weight-bold">
                {{ currentTrip.vehicle_info.vehicle_model }}
              </span>
            </v-col>
            <v-col
              cols="6"
              class="py-1"
              v-if="currentTrip.vehicle_info.cbm_capacity"
            >
              <span class="cf-info-title font-weight-regular"
                >Vehicle CBM capacity</span
              ></v-col
            >
            <v-col
              cols="6"
              class="d-flex justify-end py-1"
              v-if="currentTrip.vehicle_info.cbm_capacity"
            >
              <span class="cf-info-title font-weight-bold">
                {{ currentTrip.vehicle_info.cbm_capacity }}
              </span>
            </v-col>
            <v-col
              cols="6"
              class="py-1"
              v-if="currentTrip.vehicle_info.tonnage_capacity"
            >
              <span class="cf-info-title font-weight-regular"
                >Tonnage Capacity</span
              ></v-col
            >
            <v-col
              cols="6"
              class="d-flex justify-end py-1"
              v-if="currentTrip.vehicle_info.tonnage_capacity"
            >
              <span class="cf-info-title font-weight-bold">
                {{ currentTrip.vehicle_info.tonnage_capacity }}
              </span>
            </v-col>
            <v-col
              cols="6"
              class="py-1"
              v-if="currentTrip.trip_statistics.tonnage_utilization"
            >
              <span class="cf-info-title font-weight-regular">
                Tonnage Utilization
              </span>
            </v-col>
            <v-col
              cols="6"
              class="d-flex justify-end text-right py-1"
              v-if="currentTrip.trip_statistics.tonnage_utilization"
            >
              <span class="cf-info-title font-weight-bold">
                {{ currentTrip.trip_statistics.tonnage_utilization }} %
              </span>
            </v-col>
            <v-col
              cols="6"
              class="py-1"
              v-if="currentTrip.trip_statistics.volume_utilization"
            >
              <span class="cf-info-title font-weight-regular">
                Volume Utilization
              </span>
            </v-col>
            <v-col
              cols="6"
              class="d-flex justify-end text-right py-1"
              v-if="currentTrip.trip_statistics.volume_utilization"
            >
              <span class="cf-info-title font-weight-bold">
                {{ currentTrip.trip_statistics.volume_utilization }} %
              </span>
            </v-col>
          </v-row>

          <v-card
            class="mt-3"
            elevation="0"
            v-if="
              currentTrip.trip_statistics.partitions &&
              (currentTrip.trip_statistics.partitions.chilled ||
                currentTrip.trip_statistics.partitions.dry ||
                currentTrip.trip_statistics.partitions.frozen)
            "
          >
            <v-card-title class="py-1 px-0">
              <span
                class="cf-info-title font-weight-bold text-uppercase"
                style="opacity: 0.7"
              >
                Truck Fill Ratio
              </span>
            </v-card-title>
            <v-card-text class="pa-lg-12">
              <PieChart
                v-if="reloadChart"
                :data="{
                  labels: [`Chilled`, 'Dry', 'Frozen'],
                  datasets: [
                    {
                      backgroundColor: ['#50b7d0', '#ee872c', '#d16bc8'],
                      data: [
                        currentTrip.trip_statistics.partitions.chilled,
                        currentTrip.trip_statistics.partitions.dry,
                        currentTrip.trip_statistics.partitions.frozen,
                      ],
                    },
                  ],
                }"
                :options="options"
                :height="320"
              />
            </v-card-text>
          </v-card>
        </v-card-text>
      </v-card>

      <!---------------- Chart ----------------------------------------------------------->
      <v-card
        id="triplogs"
        outlined
        class="mx-4 mt-3"
        v-if="currentTrip.logs && currentTrip.logs.length"
      >
        <v-card-title class="light_grey px-4 py-1 d-flex justify-space-between">
          <span
            class="cf-info-title font-weight-bold text-uppercase"
            style="opacity: 0.7"
            >logs</span
          >
          <v-btn
            small
            dark
            :class="tripStatusDarkColor(currentTrip.status)"
            elevation="0"
            @click="showLogs = !showLogs"
          >
            View Logs
          </v-btn>
        </v-card-title>
        <v-card-text class="pa-0">
          <v-row no-gutters class="px-0 px-lg-2">
            <v-col cols="12" v-if="showLogs">
              <v-timeline dense>
                <v-timeline-item
                  small
                  v-for="(log, index) in currentTrip.logs"
                  :key="index"
                  class="ma-0 pa-0"
                  :color="tripStatusDarkColor(currentTrip.status)"
                >
                  <v-card class="elevation-0 pa-lg-3" outlined>
                    <v-card-text class="pt-1">
                      <v-row>
                        <v-col class="ma-0 pb-0" cols="12" lg="6">
                          <span
                            :class="`${tripStatusDarkColor(log.status)}--text`"
                            class="text-caption font-weight-bold text-lg-body-2"
                          >
                            {{ log.added_by }}
                          </span>
                        </v-col>
                        <v-col
                          class="ma-0 pb-0 d-flex justify-lg-end"
                          cols="12"
                          lg="6"
                        >
                          <span
                            class="
                              text-caption
                              font-weight-bold
                              text-lg-body-caption
                            "
                            >{{ log.created }}</span
                          >
                        </v-col>
                        <v-col
                          class="ma-0 pt-0 pb-0 text-caption text-lg-body-2"
                          cols="12"
                        >
                          <span> {{ log.message }} </span>
                        </v-col>
                      </v-row>
                    </v-card-text>
                  </v-card>
                </v-timeline-item>
              </v-timeline>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
      <CommonTripsheet v-model="showTripPdfDialog" :type="sheettype" />
      <v-dialog
        width="60%"
        v-model="showTempratureDialog"
        @keydown.esc="closeChartDialog"
      >
        <v-card>
          <v-card-title>
            <span>Temperature Log</span>
            <v-spacer />
            <v-btn x-small fab depressed @click="closeChartDialog">
              <v-icon small>mdi-close</v-icon>
            </v-btn>
          </v-card-title>
          <v-card-text class="pa-4">
            <v-tabs v-model="tempTab" background-color="primary" dark>
              <v-tab>Dry</v-tab>
              <v-tab>Frozen</v-tab>
              <v-tab>Chilled</v-tab>
            </v-tabs>
            <v-row style="min-height: 400px">
              <v-col
                cols="12"
                v-if="
                  chart &&
                  Object.keys(
                    tempTab == 0
                      ? dryTempData
                      : tempTab == 1
                      ? frozenTempData
                      : tempTab == 2
                      ? chilledTempData
                      : {}
                  ).length
                "
              >
                <CommonChartsLineChart
                  :datasets="
                    tempTab == 0
                      ? dryTempData
                      : tempTab == 1
                      ? frozenTempData
                      : tempTab == 2
                      ? chilledTempData
                      : null
                  "
                  :options="barOptions"
                />
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-dialog>
    </v-card-text>
    <TripTriporders v-model="showOrderListDialog" />
    <TripTripattachment v-model="openTripAttachmentDialog" />
  </div>
</template>

<script>
import { makeInstance, encryptLocal } from "~/assets/js/encryptLocal";
import PieChart from "@/components/common/charts/PieChart.vue";
import XLSX from "xlsx";
import { toCapitalize } from "~/assets/utils";

export default {
  props: {
    reloadChart: {
      default: false,
    },
  },
  watch: {
    tempTab() {
      this.chart = false;
      setTimeout(() => {
        this.chart = true;
      }, 200);
    },
  },
  components: {
    PieChart,
  },
  data() {
    return {
      tempTab: 0,
      chart: false,
      openTripEditDialog: false,
      openTripAttachmentDialog: false,
      showOrderListDialog: false,
      tripStatus: "active",
      containerHeight: null,
      sheettype: null,
      showLogs: false,
      showTripPdfDialog: false,
      showTempratureDialog: false,
      options: {
        responsive: true,
        legend: {
          boxWidth: 20,
          display: true,
          textAlign: "start",
          position: "bottom",
        },
      },
      options2: {
        responsive: true,
        legend: {
          boxWidth: 20,
          display: true,
          textAlign: "start",
          position: "bottom",
        },
        tooltips: {
          callbacks: {
            label: function (tooltipItem, data, d) {
              return ` ${data.labels[tooltipItem.index]} : ${
                data.datasets[0].data[tooltipItem.index]
              } minute`;
            },
          },
        },
      },
      userPermissions: encryptLocal.getItem("permissions"),
      barOptions: {
        responsive: true,
        maintainAspectRatio: false,
      },
    };
  },
  updated() {
    //Note This is used for scrolling in future
    // document.getElementById("tripdetails").scrollTop =
    //   document.getElementById("tripdetails").scrollHeight + 100;
  },
  computed: {
    currentTrip() {
      return this.$store.state.trip.currentTrip;
    },
    tripTempratureData() {
      return this.$store.getters["trip/TEMRATURE_DATA"];
    },
    chilledTempData() {
      let data = this.$store.state.trip.chilledTempratureData;
      if (data && data.length > 0) {
        let grapghData = {
          labels: data.map((obj) => {
            return obj.timestamp;
          }),
          datasets: [
            {
              label: "Chilled",
              data: data.map((obj) => {
                return obj.temperature;
              }),
              fill: false,
              borderColor: "#f97d9d",
              tension: 0.1,
            },
          ],
        };
        return grapghData;
      } else {
        return {};
      }
    },
    dryTempData() {
      const data = this.$store.state.trip.dryTempratureData;
      if (data && data.length > 0) {
        let grapghData = {
          labels: data.map((obj) => {
            return obj.timestamp;
          }),
          datasets: [
            {
              label: "Dry",
              data: data.map((obj) => {
                return obj.temperature;
              }),
              fill: false,
              borderColor: "#fab079",
              tension: 0.1,
            },
          ],
        };
        return grapghData;
      } else {
        return {};
      }
    },
    frozenTempData() {
      let data = this.$store.state.trip.frozenTempratureData;
      if (data && data.length > 0) {
        let grapghData = {
          labels: data.map((obj) => {
            return obj.timestamp;
          }),
          datasets: [
            {
              label: "Frozen",
              data: data.map((obj) => {
                return obj.temperature;
              }),
              fill: false,
              borderColor: "#13b6cf",
              tension: 0.1,
            },
          ],
        };
        return grapghData;
      } else {
        return {};
      }
    },
  },
  methods: {
    formatHeaders(data) {
      return data.map((e, i) => {
        let obj = {};
        Object.keys(e).forEach((header, j) => {
          let h = header.replace(/\_/g, " ");
          obj[toCapitalize(h)] = e[header];
        });
        return obj;
      });
    },
    openLoadSheetDialog(id) {
      this.$store
        .dispatch("trip/GET_LOAD_SHEET_ITEM_LIST", id)
        .then((response) => {
          const data = XLSX.utils.json_to_sheet(
            this.formatHeaders(this.$store.state.trip.loaditemlist)
          );
          const wb = XLSX.utils.book_new();
          wb.Props = {
            Title: this.uploadTo + " Load Sheet excel file",
            Subject: "Load Sheet Excel",
            Author: "Fero",
            CreatedDate: new Date(),
          };

          XLSX.utils.book_append_sheet(wb, data, "data");
          XLSX.writeFile(wb, "load-sheet.xlsx");
        })
        .catch((error) => {
          console.log(error);
        });
    },
    openTripSheetDialog(id) {
      this.$store
        .dispatch("trip/GET_TRIP_SHEET_ITEM_LIST", id)
        .then((response) => {
          this.showTripPdfDialog = true;
          this.sheettype = "trip";
        })
        .catch((error) => {
          console.log(error);
        });
    },
    getTempratureData(id) {
      this.chart = false;
      this.$store
        .dispatch("trip/GET_TRIP_TEMPRATURE_DATA", id)
        .then((result) => {
          for (let key in result) {
            if (result[key].length) {
              this.showTempratureDialog = true;
              this.$forceUpdate();
            }
          }
          this.chart = true;
          this.$forceUpdate();
        })
        .catch((err) => {
          this.$notifier.showMessage({
            content: err.message,
            color: "error",
          });
        });
    },
    closeChartDialog() {
      this.chart = false;
      this.showTempratureDialog = false;
    },
    coloredTripStatus(status) {
      switch (status) {
        case "scheduled":
          return "#90A4AE";
        case "active":
          return "#90CAF9";
        case "paused":
          return "#FFB300";
        case "completed":
          return "#66BB6A";

        default:
          return "#ffffff";
      }
    },

    tripStatusDarkColor(status) {
      switch (status) {
        case "scheduled":
          return "unassigned";
        case "active":
          return "assigned";
        case "paused":
          return "pickedup";
        case "completed":
          return "successful";
      }
    },
    tripStatusLightColor(status) {
      switch (status) {
        case "scheduled":
          return "light_unassigned";
        case "active":
          return "light_assigned";
        case "paused":
          return "light_pickedup";
        case "completed":
          return "light_successful";
      }
    },
    async editTrip(trip) {
      let orderParams = {
        project__project_id: trip.project_id,
        execution_date: trip.trip_date,
      };
      let driverParams = {
        project__project_id: trip.project_id,
        trip_date: trip.trip_date,
        is_active: true,
      };
      await this.$store.dispatch(
        "trip_creation/GET_UNASSIGNED_ORDERS",
        orderParams
      );
      await this.$store.dispatch(
        "trip_creation/GET_UNASSIGNED_DRIVERS",
        driverParams
      );
      // making same convention for already assigned driver
      let obj = {};
      obj.id = trip.driver_id;
      obj.first_name = trip.driver;
      await this.$store.commit(
        "trip_creation/PUSH_TO_UNASSIGNED_DRIVERS_LIST",
        obj
      );
      // Making same convention for orders
      trip.orders = trip.trip_orders;
      delete trip.trip_orders;

      await this.$store.commit("trip_creation/SET_TRIP_LIST", {
        data: [trip],
        mode: true,
      });
      await this.$router.push("/trip/edit/");
    },
  },
  mounted() {
    if (process.browser) {
      if (this.$vuetify.breakpoint.xl) {
        this.containerHeight =
          ((window.innerHeight / 100) * 78).toFixed() + "px";
      } else if (this.$vuetify.breakpoint.lg) {
        this.containerHeight =
          ((window.innerHeight / 100) * 74).toFixed() + "px";
      }
    }
  },
  beforeCreate() {
    if (encryptLocal == null) {
      makeInstance(localStorage.getItem("user"));
    }
  },
};
</script>

<style scoped>
</style>

