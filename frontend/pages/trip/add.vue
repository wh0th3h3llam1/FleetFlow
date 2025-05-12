<template>
  <div
    class="pa-4 light_grey"
    style="height: 92vh; display: flex; flex-direction: column"
  >
    <v-row no-gutters>
      <v-col cols="3" class="pa-4">
        <v-text-field
          label="Search here.."
          v-model="searchString"
          prepend-inner-icon="mdi-magnify"
          hide-details="auto"
          outlined
          dense
          clearable
          class="background-white"
        ></v-text-field>
        <v-tabs
          grow
          slider-color="primary"
          class="pt-4"
          v-model="activeTab"
          background-color="white"
        >
          <v-tab><span class="caption">Unassigned Orders</span></v-tab>
          <v-tab class="caption">Unassigned Drivers</v-tab>
        </v-tabs>
        <v-tabs-items v-model="activeTab" class="light_grey">
          <!------------------------------------------------------------- Orders Tab ------------------------------------------------------------->
          <v-tab-item class="pa-2" style="background-color: white">
            <div
              v-if="
                Orders && !Orders.length && (!trip.trip_date || !trip.project)
              "
              class="d-flex justify-center align-center"
              style="height: 74vh"
            >
              <span>Please select Trip date & Project!</span>
            </div>
            <div
              v-else-if="
                Orders && !Orders.length && trip.trip_date && trip.project
              "
              class="d-flex justify-center align-center"
              style="height: 74vh"
            >
              <span>No records to show</span>
            </div>
            <div
              v-else
              ref="ordersTab"
              class="overflow-y-auto overflow-x-hidden"
              :style="{ height: this.containerHeight }"
            >
              <v-row
                class="py-1"
                style="
                  position: sticky;
                  top: 0;
                  background-color: white;
                  z-index: 2;
                "
              >
                <v-col cols="6" class="pl-9">
                  <span>Select All</span>
                </v-col>
                <v-col cols="6" class="d-flex justify-end pr-7">
                  <v-checkbox
                    class="ma-0 pa-0"
                    hide-details
                    :input-value="
                      selectedOrders.length != 0 &&
                      selectedOrders.length ==
                        Orders.filter((order) => Object.keys(order).length != 0)
                          .length
                        ? true
                        : false
                    "
                    @change="selectAllOrders($event)"
                  ></v-checkbox>
                </v-col>
              </v-row>
              <div v-for="(order, orderIndex) in Orders" :key="orderIndex">
                <div
                  class="card mx-0 mt-2 mb-0"
                  :draggable="true"
                  @dragstart="onDragStart($event, order.id)"
                  v-if="Object.keys(order).length > 0"
                >
                  <LazyTripTriporderscard
                    :order="order"
                    :index="orderIndex"
                    @sendData="CheckboxSelect($event, order.id)"
                    :isChecked="selectedOrders.indexOf(order.id) > -1"
                  />
                </div>
              </div>
            </div>
          </v-tab-item>
          <!-------------------------------------------------------------------- Drivers Tab -------------------------------------------------------------------->
          <v-tab-item class="pa-2" style="background-color: white">
            <div
              v-if="
                allDrivers &&
                !allDrivers.length &&
                (!trip.trip_date || !trip.project)
              "
              class="d-flex justify-center align-center"
              style="height: 74vh"
            >
              <span>Please select Trip date & Project!</span>
            </div>
            <div
              v-else-if="
                allDrivers &&
                !allDrivers.length &&
                trip.trip_date &&
                trip.project
              "
              class="d-flex justify-center align-center"
              style="height: 74vh"
            >
              <span>No records to show</span>
            </div>
            <div
              v-else
              style="height: 74vh"
              class="overflow-y-auto align-start"
            >
              <div id="driverParent" ref="driverParent">
                <div
                  v-for="(driver, driverIndex) in allDrivers"
                  :key="driverIndex"
                >
                  <div class="card mx-0 mt-1 mb-0">
                    <v-row>
                      <v-col
                        cols="3"
                        class="d-flex align-center justify-center"
                      >
                        <img
                          src="~/static/user.png"
                          class="pa-3"
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
                                  <v-icon class="pr-1 primary--text cf-icon">
                                    mdi-account-box
                                  </v-icon>
                                  {{ driver.first_name }} {{ driver.last_name }}
                                </span>
                              </template>
                              <span>Driver Name</span>
                            </v-tooltip>
                          </v-col>
                          <v-col cols="12" class="cf-card-space">
                            <v-icon class="pr-1 primary--text cf-icon">
                              mdi-cellphone
                            </v-icon>
                            <span class="cf-card-text font-weight-noraml">
                              {{ driver.contact_number }}
                            </span>
                          </v-col>
                          <v-col cols="12" class="cf-card-space">
                            <v-icon class="pr-1 primary--text cf-icon">
                              mdi-truck
                            </v-icon>
                            <span class="cf-card-text font-weight-noraml">
                              {{ driver.vehicle }}
                            </span>
                          </v-col>
                          <v-col cols="6" class="cf-card-space">
                            <v-icon class="pr-1 primary--text cf-icon">
                              mdi-file-document
                            </v-icon>
                            <span
                              class="
                                cf-card-text
                                font-weight-normal
                                text-capitalize
                              "
                            >
                              {{ driver.project }}
                            </span>
                          </v-col>
                          <v-col cols="6" class="text-right pr-3 cf-card-space">
                            <span class="caption text-capitalize">
                              {{ driver.status }}
                            </span>
                            <v-avatar
                              :class="coloredDriverStatus(driver.status)"
                              size="16"
                              class="ml-1"
                            ></v-avatar>
                          </v-col>
                        </v-row>
                      </v-col>
                    </v-row>
                  </div>
                </div>
              </div>
            </div>
          </v-tab-item>
        </v-tabs-items>
      </v-col>
      <!---------------------------------------------------------- Other side WHile Create Trip---------------------------------------------------------->
      <v-col
        cols="9"
        class="pa-8"
        style="background-color: white"
        v-if="!editMode"
      >
        <div>
          <span
            class="
              text-lg-subtitle-1 text-xl-h6 text-uppercase
              font-weight-black
              primary--text
            "
          >
            Trip Creation
          </span>
          <v-alert
            v-if="Object.keys(nonFieldError).length != 0"
            dense
            dismissible
            v-model="alert"
            type="error"
          >
            <v-list
              class="pa-0"
              dense
              style="background: inherit !important"
              v-for="(errors, key, i) in nonFieldError"
              :key="i"
            >
              <v-list-item dense style="min-height: 20px !important">
                <span>{{ key }} .</span>
              </v-list-item>
              <v-list-item
                dense
                style="min-height: 20px !important"
                v-for="(error, i) in errors"
                :key="i"
              >
                <span>{{ error }}</span>
              </v-list-item>
            </v-list>
          </v-alert>
          <v-form v-model="isValid" class="mt-4" ref="emtyTripForm">
            <v-row class="mb-2">
              <v-col cols="2">
                <v-menu
                  ref="tripDate"
                  v-model="tripDate"
                  :close-on-content-click="false"
                  :return-value.sync="trip.trip_date"
                  transition="scale-transition"
                  offset-y
                  min-width="auto"
                >
                  <template v-slot:activator="{ on, attrs }">
                    <v-text-field
                      v-model="trip.trip_date"
                      label="Trip Date"
                      :rules="[(v) => !!v || 'Trip Date is required']"
                      @change="validate"
                      prepend-inner-icon="mdi-calendar"
                      :error-messages="error.trip_date"
                      hide-details="auto"
                      dense
                      outlined
                      readonly
                      v-bind="attrs"
                      v-on="on"
                    ></v-text-field>
                  </template>
                  <v-date-picker
                    v-model="trip.trip_date"
                    :min="nowDate"
                    no-title
                    scrollable
                    @change="$refs.tripDate.save(trip.trip_date), validateField"
                  >
                  </v-date-picker>
                </v-menu>
              </v-col>
              <v-col cols="2">
                <v-select
                  dense
                  v-model="trip.project"
                  :rules="[(v) => !!v || 'Project is required']"
                  hide-details="auto"
                  outlined
                  label="Select Project"
                  :error-messages="error.project"
                  :items="allProjects"
                  return-object
                  @change="validateField($event)"
                  :menu-props="{ offsetY: true }"
                ></v-select>
              </v-col>
              <v-col cols="2">
                <v-select
                  dense
                  hide-details="auto"
                  outlined
                  :rules="[(v) => !!v || 'Driver is required']"
                  v-model="trip.driver"
                  label="Select Driver"
                  :items="allDrivers"
                  item-text="first_name"
                  item-value="id"
                  :error-messages="error.driver"
                  @change="validate"
                  return-object
                  :menu-props="{ offsetY: true }"
                ></v-select>
              </v-col>
              <v-col cols="2">
                <v-text-field
                  dense
                  hide-details="auto"
                  :error-messages="error.reference_number"
                  outlined
                  :rules="[(v) => !!v || 'Trip Reference number is required']"
                  @input="validate"
                  v-model="trip.reference_number"
                  label="Trip Reference number"
                ></v-text-field>
              </v-col>
              <v-col cols="2">
                <v-btn
                  small
                  class="primary cf-list-btn px-2 rounded"
                  @click="addEmtyTripToArray()"
                  :disabled="!isValid"
                  @keydown.enter="addEmtyTripToArray()"
                >
                  Create Empty Trip</v-btn
                >
              </v-col>
              <v-col v-if="tripList.length" class="d-flex justify-end" cols="2">
                <v-btn class="primary" @click="submitTrips()">
                  Create Trip(s)
                </v-btn>
              </v-col>
            </v-row>
          </v-form>
        </div>

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
              <div class="px-4 py-3 d-flex justify-space-between align-center">
                <div>
                  <span class="trip-expansion-title mr-1 pa-1">
                    {{ trip.reference_number }}
                  </span>

                  <v-tooltip
                    top
                    content-class="no-opacity"
                    :close-delay="0"
                    :open-delay="200"
                    color="transparent"
                    max-width="300"
                  >
                    <template v-slot:activator="{ on, attrs }">
                      <span
                        v-bind="attrs"
                        v-on="on"
                        class="trip-expansion-title mr-1 pa-1"
                      >
                        <v-icon class="mr-2" color="white"> mdi-truck </v-icon>
                        {{ trip.driver.vehicle_info.vehicle_plate_no }}
                      </span>
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
                        <v-col cols="6" class="text-grey py-1">
                          <span> CBM Capacity </span>
                        </v-col>
                        <v-col cols="6" class="text-grey py-1">
                          <span class="font-weight-bold">
                            {{ trip.driver.vehicle_info.cbm_capacity }}
                          </span>
                        </v-col>
                        <v-col cols="6" class="text-grey py-1">
                          <span> Tonnage Capacity </span>
                        </v-col>
                        <v-col cols="6" class="text-grey py-1">
                          <span class="font-weight-bold">
                            {{ trip.driver.vehicle_info.tonnage_capacity }}
                          </span>
                        </v-col>
                        <v-col
                          cols="6"
                          class="text-grey d-flex align-center py-1"
                        >
                          <span> Storage Type(s) </span>
                        </v-col>
                        <v-col cols="6" class="text-grey py-1">
                          <v-row no-gutters>
                            <v-col
                              cols="12"
                              v-for="(type, type_index) in trip.driver
                                .vehicle_info.storages"
                              :key="type_index"
                            >
                              <v-icon
                                :color="
                                  type == 'Dry'
                                    ? 'light_orange'
                                    : type == 'Chilled'
                                    ? 'light_red'
                                    : type == 'Frozen'
                                    ? 'blue'
                                    : ''
                                "
                                class="mr-1"
                              >
                                {{
                                  type == "Dry"
                                    ? "mdi-white-balance-sunny"
                                    : type == "Chilled"
                                    ? "mdi-ice-pop"
                                    : type == "Frozen"
                                    ? "mdi-snowflake"
                                    : ""
                                }}
                              </v-icon>
                              <span class="font-weight-bold">
                                {{
                                  type == "Dry"
                                    ? "Dry"
                                    : type == "Chilled"
                                    ? "Chilled"
                                    : type == "Frozen"
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
                </div>

                <div>
                  <span class="trip-expansion-title mr-1 pa-1">
                    <v-icon class="mr-2" color="white">
                      mdi-card-account-details-outline
                    </v-icon>
                    {{ trip.driver.first_name }}
                  </span>
                  <span
                    class="trip-expansion-title mr-1 pa-1"
                    v-if="trip.orders"
                  >
                    <v-icon class="mr-2" color="white">
                      mdi-archive-outline
                    </v-icon>
                    Orders {{ trip.orders.length }}
                  </span>
                  <span class="trip-expansion-title mr-1 pa-1">
                    <v-icon color="white" @click="removeTrip(tripIndex)">
                      mdi-close-box
                    </v-icon>
                  </span>
                </div>
              </div>
            </v-expansion-panel-header>
            <v-expansion-panel-content
              class="border-x-light_grey border-bottom-light_grey"
            >
              <v-row no-gutters>
                <v-col
                  cols="12"
                  class="pt-4"
                  v-if="trip.errors && trip.errors.length"
                >
                  <v-alert dense type="error" text dismissible v-model="alert">
                    <v-list
                      class="pa-0"
                      dense
                      outlined
                      style="background: inherit !important"
                      v-for="(error, i) in trip.errors"
                      :key="i"
                    >
                      <v-list-item dense style="min-height: 20px !important">
                        <span class="primary--text">{{ i + 1 }} .</span
                        ><span class="primary--text">{{ error }}</span>
                      </v-list-item>
                    </v-list>
                  </v-alert>
                </v-col>
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
                    <v-col
                      cols="12"
                      v-if="
                        mapData[tripIndex] &&
                        Object.keys(mapData[tripIndex]).length > 0
                      "
                    >
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
                                mapData[tripIndex].vehicle_partition.chilled,
                                mapData[tripIndex].vehicle_partition.dry,
                                mapData[tripIndex].vehicle_partition.frozen,
                              ],
                            },
                          ],
                        }"
                        :options="options"
                        :height="100"
                      />
                    </v-col>
                  </v-row>
                </v-col>

                <v-col
                  cols="8"
                  v-if="
                    mapData[tripIndex] &&
                    Object.keys(mapData[tripIndex]).length > 0
                  "
                  class="pa-3 d-flex justify-center align-center"
                >
                  <v-row
                    class="trip-expansion-body"
                    v-if="
                      mapData[tripIndex] &&
                      Object.keys(mapData[tripIndex]).length > 0
                    "
                  >
                    <v-col cols="3" class="border-right-light_grey">
                      <v-card elevation="0">
                        <v-card-title class="pa-0 d-flex justify-center"
                          ><h6>Weight</h6></v-card-title
                        >
                        <v-card-text class="pa-0 text-center">
                          <span>
                            {{ mapData[tripIndex].total_weight }}
                          </span>
                        </v-card-text>
                      </v-card>
                    </v-col>
                    <v-col cols="3" class="border-right-light_grey">
                      <v-card class="text-center" elevation="0">
                        <v-card-title class="pa-0 d-flex justify-center"
                          ><h6>Volume</h6></v-card-title
                        >
                        <v-card-text class="pa-0 text-center">
                          <span>
                            <span>
                              {{ mapData[tripIndex].total_volume }}
                            </span>
                          </span>
                        </v-card-text>
                      </v-card>
                    </v-col>
                    <v-col cols="3" class="border-right-light_grey">
                      <v-card class="text-center" elevation="0">
                        <v-card-title class="pa-0 d-flex justify-center"
                          ><h6>Distance</h6></v-card-title
                        >
                        <v-card-text class="pa-0 text-center">
                          <span>
                            <span>
                              {{ mapData[tripIndex].distance_in_km }} km
                            </span>
                          </span>
                        </v-card-text>
                      </v-card>
                    </v-col>
                    <v-col cols="3" class="border-right-light_grey">
                      <v-card elevation="0">
                        <v-card-title class="pa-0 d-flex justify-center">
                          <h6>Boxes</h6>
                        </v-card-title>
                        <v-card-text class="pa-0 text-center">
                          <span>
                            {{ mapData[tripIndex].boxes }}
                          </span>
                        </v-card-text>
                      </v-card>
                    </v-col>
                    <v-col cols="3" class="border-right-light_grey">
                      <v-card class="text-center" elevation="0">
                        <v-card-title class="pa-0 d-flex justify-center"
                          ><h6>Travelling Time</h6></v-card-title
                        >
                        <v-card-text class="pa-0 text-center">
                          <span>
                            <span>
                              {{ mapData[tripIndex].travelling_time }}</span
                            >
                          </span>
                        </v-card-text>
                      </v-card>
                    </v-col>
                    <v-col cols="3" class="border-right-light_grey">
                      <v-card class="text-center" elevation="0">
                        <v-card-title class="pa-0 d-flex justify-center"
                          ><h6>Total Time</h6></v-card-title
                        >
                        <v-card-text class="pa-0 text-center">
                          <span>
                            <span> {{ mapData[tripIndex].total_time }}</span>
                          </span>
                        </v-card-text>
                      </v-card>
                    </v-col>
                    <v-col cols="3" class="border-right-light_grey">
                      <v-card class="text-center" elevation="0">
                        <v-card-title class="pa-0 d-flex justify-center"
                          ><h6>Item Quantity (Each)</h6></v-card-title
                        >
                        <v-card-text class="pa-0 text-center">
                          <span>
                            {{ mapData[tripIndex].total_no_of_items }}
                          </span>
                        </v-card-text>
                      </v-card>
                    </v-col>
                    <v-col cols="3" class="border-right-light_grey">
                      <v-card class="text-center" elevation="0">
                        <v-card-title class="pa-0 d-flex justify-center"
                          ><h6>total cases</h6></v-card-title
                        >
                        <v-card-text class="pa-0 text-center">
                          <span>
                            {{ mapData[tripIndex].total_no_of_cases }}
                          </span>
                        </v-card-text>
                      </v-card>
                    </v-col>
                    <v-col cols="3" class="border-right-light_grey">
                      <v-card class="text-center" elevation="0">
                        <v-card-title class="pa-0 d-flex justify-center"
                          ><h6>Total Utilized %</h6></v-card-title
                        >
                        <v-card-text class="pa-0 text-center">
                          <span>
                            {{ mapData[tripIndex].vehicle_partition.used }}
                          </span>
                        </v-card-text>
                      </v-card>
                    </v-col>
                    <v-col cols="3" class="border-right-light_grey">
                      <v-card class="text-center" elevation="0">
                        <v-card-title class="pa-0 d-flex justify-center"
                          ><h6>Total Unutilized %</h6></v-card-title
                        >
                        <v-card-text class="pa-0 text-center">
                          <span>
                            {{ mapData[tripIndex].vehicle_partition.unused }}
                          </span>
                        </v-card-text>
                      </v-card>
                    </v-col>
                  </v-row>
                </v-col>

                <v-col
                  cols="4"
                  v-if="
                    mapData[tripIndex] &&
                    Object.keys(mapData[tripIndex]).length > 0
                  "
                >
                  <v-row no-gutters class="d-flex justify-center my-4">
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
                            {{ mapData[tripIndex].vehicle_partition.chilled }}
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
                            {{ mapData[tripIndex].vehicle_partition.dry }}
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
                            {{ mapData[tripIndex].vehicle_partition.frozen }}
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
                            {{ mapData[tripIndex].chilled_cases }}
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
                            {{ mapData[tripIndex].dry_cases }}
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
                            {{ mapData[tripIndex].frozen_cases }}
                          </span>
                        </v-card-text>
                      </v-card>
                    </v-col>
                  </v-row>
                </v-col>
                <v-col cols="12">
                  <div
                    :dropzone="true"
                    class="dropZone background-white mb-2"
                    @dragenter.prevent
                    @dragover.prevent
                    @drop="onOrderDrop($event, tripIndex)"
                  >
                    <div
                      v-if="trip.orders && !trip.orders.length"
                      class="d-flex justify-center align-center pa-12"
                    >
                      <span> Drag & Drop orders here </span>
                    </div>
                    <v-simple-table
                      border="1"
                      v-else
                      fixed-header
                      dense
                      height="300px"
                      style="width: 100%"
                      class="cf-table pt-4"
                    >
                      <template v-slot:default>
                        <thead>
                          <tr>
                            <th
                              background-color="light-blue lighten-5"
                              style="
                                border-bottom: 1px solid #80808069 !important;
                                border-top: 1px solid #80808069 !important;
                                border-left: 1px solid #80808069 !important;
                              "
                              class="text-left text-primary"
                            >
                              Reference Number
                            </th>
                            <th
                              style="
                                border-bottom: 1px solid #80808069 !important;
                                border-top: 1px solid #80808069 !important;
                              "
                              class="text-left text-primary"
                            >
                              Customer Name
                            </th>
                            <th
                              style="
                                border-bottom: 1px solid #80808069 !important;
                                border-top: 1px solid #80808069 !important;
                              "
                              class="text-left text-primary"
                            >
                              Order Type
                            </th>
                            <th
                              style="
                                border-bottom: 1px solid #80808069 !important;
                                border-top: 1px solid #80808069 !important;
                              "
                              class="text-left text-primary"
                            >
                              Total Weight(KG)
                            </th>
                            <th
                              style="
                                border-bottom: 1px solid #80808069 !important;
                                border-top: 1px solid #80808069 !important;
                              "
                              class="text-left text-primary"
                            >
                              Total Volume(CBM)
                            </th>
                            <th
                              style="
                                border-bottom: 1px solid #80808069 !important;
                                border-top: 1px solid #80808069 !important;
                                border-right: 1px solid #80808069 !important;
                              "
                              class="text-left text-primary"
                            >
                              Action
                            </th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr
                            v-for="(order, i) in trip.orders"
                            :key="i"
                            :draggable="true"
                            @dragstart="
                              onInternalDragStart($event, i, tripIndex)
                            "
                            @dragover.prevent="onDragOver($event, i, tripIndex)"
                          >
                            <td>
                              <v-tooltip left>
                                <template v-slot:activator="{ on, attrs }">
                                  <v-icon
                                    color="error"
                                    v-bind="attrs"
                                    v-on="on"
                                    v-if="order.eta_violation"
                                  >
                                    mdi-information-outline
                                  </v-icon>
                                </template>
                                <span class="pr-2"
                                  >Delivery Window Violation</span
                                >
                              </v-tooltip>
                              <span>{{ order.reference_number }}</span>
                            </td>
                            <td>{{ order.customer_name }}</td>
                            <td>{{ order.order_type }}</td>
                            <td>{{ order.total_kg }}</td>
                            <td>{{ order.total_cbm }}</td>
                            <td class="d-flex align-center">
                              <v-icon
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

                  <v-row>
                    <v-col
                      v-if="trip.orders.length > 2"
                      cols="12"
                      class="pt-2 d-flex justify-end"
                    >
                      <div class="pr-2">
                        <v-btn
                          small
                          class="primary"
                          depressed
                          v-if="
                            mapData[tripIndex] &&
                            Object.keys(mapData[tripIndex]).length > 0
                          "
                          @click="view_on_map(tripIndex)"
                        >
                          <span>View on map</span>
                        </v-btn>
                      </div>
                      <v-btn
                        small
                        class="primary"
                        depressed
                        :loading="tiaLoading"
                        @click="get_trip_recommendation(trip, tripIndex)"
                      >
                        <span>TiA Recommendation</span>
                      </v-btn>
                      <v-tooltip top>
                        <template v-slot:activator="{ on, attrs }">
                          <div class="ml-2" v-bind="attrs" v-on="on">
                            <v-icon color="primary" @click="openInformationDialog">
                              mdi-information
                            </v-icon>
                          </div>
                          </template>
                          <span>Info</span>
                      </v-tooltip>
                    </v-col>
                  </v-row>
                </v-col>
              </v-row>
            </v-expansion-panel-content>
          </v-expansion-panel>
        </v-expansion-panels>
      </v-col>
    </v-row>
    <v-dialog
      v-model="openTripViewDialog"
      fullscreen
      hide-overlay
      transition="dialog-bottom-transition"
      eager
    >
      <v-card>
        <v-card-title>
          <span>{{ tripOnMap.reference_number }}</span>
          <v-spacer></v-spacer>
          <v-btn small icon @click="openTripViewDialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        <v-card-text>
          <CommonGmap
            mapWidth="100%"
            mapHeight="90vh"
            ref="tripEditCreateViewTrip"
            :dialog-status="openTripViewDialog"
            :clusterMarkers="true"
          />
        </v-card-text>
      </v-card>
    </v-dialog>
    <Tiarecommendinfo
      :openDialog="informationDialog"
      @closeDialog="closeInformationDialog"
    />
  </div>
