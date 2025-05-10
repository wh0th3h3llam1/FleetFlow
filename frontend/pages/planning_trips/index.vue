<template>
  <div>
    <v-row no-gutters>
      <v-col cols="3" lg="3" class="pa-4 light_grey">
        <div class="d-none1">
          <v-row no-gutters>
            <v-col cols="12" class="pt-2 pb-4">
              <v-text-field
                label="Search here.."
                prepend-inner-icon="mdi-magnify"
                v-model="searchString"
                hide-details="auto"
                outlined
                dense
                clearable
                aria-autocomplete="false"
                class="background-white"
              ></v-text-field>
            </v-col>
          </v-row>
          <v-tabs right grow>
            <v-tab class="caption">unassigned Orders</v-tab>
            <v-tab class="caption">unassigned Drivers</v-tab>

            <v-tab-item class="overflow-y-auto light_grey" style="height: 77vh">
              <div
                v-for="(order, orderIndex) in unassignedOrders"
                :key="orderIndex"
              >
                <div
                  :draggable="true"
                  @dragstart="onDragStart($event, order.id)"
                  v-show="
                    Object.keys(order).length > 0 &&
                    matchSearch(order.reference_number)
                  "
                >
                  <PlantripTripordercard
                    :order="order"
                    :index="orderIndex"
                    :isChecked="selectedOrders.indexOf(order.id) > -1"
                    @sendData="CheckboxSelect($event, order.id)"
                    @openDialog="openRejectionDialog"
                  />
                </div>
              </div>
            </v-tab-item>
            <v-tab-item class="overflow-y-auto light_grey" style="height: 77vh">
              <div id="driverParent" ref="driverParent">
                <div
                  v-for="(driver, driverIndex) in unassignedDrivers"
                  :key="driverIndex"
                >
                  <div
                    v-show="
                      matchSearch(driver.full_name) ||
                      matchSearch(driver.contact_number)
                    "
                    class="card mx-0 mt-1 mb-0"
                  >
                    <v-row>
                      <v-col
                        cols="3"
                        class="d-flex align-center justify-center"
                      >
                        <img
                          src="~/static/user.png"
                          class="pa-lg-3"
                          style="width: 100% !important"
                          alt="User"
                        />
                      </v-col>
                      <v-col cols="9">
                        <v-row no-gutters>
                          <v-col cols="12" class="cf-card-space">
                            <v-tooltip right>
                              <template v-slot:activator="{ on, attrs }">
                                <span
                                  v-bind="attrs"
                                  v-on="on"
                                  class="cf-card-text font-weight-bold"
                                >
                                  <v-icon class="pr-1 text-grey cf-icon">
                                    mdi-account-box
                                  </v-icon>
                                  {{ driver.full_name }}
                                </span>
                              </template>
                              <span>Driver Name</span>
                            </v-tooltip>
                          </v-col>
                          <v-col cols="12" class="cf-card-space">
                            <v-icon class="pr-1 text-grey cf-icon">
                              mdi-truck
                            </v-icon>
                            <span class="cf-card-text font-weight-noraml">
                              {{ driver.vehicle_assigned }}
                            </span>
                          </v-col>
                          <v-col cols="12" class="cf-card-space">
                            <v-icon class="pr-1 text-grey cf-icon">
                              mdi-map-marker-path
                            </v-icon>
                            <span class="cf-card-text font-weight-noraml">
                              {{ driver.zone }}
                            </span>
                          </v-col>
                          <v-col cols="12" class="cf-card-space">
                            <v-icon class="pr-1 text-grey cf-icon">
                              mdi-clock
                            </v-icon>
                            <span class="cf-card-text font-weight-noraml">
                              {{ driver.shift_timings }}
                            </span>
                          </v-col>
                          <v-col
                            cols="12"
                            class="d-flex justify-end cf-card-space"
                            v-if="driver.rejection_reason_list && driver.rejection_reason_list.length != 0"
                          >
                            <v-tooltip right>
                              <template v-slot:activator="{ on, attrs }">
                                <span
                                  v-bind="attrs"
                                  v-on="on"
                                  class="cf-card-text font-weight-bold"
                                >
                                  <v-icon
                                    @click="openDriverRejectionDialog(driver.rejection_reason_list)"
                                    class="mr-2 red--text"
                                  >
                                    mdi-information
                                  </v-icon>
                                </span>
                              </template>
                              <span>Rejection Reason</span>
                            </v-tooltip>
                          </v-col>
                        </v-row>
                      </v-col>
                    </v-row>
                  </div>
                </div>
              </div>
            </v-tab-item>
          </v-tabs>
        </div>
      </v-col>
      <v-col cols="9" lg="9" class="pa-4">
        <v-row no-gutters class="pb-4 d-flex">
          <v-col cols="12" class="pb-4 pt-2">
            <span class="text-h6 font-weight-bold text-grey">
              {{ planDetails.plan_name }}
            </span>
          </v-col>
          <v-col
            cols="10"
            xl="10"
            lg="10"
            md="12"
            sm="12"
            class="mb-sm-3 mb-md-3 mb-lg-0 mb-xl-0"
          >
            <v-row no-gutters>
              <v-col cols="2" class="text-center font-weight-bold text-grey">
                {{ planDetails.total_orders_count }}
              </v-col>
              <v-col cols="2" class="text-center font-weight-bold text-grey">
                {{ planDetails.planned_orders_count }}
              </v-col>
              <v-col cols="2" class="text-center font-weight-bold text-grey">
                {{ planDetails.trip_count }}
              </v-col>
              <v-col cols="2" class="text-center font-weight-bold text-grey">
                {{ planDetails.distance }}
              </v-col>
              <v-col cols="2" class="text-center font-weight-bold text-grey">
                {{ planDetails.travelling_time }}
              </v-col>
              <v-col cols="2" class="text-center font-weight-bold text-grey">
                {{ planDetails.plan_date }}
              </v-col>
            </v-row>
            <v-row no-gutters>
              <v-col cols="2" class="text-center text-caption text-grey">
                Total Orders
              </v-col>
              <v-col cols="2" class="text-center text-caption text-grey">
                Total Planned Orders
              </v-col>
              <v-col cols="2" class="text-center text-caption text-grey">
                Total Trips
              </v-col>
              <v-col cols="2" class="text-center text-caption text-grey">
                Total Distance
              </v-col>
              <v-col cols="2" class="text-center text-caption text-grey">
                Total Travelling Time
              </v-col>
              <v-col cols="2" class="text-center text-caption text-grey">
                Plan Date
              </v-col>
            </v-row>
            <v-row no-gutters class="pt-2">
              <v-col cols="2" class="text-center font-weight-bold text-grey">
                {{ planDetails.planned_locations_count }}
              </v-col>
              <v-col cols="2" class="text-center font-weight-bold text-grey">
                {{ planDetails.fleet_capacity_utilization }} %
              </v-col>
              <v-col cols="2" class="text-center font-weight-bold text-grey">
                {{ planDetails.customer_address_count }}
              </v-col>
            </v-row>
            <v-row no-gutters>
              <v-col cols="2" class="text-center text-caption text-grey">
                Total Drop Points
              </v-col>
              <v-col cols="2" class="text-center text-caption text-grey">
                Fleet Capacity Utilization
              </v-col>
              <v-col cols="2" class="text-center text-caption text-grey">
                Total Customers
              </v-col>
            </v-row>
          </v-col>
          <v-col
            cols="2"
            xl="2"
            lg="2"
            md="12"
            sm="12"
            class="d-flex justify-end align-end mb-n1"
          >
            <!-- For showing multiple trips on map  -->
            <!-- <v-btn
              class="primary mr-3"
              small
              @click="viewMap()"
            >
              View Trip
            </v-btn> -->
            <v-btn
              v-if="userPermissions.trip.add"
              class="primary"
              :disabled="planDetails.action_taken"
              @click="confirmTrips"
              small
            >
              Create Trip(s)
            </v-btn>
          </v-col>
          <v-col cols="12" class="pt-5">
            <hr />
          </v-col>
          <v-col
            cols="12"
            class="mt-5 overflow-y-auto overflow-x-hidden"
            style="height: 75vh !important"
          >
            <v-expansion-panels multiple class="pa-0 ma-0 cf-trip-expansion">
              <v-expansion-panel
                v-for="(trip, tripIndex) in tripList"
                :key="tripIndex"
                class="pa-0 mx-0 mt-0 mb-2"
              >
                <v-expansion-panel-header
                  class="primary py-0 pl-0 pr-2 ma-0"
                  style="min-height: 40px !important; color: white !important"
                >
                  <v-row no-gutters class="px-4 py-3" justify="space-between">
                    <v-tooltip
                      top
                      content-class="no-opacity"
                      :close-delay="0"
                      :open-delay="200"
                      color="transparent"
                      max-width="300"
                    >
                      <template v-slot:activator="{ on, attrs }">
                        <v-col
                          v-bind="attrs"
                          v-on="on"
                          cols="6"
                          class="d-flex align-center"
                        >
                          <span
                            class="trip-expansion-title mr-1 pa-1"
                            v-if="trip.transport_detail"
                          >
                            <v-icon class="mr-1" color="white">
                              mdi-card-account-details-outline
                            </v-icon>
                            <span class="trip-expansion-title mr-1 pa-1">
                              {{ trip.transport_detail.driver }}
                            </span>
                            <span v-if="trip.transport_detail">
                              <v-icon color="white">mdi-truck</v-icon>
                              <span class="trip-expansion-title mr-1 pa-1">
                                {{ trip.transport_detail.vehicle }}
                              </span>
                            </span>
                          </span>
                        </v-col>
                      </template>
                      <div
                        class="
                          tooltip
                          background-white
                          border-y-grey border-x-grey
                          pa-3
                          rounded-lg
                        "
                      >
                        <v-row no-gutters>
                          <v-col
                            cols="6"
                            class="text-grey py-1"
                            v-if="trip.transport_detail"
                          >
                            <span> CBM Capacity </span>
                          </v-col>
                          <v-col
                            cols="6"
                            class="text-grey py-1"
                            v-if="trip.transport_detail"
                          >
                            <span class="font-weight-bold">
                              {{ trip.transport_detail.cbm_capacity }}
                            </span>
                          </v-col>
                          <v-col
                            cols="6"
                            class="text-grey py-1"
                            v-if="trip.transport_detail"
                          >
                            <span> Tonnage Capacity </span>
                          </v-col>
                          <v-col
                            cols="6"
                            class="text-grey py-1"
                            v-if="trip.transport_detail"
                          >
                            <span class="font-weight-bold">
                              {{
                                trip.transport_detail.vehicle_tonnage_capacity
                              }}
                            </span>
                          </v-col>
                          <v-col
                            cols="6"
                            class="text-grey d-flex align-center py-1"
                            v-if="
                              trip.transport_detail &&
                              trip.transport_detail.vehicle_storage_type
                            "
                          >
                            <span> Storage Type(s) </span>
                          </v-col>
                          <v-col
                            cols="6"
                            class="text-grey py-1"
                            v-if="
                              trip.transport_detail &&
                              trip.transport_detail.vehicle_storage_type
                            "
                          >
                            <v-row no-gutters>
                              <v-col
                                cols="12"
                                v-for="(type, type_index) in trip
                                  .transport_detail.vehicle_storage_type"
                                :key="type_index"
                              >
                                <v-icon
                                  :color="
                                    type == 'D'
                                      ? 'light_orange'
                                      : type == 'C'
                                      ? 'light_red'
                                      : type == 'F'
                                      ? 'blue'
                                      : ''
                                  "
                                  class="mr-1"
                                >
                                  {{
                                    type == "D"
                                      ? "mdi-white-balance-sunny"
                                      : type == "C"
                                      ? "mdi-ice-pop"
                                      : type == "F"
                                      ? "mdi-snowflake"
                                      : ""
                                  }}
                                </v-icon>
                                <span class="font-weight-bold">
                                  {{
                                    type == "D"
                                      ? "Dry"
                                      : type == "C"
                                      ? "Chilled"
                                      : type == "F"
                                      ? "Frozen"
                                      : ""
                                  }}
                                </span>
                              </v-col>
                            </v-row>
                          </v-col>
                        </v-row>
                      </div>
                    </v-tooltip>
                    <v-col class="d-flex justify-end">
                      <span
                        class="trip-expansion-title mr-1 pa-1"
                        v-if="trip.customer_address_count"
                      >
                        <span>Customers:</span>
                        {{ trip.customer_address_count }}
                      </span>
                      <span
                        class="trip-expansion-title mr-1 pa-1"
                        v-if="trip.planned_locations_count"
                      >
                        <span>Drop Points:</span>
                        {{ trip.planned_locations_count }}
                      </span>

                      <v-btn text small readonly>
                        <span class="trip-expansion-title">
                          <v-icon class="mr-2" color="white">
                            mdi-archive-outline
                          </v-icon>
                          Orders {{ trip.planned_orders.length }}
                        </span>
                      </v-btn>
                      <v-tooltip top max-width="300">
                        <template v-slot:activator="{ on, attrs }">
                          <v-btn
                            v-bind="attrs"
                            v-on="on"
                            @click.prevent="viewMap(trip)"
                            text
                            small
                          >
                            <span class="trip-expansion-title">
                              <v-icon class="mr-2 mt-n1" color="white">
                                mdi-map
                              </v-icon>
                            </span>
                          </v-btn>
                        </template>
                        <span> Show on Map </span>
                      </v-tooltip>

                      <span
                        class="px-3 trip-expansion-title"
                        v-if="userPermissions.trip.add"
                      >
                        <v-icon color="white" @click="removeTrip(tripIndex)">
                          mdi-close-box</v-icon
                        >
                      </span>
                    </v-col>
                  </v-row>
                </v-expansion-panel-header>

                <v-expansion-panel-content
                  class="border-x-light_grey border-bottom-light_grey"
                >
                  <v-row no-gutters>
                    <v-col
                      cols="4"
                      class="
                        border-right-light_grey
                        d-flex
                        justify-center
                        align-center
                        pr-12
                        pt-6
                      "
                    >
                      <v-row no-gutters>
                        <v-col cols="12">
                          <PieChart
                            :data="{
                              labels: ['Chilled', 'Dry', 'Frozen'],
                              datasets: [
                                {
                                  backgroundColor: [
                                    '#50b7d0',
                                    '#ee872c',
                                    '#d16bc8',
                                  ],
                                  data: [
                                    trip.cargos_per.chilled,
                                    trip.cargos_per.dry,
                                    trip.cargos_per.frozen,
                                  ],
                                },
                              ],
                            }"
                            :options="options"
                            :height="140"
                          />
                        </v-col>
                      </v-row>
                    </v-col>

                    <v-col cols="8">
                      <v-row no-gutters class="trip-expansion-body pt-6">
                        <v-col
                          cols="3"
                          class="border-right-light_grey"
                          v-if="trip.mass !== null"
                        >
                          <v-card elevation="0">
                            <v-card-title class="pa-0 d-flex justify-center">
                              <h6>Weight</h6>
                            </v-card-title>
                            <v-card-text class="pa-0 text-center">
                              <span>
                                {{ trip.mass }}
                              </span>
                            </v-card-text>
                          </v-card>
                        </v-col>

                        <v-col
                          cols="3"
                          class="border-right-light_grey"
                          v-if="trip.volume !== null"
                        >
                          <v-card elevation="0">
                            <v-card-title class="pa-0 d-flex justify-center">
                              <h6>Volume</h6>
                            </v-card-title>
                            <v-card-text class="pa-0 text-center">
                              <span>
                                {{ trip.volume }}
                              </span>
                            </v-card-text>
                          </v-card>
                        </v-col>

                        <v-col cols="3" class="border-right-light_grey">
                          <v-card elevation="0">
                            <v-card-title class="pa-0 d-flex justify-center">
                              <h6>Distance</h6>
                            </v-card-title>
                            <v-card-text class="pa-0 text-center">
                              <span>
                                {{ trip.distance }}
                              </span>
                            </v-card-text>
                          </v-card>
                        </v-col>
                        <v-col cols="3">
                          <v-card elevation="0">
                            <v-card-title class="pa-0 d-flex justify-center">
                              <h6>Boxes</h6>
                            </v-card-title>
                            <v-card-text class="pa-0 text-center">
                              <span>
                                {{ trip.boxes }}
                              </span>
                            </v-card-text>
                          </v-card>
                        </v-col>
                        <v-col cols="3" class="border-right-light_grey pt-2">
                          <v-card elevation="0">
                            <v-card-title class="pa-0 d-flex justify-center">
                              <h6>Travelling Time</h6>
                            </v-card-title>
                            <v-card-text class="pa-0 text-center">
                              <span>
                                {{ trip.travelling_time }}
                              </span>
                            </v-card-text>
                          </v-card>
                        </v-col>
                        <v-col cols="3" class="border-right-light_grey pt-2">
                          <v-card elevation="0">
                            <v-card-title class="pa-0 d-flex justify-center">
                              <h6>Total Time</h6>
                            </v-card-title>
                            <v-card-text class="pa-0 text-center">
                              <span>
                                {{ trip.total_time }}
                              </span>
                            </v-card-text>
                          </v-card>
                        </v-col>
                        <v-col cols="3" class="border-right-light_grey pt-2">
                          <v-card elevation="0">
                            <v-card-title class="pa-0 d-flex justify-center">
                              <h6>ITEM QUANTITY (EACH)</h6>
                            </v-card-title>
                            <v-card-text class="pa-0 text-center">
                              <span>
                                {{ trip.cargos_count }}
                              </span>
                            </v-card-text>
                          </v-card>
                        </v-col>
                        <v-col
                          cols="3"
                          class="border-right-light_grey pt-2"
                          v-if="trip.total_cases && trip.total_cases !== null"
                        >
                          <v-card elevation="0">
                            <v-card-title class="pa-0 d-flex justify-center">
                              <h6>Total Cases</h6>
                            </v-card-title>
                            <v-card-text class="pa-0 text-center">
                              <span>
                                {{ trip.total_cases }}
                              </span>
                            </v-card-text>
                          </v-card>
                        </v-col>
                        <v-col
                          cols="3"
                          class="border-right-light_grey pt-2"
                          v-if="trip.total_cases && trip.total_cases !== null"
                        >
                          <v-card elevation="0">
                            <v-card-title class="pa-0 d-flex justify-center">
                              <h6>Total Utilized %</h6>
                            </v-card-title>
                            <v-card-text class="pa-0 text-center">
                              <span>
                                {{ trip.cargos_per.used }}
                              </span>
                            </v-card-text>
                          </v-card>
                        </v-col>
                        <v-col
                          cols="3"
                          class="border-right-light_grey pt-2"
                          v-if="trip.total_cases && trip.total_cases !== null"
                        >
                          <v-card elevation="0">
                            <v-card-title class="pa-0 d-flex justify-center">
                              <h6>Total Unutilized %</h6>
                            </v-card-title>
                            <v-card-text class="pa-0 text-center">
                              <span>
                                {{ trip.cargos_per.unused }}
                              </span>
                            </v-card-text>
                          </v-card>
                        </v-col>
                      </v-row>
                    </v-col>

                    <v-col cols="4">
                      <v-row no-gutters class="my-4">
                        <v-col cols="4" class="border-right-light_grey">
                          <v-card elevation="0">
                            <v-card-title
                              class="
                                pa-0
                                d-flex
                                justify-center
                                primary--text
                                text-no-wrap
                              "
                              ><h6>Chilled</h6></v-card-title
                            >
                            <v-card-text class="pa-0 text-center">
                              <span class="text-no-wrap">
                                {{ trip.cargos_per.chilled }}
                                %
                              </span>
                            </v-card-text>
                          </v-card>
                        </v-col>
                        <v-col cols="3" class="border-right-light_grey">
                          <v-card elevation="0">
                            <v-card-title
                              class="
                                pa-0
                                d-flex
                                justify-center
                                primary--text
                                text-no-wrap
                              "
                              ><h6>Dry</h6></v-card-title
                            >
                            <v-card-text class="pa-0 text-center">
                              <span class="text-no-wrap">
                                {{ trip.cargos_per.dry }}
                                %
                              </span>
                            </v-card-text>
                          </v-card>
                        </v-col>
                        <v-col cols="4">
                          <v-card elevation="0">
                            <v-card-title
                              class="
                                pa-0
                                d-flex
                                justify-center
                                primary--text
                                text-no-wrap
                              "
                              ><h6>Frozen</h6></v-card-title
                            >
                            <v-card-text class="pa-0 text-center">
                              <span class="text-no-wrap">
                                {{ trip.cargos_per.frozen }}
                                %
                              </span>
                            </v-card-text>
                          </v-card>
                        </v-col>

                        <v-col cols="4" class="pt-3 border-right-light_grey">
                          <v-card elevation="0">
                            <v-card-title
                              class="
                                pa-0
                                d-flex
                                justify-center
                                primary--text
                                text-no-wrap
                              "
                              ><h6 style="line-height: 15px">
                                Cases
                              </h6></v-card-title
                            >
                            <v-card-text class="pa-0 text-center">
                              <span class="text-no-wrap">
                                {{ trip.cargo_cases.chilled_cases }}
                              </span>
                            </v-card-text>
                          </v-card>
                        </v-col>

                        <v-col cols="3" class="pt-3 border-right-light_grey">
                          <v-card elevation="0">
                            <v-card-title
                              class="
                                pa-0
                                d-flex
                                justify-center
                                primary--text
                                text-no-wrap
                              "
                              ><h6 style="line-height: 15px">
                                Cases
                              </h6></v-card-title
                            >
                            <v-card-text class="pa-0 text-center">
                              <span class="text-no-wrap">
                                {{ trip.cargo_cases.dry_cases }}
                              </span>
                            </v-card-text>
                          </v-card>
                        </v-col>

                        <v-col cols="4" class="pt-3">
                          <v-card elevation="0">
                            <v-card-title
                              class="
                                pa-0
                                d-flex
                                justify-center
                                primary--text
                                text-no-wrap
                              "
                              ><h6 style="line-height: 15px">
                                Cases
                              </h6></v-card-title
                            >
                            <v-card-text class="pa-0 text-center">
                              <span class="text-no-wrap">
                                {{ trip.cargo_cases.frozen_cases }}
                              </span>
                            </v-card-text>
                          </v-card>
                        </v-col>
                      </v-row>
                    </v-col>

                    <v-col cols="9"> </v-col>
                    <v-col cols="3">
                      <v-text-field
                        label="Search"
                        outlined
                        dense
                        class="pt-8"
                        v-model="mainSearch[`trip-${tripIndex}`]"
                      ></v-text-field>
                    </v-col>
                    <v-col cols="12">
                      <div
                        :dropzone="true"
                        class="dropZone background-white"
                        @dragenter.prevent
                        @dragover.prevent
                        @drop="onOrderDrop($event, tripIndex)"
                      >
                        <span v-if="!trip.planned_orders.length">
                          Drag & Drop orders here
                        </span>
                        <v-simple-table
                          v-else
                          fixed-header
                          dense
                          height="300px"
                          style="width: 100%"
                          class="mb-12"
                        >
                          <template v-slot:default>
                            <thead>
                              <tr>
                                <th
                                  class="
                                    background-light_grey
                                    text-left text-grey
                                    border-left-grey-thin border-y-grey-thin
                                  "
                                >
                                  Reference Number
                                </th>
                                <th
                                  class="
                                    background-light_grey
                                    border-y-grey-thin
                                    text-left text-grey
                                  "
                                >
                                  Customer Name
                                </th>
                                <th
                                  class="
                                    background-light_grey
                                    border-y-grey-thin
                                    text-left text-grey
                                  "
                                >
                                  Address
                                </th>
                                <th
                                  class="
                                    background-light_grey
                                    border-y-grey-thin
                                    text-left text-grey
                                  "
                                >
                                  Order Type
                                </th>
                                <th
                                  class="
                                    background-light_grey
                                    border-y-grey-thin
                                    text-left text-grey
                                  "
                                >
                                  Quantity
                                </th>
                                <th
                                  class="
                                    background-light_grey
                                    border-y-grey-thin
                                    text-left text-grey
                                  "
                                >
                                  Cases count
                                </th>
                                <th
                                  class="
                                    background-light_grey
                                    border-y-grey-thin
                                    text-left text-grey
                                  "
                                >
                                  Arrival Time
                                </th>
                                <th
                                  class="
                                    background-light_grey
                                    border-y-grey-thin
                                    text-left text-grey
                                  "
                                >
                                  Departure Time
                                </th>
                                <th
                                  class="
                                    background-light_grey
                                    border-y-grey-thin border-right-grey-thin
                                    text-left text-grey
                                  "
                                >
                                  Action
                                </th>
                              </tr>
                            </thead>
                            <tbody id="myTable">
                              <tr
                                v-for="(order, i) in trip.planned_orders"
                                class="border-bottom-gray"
                                :key="i"
                                :draggable="true"
                                @dragstart="
                                  onInternalDragStart($event, i, tripIndex)
                                "
                                @dragover.prevent="
                                  onDragOver($event, i, tripIndex)
                                "
                                v-show="
                                  searchOrder(
                                    order.reference_number,
                                    mainSearch[`trip-${tripIndex}`]
                                  )
                                "
                              >
                                <td>{{ order.reference_number }}</td>
                                <td>{{ order.customer_name }}</td>
                                <td>{{ order.address }}</td>
                                <td>{{ order.order_type }}</td>
                                <td>{{ order.cargo_count }}</td>
                                <td>{{ order.cases }}</td>
                                <td>{{ order.timings.pickup_time }}</td>
                                <td>{{ order.timings.drop_time }}</td>
                                <td>
                                  <v-icon
                                    v-if="userPermissions.trip.add"
                                    small
                                    @click.prevent="
                                      removeOrderFromTrip(
                                        order.oldIndex,
                                        tripIndex,
                                        i
                                      )
                                    "
                                  >
                                    mdi-close
                                  </v-icon>
                                </td>
                              </tr>
                            </tbody>
                          </template>
                        </v-simple-table>
                      </div>
                    </v-col>
                  </v-row>
                </v-expansion-panel-content>
              </v-expansion-panel>
            </v-expansion-panels>
          </v-col>
        </v-row>
        <PlantripViewtrip v-model="openTripViewDialog" :trip="selectedTrip" />
        <PlantripTriporderreason
          v-model="openOrderRejectDialog"
          :reason="rejectationReason"
        />
        <PlantripTripdriverreason
          v-model="openDriverRejectDialog"
          :reason="rejectionReason"
        />
      </v-col>
    </v-row>
  </div>