</template>

<script>
import authHeader from "~/store/authHeader";
import PieChart from "~/components/common/charts/PieChart.vue";
import Tiarecommendinfo from "@/components/common/dialog/tiarecommendinfo";
export default {
  components: {
    PieChart,
    Tiarecommendinfo,
  },
  data() {
    return {
      tripOnMap: {},
      openTripViewDialog: false,
      orderIndexToMoveOn: undefined,
      selectedOrders: [],
      nonFieldError: [],
      formErrors: [],
      serverErrors: null,
      error: {},
      searchString: "",
      nowDate: new Date().toISOString().slice(0, 10),
      activeTab: 0,
      isValid: false,
      assignOrders: [],
      tripDate: false,
      tiaLoading: false,
      alert: true,
      trip: {
        orders: [],
        show: false,
      },
      informationDialog: false,
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
    };
  },
  computed: {
    mapData() {
      return this.$store.state.trip_creation.mapData;
    },
    containerHeight() {
      if (this.$vuetify.breakpoint.xl) {
        return ((window.innerHeight / 100) * 80).toFixed() + "px";
      } else if (this.$vuetify.breakpoint.lg) {
        return ((window.innerHeight / 100) * 75).toFixed() + "px";
      } else if (this.$vuetify.breakpoint.md) {
        return ((window.innerHeight / 100) * 70).toFixed() + "px";
      }
    },
    unassignedDrivers() {
      return [];
    },
    allProjects() {
      return this.$store.getters["project/PROJECT_LIST_FOR_DROPDOWN"];
    },
    editMode() {
      return this.$store.state.trip_creation.isEditMode;
    },
    allDrivers() {
      if (
        this.activeTab == 1 &&
        this.searchString != null &&
        this.searchString.length &&
        this.searchString.trim() != ""
      ) {
        if (this.searchString.length > 1) {
          return this.$store.state.trip_creation.unassignedDriverList.filter(
            (v) => {
              return (
                v.first_name
                  .toLowerCase()
                  .indexOf(this.searchString.toLowerCase()) > -1
              );
            }
          );
        } else {
          return this.$store.state.trip_creation.unassignedDriverList;
        }
      } else {
        return this.$store.state.trip_creation.unassignedDriverList;
      }
    },
    Orders: {
      get() {
        if (
          this.activeTab == 0 &&
          this.searchString != null &&
          this.searchString.length &&
          this.searchString.trim() != ""
        ) {
          if (this.searchString.length > 1) {
            return this.$store.state.trip_creation.unassignedOrderList
              .map((v) => {
                if (this.assignOrders.indexOf(v.id) == -1) {
                  return v;
                } else {
                  return {};
                }
              })
              .filter((v) => {
                if (v.reference_number) {
                  return (
                    v.reference_number
                      .toLowerCase()
                      .indexOf(this.searchString.toLowerCase()) > -1
                  );
                } else return true;
              });
          } else {
            return this.$store.state.trip_creation.unassignedOrderList.map(
              (v) => {
                if (this.assignOrders.indexOf(v.id) == -1) {
                  return v;
                } else {
                  return {};
                }
              }
            );
          }
        } else {
          return this.$store.state.trip_creation.unassignedOrderList.map(
            (v) => {
              if (this.assignOrders.indexOf(v.id) == -1) {
                return v;
              } else {
                return {};
              }
            }
          );
        }
      },
    },
    createdTripDates() {
      return this.tripList.map((trip) => {
        return trip.trip_date;
      });
    },
    tripRefNumbers() {
      return this.tripList.map((trip) => {
        return trip.reference_number;
      });
    },
    tripList: {
      get() {
        return this.$store.state.trip_creation.tripList;
      },
      set(value) {
        this.$store.commit("trip_creation/SET_TRIP_LIST", value);
      },
    },
  },
  methods: {
    openInformationDialog() {
      this.informationDialog = true;
    },
    closeInformationDialog() {
      this.informationDialog = false;
    },
    refreshAssignOrders() {
      this.assignOrders = this.$store.state.trip_creation.tripList
        .map((trip) => trip.orders.map((order) => order.id))
        .reduce((p, c) => {
          return [...c, ...p];
        });
    },
    validate() {
      if (this.trip.reference_number && this.trip.trip_date) {
        if (
          this.tripList.find(
            (trip) =>
              trip.reference_number == this.trip.reference_number &&
              trip.trip_date == this.trip.trip_date
          )
        ) {
          this.error.reference_number = "Trip with this refrance exist";
          this.error.trip_date = "Trip with this date exist";
        } else {
          this.error.reference_number = null;
          this.error.trip_date = null;
        }
      }
      if (this.trip.trip_date && this.trip.driver) {
        if (
          this.tripList.find(
            (trip) =>
              trip.trip_date == this.trip.trip_date &&
              trip.driver.id == this.trip.driver.id
          )
        ) {
          this.error.driver =
            "Trip is already assigned to this driver on this date";
        } else {
          this.error.driver = null;
        }
      } else {
        this.error.reference_number = null;
        this.error.trip_date = null;
        this.error.driver = null;
      }
    },
    validateField(e) {
      if (this.trip.trip_date && this.trip.project) {
        let orderParams = {
          project__project_id: this.trip.project.value,
          execution_date: this.trip.trip_date,
        };
        let driverParams = {
          project__project_id: this.trip.project.value,
          trip_date: this.trip.trip_date,
          is_active: true,
        };
        this.$store
          .dispatch("trip_creation/GET_UNASSIGNED_ORDERS", orderParams)
          .then(() => {
            this.$store.dispatch(
              "trip_creation/GET_UNASSIGNED_DRIVERS",
              driverParams
            );
          });
      }
    },
    coloredDriverStatus(status) {
      if (status === "off_duty") {
        return "black";
      } else {
        return "pgreen";
      }
    },
    addEmtyTripToArray() {
      this.trip.show = true;
      this.$store.commit("trip_creation/CREATE_EMPTY_TRIP", this.trip);
      this.trip = {
        orders: [],
        show: false,
      };
      this.$refs.emtyTripForm.reset();
    },
    get_unassignedorder_list() {
      this.refreshAssignOrders();
      this.$store.dispatch("trip_creation/GET_UNASSIGNED_ORDERS");
    },
    syncEditTripData(value, key, index) {
      this.$store.commit("trip_creation/UPDATE_EDIT_TRIP_DATA", {
        value: value,
        key: key,
        index: index,
      });
    },
    get_trip_recommendation(trip, tripIndex) {
      this.tiaLoading = true;
      let params = {};
      params.driver = trip.driver.id;
      params.orders = trip.orders.map((order) => {
        return order.id;
      });
      this.$store
        .dispatch("trip_creation/GET_TRIP_RECOMMANDATION", params)
        .then((result) => {
          this.$store.commit("trip_creation/PUSH_TO_MAP_DATA", {
            index: tripIndex,
            data: result.data,
          });
          this.tripList[tripIndex].errors = [];
          if (result.data.cbm_capacity_exceeds) {
            this.alert = true
            this.tripList[tripIndex].errors.push(
              "Total Order CBM exceeds vehicle CBM limit"
            );
          }
          if (result.data.weight_capacity_exceeds) {
            this.alert = true
            this.tripList[tripIndex].errors.push(
              "Total Order Weight exceeds vehicle weight limit"
            );
          }
          this.$store.commit("trip_creation/UPDATE_ORDER_SEQUANCE", {
            tripIndex: tripIndex,
            data: result.data.order_details,
          });
          this.tripOnMap = trip;
          this.tiaLoading = false;
        })
        .catch((err) => {
          this.tiaLoading = false;
        });
    },
    view_on_map(tripIndex) {
      this.$refs.tripEditCreateViewTrip.clearGeoJson();
      this.$refs.tripEditCreateViewTrip.clearMarker();
      this.$refs.tripEditCreateViewTrip.initMap();
      this.$refs.tripEditCreateViewTrip.loadRoutes(
        this.mapData[tripIndex].trip_route,
        this.mapData[tripIndex].order_details,
        this.mapData[tripIndex].warehouse_details[0]
      );
      this.openTripViewDialog = true;
    },
    submitTrips() {
      if (this.tripList.length) {
        let postData = this.tripList.map((trip) => {
          return {
            reference_number: trip.reference_number,
            driver: trip.driver.id,
            orders: trip.orders.map((order) => {
              return order.id;
            }),
            trip_date: trip.trip_date,
          };
        });
        let tripsWithEmtyOrders = [];
        postData.forEach((element) => {
          if (element.orders.length == 0) {
            tripsWithEmtyOrders.push(element.reference_number);
          }
        });
        if (tripsWithEmtyOrders.length != 0) {
          this.$notifier.showMessage({
            content: `Trips ${tripsWithEmtyOrders.join()} has no orders!`,
          });
          return false;
        }
        this.$axios
          .post("/api/v1/trip/", postData, { headers: authHeader() })
          .then((result) => {
            this.$notifier.showMessage({
              content: `Trip(s) Created!`,
            });
            this.tripList = [];
            this.$router.push("/trips");
          })
          .catch((err) => {
            this.nonFieldError = err.response.data[0];
          });
      }
    },
    coloredOrderStatus(status) {
      switch (status) {
        case "unassigned":
          return "#3f3f3f";
        case "assigned":
          return "#1ab7d0";
        case "picked_up":
          return "#f28c33";
        case "delivery-attempted":
          return "#15895f";
        case "delivered":
          return "#79c267";
        case "returned":
          return "#9e1d1d";
        case "cancelled":
          return "#ff6663";
        default:
          return "#ffffff";
      }
    },
    // Drag & Drop Functions.
    onInternalDragStart(e, orderIndex, tripIndexToMoveFrom) {
      this.$store.commit("trip_creation/SET_SELECTED_INTERNAL_ORDER_TO_MOVE", {
        orderIndex: orderIndex,
        tripIndexToMoveFrom: tripIndexToMoveFrom,
      });
    },
    onDragStart(event, orderId, tripIndexToMoveFrom) {
      this.$store.commit("trip_creation/SET_SELECTED_ORDER_TO_MOVE", {
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
          this.$store.commit("trip_creation/PUSH_ORDER_TO_TRIP", obj);
          i++;
        }
      } else {
        this.$store.commit("trip_creation/PUSH_ORDER_TO_TRIP", obj);
      }
      this.selectedOrders = [];
      this.refreshAssignOrders();
      this.$forceUpdate();
    },
    removeOrderFromTrip(oldIndex, tripIndex, currentOrderIndex) {
      this.$store.commit("trip_creation/REMOVE_ORDER_FROM_TRIP", {
        oldIndex: oldIndex,
        tripIndex: tripIndex,
        currentOrderIndex: currentOrderIndex,
      });
      this.refreshAssignOrders();
    },
    removeTrip(tripIndex) {
      if (
        confirm(
          "Do You really want to delete this Trip? All the orders will get unassigned!"
        )
      ) {
        while (this.tripList[tripIndex]["orders"].length > 0) {
          this.removeOrderFromTrip(
            this.tripList[tripIndex]["orders"][0].oldIndex,
            tripIndex,
            0
          );
        }
        this.$store.commit("trip_creation/REMOVE_TRIP", tripIndex);
        this.$store.commit("trip_creation/CLEAR_MAP_DATA", tripIndex);
      }
      this.refreshAssignOrders();
    },
    CheckboxSelect(isChecked, orderId) {
      if (isChecked) {
        this.selectedOrders.push(orderId);
      } else {
        this.selectedOrders.splice(this.selectedOrders.indexOf(orderId), 1);
      }
    },
    selectAllOrders(isChecked) {
      this.$store.commit("TOGGLE_LOADER", true);
      setTimeout(() => {
        if (isChecked) {
          this.selectedOrders = [];
          this.Orders.forEach((order, i) => {
            if (Object.keys(order).length > 0) {
              this.selectedOrders.push(order.id);
            }
            if (this.Orders.length - 1 == i) {
              this.$store.commit("TOGGLE_LOADER", false);
            }
          });
        } else {
          this.$store.commit("TOGGLE_LOADER", false);
          this.selectedOrders = [];
        }
      }, 10);
      this.$forceUpdate();
    },
  },
  beforeDestroy() {
    this.tripList = [];
    this.$store.commit("trip_creation/EMPTY_ALL_FIELDS");
  },
  beforeMount() {
    this.$store.commit("trip_creation/EMPTY_ALL_FIELDS");
  },
};
</script>

<style scoped>
.dropZone {
  min-height: 14vh;
}
</style>