</template>

<script>
import { makeInstance, encryptLocal } from "~/assets/js/encryptLocal";
import PieChart from "~/components/common/charts/PieChart.vue";

export default {
  components: {
    PieChart,
  },
  data() {
    return {
      options: {
        responsive: true,
        pieceLabel: {
          mode: "percentage",
          precision: 1,
        },
        legend: {
          display: true,
          position: "right",
        },
      },
      mainSearch: {},
      orderSearching: null,
      openTripViewDialog: false,
      openOrderRejectDialog: false,
      openDriverRejectDialog: false,
      orderIndexToMoveOn: undefined,
      selectedOrders: [],
      searchString: null,
      selectedTrip: {},
      rejectationReason: null,
      rejectionReason: null,
      userPermissions: encryptLocal.getItem("permissions"),
    };
  },
  computed: {
    planId() {
      return this.$store.state.trip_planning.planId;
    },
    unassignedOrders() {
      return this.$store.state.trip_planning.unassignedOrderList;
    },
    unassignedDrivers() {
      return this.$store.state.trip_planning.unassignedDriverList;
    },
    tripList() {
      return this.$store.state.trip_planning.tripList;
    },
    planDetails() {
      return this.$store.state.trip_planning.planDetails;
    },
  },
  methods: {
    searchOrder(reference_number, search) {
      if (search && search.length > 3) {
        if (
          reference_number.toLowerCase().indexOf(search.toLowerCase()) != -1
        ) {
          return true;
        } else {
          return false;
        }
      } else {
        return true;
      }
    },
    resetOrderListInSearchedTrip() {
      this.$store.commit("trip_planning/RESET_ORDER_SEARCH", {
        search: tripSearch,
        tripIndex: tripIndex,
      });
    },
    CheckboxSelect(isChecked, orderId) {
      if (isChecked) {
        this.selectedOrders.push(orderId);
      } else {
        this.selectedOrders.splice(this.selectedOrders.indexOf(orderId), 1);
      }
    },
    openRejectionDialog(reason) {
      this.openOrderRejectDialog = true;
      this.rejectationReason = reason;
    },
    openDriverRejectionDialog(reason) {
      this.openDriverRejectDialog = true;
      this.rejectionReason = reason;
    },
    changeTooltipPosition(event) {
      setTimeout(() => {
        let tooltip = document.getElementsByClassName(
          "menuable__content__active"
        );

        if (tooltip.length) {
          if (event.clientX + tooltip[0].offsetWidth > window.innerWidth) {
            tooltip[0].style.left =
              window.innerWidth - tooltip[0].offsetWidth - 40 + "px";
          } else {
            tooltip[0].style.left = event.clientX + "px";
          }
          tooltip[0].style.top = event.clientY + 20 + "px";
        }
      }, 220);
    },
    viewMap(trip) {
      this.selectedTrip = trip;
      this.$store
        .dispatch("trip_planning/GET_LOCATION_DATA", {
          trip_id: trip.id,
          plan_id: this.planId,
        })
        .then((resp) => {
          this.openTripViewDialog = true;
        })
        .catch((err) => {
          if (err.message) {
            this.$notifier.showMessage({
              content: err.message,
              color: "error",
            });
          } else {
            this.$notifier.showMessage({
              content: "Error Fetching data!",
              color: "error",
            });
          }
        });
    },
    matchSearch(string) {
      if (this.searchString == null || this.searchString.trim().length == 0) {
        return true;
      } else {
        return (
          string.toLowerCase().indexOf(this.searchString.toLowerCase()) > -1
        );
      }
    },
    // Drag & Drop Functions.
    onInternalDragStart(e, orderIndex, tripIndexToMoveFrom) {
      this.$store.commit("trip_planning/SET_SELECTED_INTERNAL_ORDER_TO_MOVE", {
        orderIndex: orderIndex,
        tripIndexToMoveFrom: tripIndexToMoveFrom,
      });
    },
    onDragStart(event, orderId, tripIndexToMoveFrom) {
      this.$store.commit("trip_planning/SET_SELECTED_ORDER_TO_MOVE", {
        orderId: orderId,
        tripIndexToMoveFrom: tripIndexToMoveFrom,
      });
    },
    onDragOver(event, orderIndexToMoveOn) {
      this.orderIndexToMoveOn = orderIndexToMoveOn;
    },
    onOrderDrop(event, tripIndexToMoveOn) {
      let obj = {
        tripIndexToMoveOn: tripIndexToMoveOn,
      };

      if (event.target.localName !== "div") {
        obj.orderIndexToMoveOn = this.orderIndexToMoveOn;
      }

      if (this.selectedOrders.length > 0) {
        let i = 0;
        while (i < this.selectedOrders.length) {
          this.onDragStart(null, this.selectedOrders[i]);
          this.$store.commit("trip_planning/PUSH_ORDER_TO_TRIP", obj);
          i++;
        }
      } else {
        this.$store.commit("trip_planning/PUSH_ORDER_TO_TRIP", obj);
      }

      this.selectedOrders = [];
    },
    removeOrderFromTrip(oldIndex, tripIndex, currentOrderIndex) {
      this.$store.commit("trip_planning/REMOVE_ORDER_FROM_TRIP", {
        oldIndex: oldIndex,
        tripIndex: tripIndex,
        currentOrderIndex: currentOrderIndex,
      });
    },
    removeTrip(tripIndex) {
      while (this.tripList[tripIndex]["planned_orders"].length > 0) {
        this.removeOrderFromTrip(
          this.tripList[tripIndex]["planned_orders"][0].oldIndex,
          tripIndex,
          0
        );
      }

      this.$store.commit("trip_planning/REMOVE_TRIP", tripIndex);
    },
    toggleOrderSelection(isChecked, orderIndex) {
      if (isChecked) {
        this.selectedOrders.push(orderIndex);
      } else {
        this.selectedOrders.splice(this.selectedOrders.indexOf(orderIndex), 1);
      }
    },
    coloreddriverStatus(status) {
      switch (status) {
        case "Off Duty":
          return "#3f3f3f";
        case "On Duty":
          return "#79c267";
        default:
          return "#ffffff";
      }
    },
    getData() {
      this.$store.dispatch("trip_planning/GET_TRIP_PLAN_DATA", this.planId);
      // this.$store.dispatch("trip_planning/GET_PLANNED_TRIPS", this.planId);
    },
    confirmTrips() {
      // this.planDetails.action_taken = true;
      this.$store.commit("trip_planning/TOGGLE_SUBMIT_BUTTON", true);
      let payload = this.tripList.map((trip) => {
        return {
          trip_id: trip.id,
          orders: trip.planned_orders.map((order) => {
            return order.id;
          }),
        };
      });

      this.$store
        .dispatch("trip_planning/CONFIRM_TRIP", {
          plan_id: this.planId,
          data: payload,
        })
        .then((resp) => {
          this.$router.push({
            name: "trips",
            path: "/trips",
          });
        })
        .catch((err) => {
          this.$store.commit("trip_planning/TOGGLE_SUBMIT_BUTTON", false);
          if (err.message) {
            this.$notifier.showMessage({
              content: err.message,
              color: "error",
            });
          } else {
            this.$notifier.showMessage({
              content: "Error Updating data!",
              color: "error",
            });
          }
        });
    },
  },
  mounted() {
    if (this.planId == null || this.planId == undefined) {
      this.$router.push({
        name: "plan_trips",
        path: "/plan_trips",
      });
    } else {
      this.getData();
    }
  },
  beforeDestroy() {
    this.$store.commit("trip_planning/SET_UNASSIGNED_ORDERS", []);
    this.$store.commit("trip_planning/SET_UNASSIGNED_DRIVERS", []);
    this.$store.commit("trip_planning/SET_PLANNED_TRIPS", []);
    this.$store.commit("trip_planning/SET_SELECTED_PLAN_ID", null);
    this.$store.commit("trip_planning/SET_PLAN_DETAILS", {});
  },
  beforeCreate() {
    if (encryptLocal == null) {
      makeInstance(localStorage.getItem("user"));
    }
  },
};
</script>

<style lang="scss">
.no-opacity {
  opacity: 1 !important;
}
</style>
