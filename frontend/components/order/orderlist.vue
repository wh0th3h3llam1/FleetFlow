<template>
  <div class="border-right-light_grey">
    <v-row no-gutters>
      <v-col
        id="orderListHeaderContainer"
        cols="12"
        class="background-light_grey px-4 pt-4"
      >
        <v-row no-gutters>
          <v-col cols="6" class="px-2 pt-2">
            <span class="text-h5 text-uppercase font-weight-bold text-grey">
              Orders
            </span>
          </v-col>
          <v-scale-transition mode="out-in"> </v-scale-transition>
          <v-col cols="12" class="d-flex px-2 pt-2 pb-4">
            <v-text-field
              label="Search here.."
              prepend-inner-icon="mdi-magnify"
              hide-details="auto"
              outlined
              dense
              aria-autocomplete="false"
              class="background-white"
              :value="orderFilter.search"
              @input="syncOrderFilter($event, 'search')"
            ></v-text-field>
            <v-tooltip bottom>
              <template v-slot:activator="{ on, attrs }">
                <v-btn
                  small
                  fab
                  depressed
                  color="primary"
                  class="ml-1 rounded"
                  v-bind="attrs"
                  v-on="on"
                  @click="get_order_list(true)"
                >
                  <v-icon small>mdi-refresh</v-icon>
                </v-btn>
              </template>
              <span>Refresh</span>
            </v-tooltip>

            <v-tooltip bottom>
              <template v-slot:activator="{ on, attrs }">
                <v-btn
                  small
                  fab
                  depressed
                  color="primary"
                  class="ml-1 rounded"
                  @click="openOrderFilterDialog = true"
                  v-bind="attrs"
                  v-on="on"
                >
                  <v-icon small>mdi-filter</v-icon>
                </v-btn>
              </template>
              <span>Order Filters</span>
            </v-tooltip>

            <v-tooltip bottom>
              <template v-slot:activator="{ on, attrs }">
                <div v-bind="attrs" v-on="on">
                  <v-menu
                    transition="slide-y-transition"
                    bottom
                    right
                    left
                    offset-y
                  >
                    <template v-slot:activator="{ on, attrs }">
                      <v-btn
                        small
                        fab
                        depressed
                        color="primary"
                        class="ml-1 rounded"
                        v-bind="attrs"
                        v-on="on"
                        v-if="
                          userPermissions.order && userPermissions.order.add
                        "
                      >
                        <v-icon>mdi-plus</v-icon>
                      </v-btn>
                    </template>
                    <v-list dense style="width: 250px">
                      <v-list-item @click="openOrderForm = true">
                        <v-list-item-title>Create Order</v-list-item-title>
                      </v-list-item>
                      <v-list-item @click="open_bulk_upload_dialog('Orders')">
                        <v-list-item-title
                          >Bulk Upload Orders</v-list-item-title
                        >
                      </v-list-item>
                      <v-list-item @click="open_bulk_upload_dialog('B2C Orders')">
                        <v-list-item-title
                          >Bulk Upload B2C Orders</v-list-item-title
                        >
                      </v-list-item>
                      <v-list-item
                        @click="open_bulk_upload_dialog('Orders Update')"
                      >
                        <v-list-item-title
                          >Bulk Update Orders</v-list-item-title
                        >
                      </v-list-item>
                    </v-list>
                  </v-menu>
                </div>
              </template>
              <span>Create Order</span>
            </v-tooltip>
          </v-col>
          <v-col
            cols="12"
            class="px-2 pb-2"
            v-if="appliedFilters && appliedFilters.length !== 0"
          >
            <v-chip
              small
              close
              dark
              class="mr-1 mb-1 text-capitalize background-black"
              v-for="(filter, index) in appliedFilters"
              :key="index"
              @click:close="removeFilter(filter)"
            >
              {{ filter }}
            </v-chip>
          </v-col>
          <v-col cols="12">
            <v-row class="pb-2 px-2">
              <v-col cols="6" class="d-flex justify-start">
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

                <span>Select All</span>
              </v-col>
              <v-col
                cols="6"
                class="d-flex justify-end align-center px-2 pt-2"
                v-if="
                  selectedOrders.length &&
                  userPermissions.order &&
                  userPermissions.order.delete
                "
              >
                <span class="pr-3">
                  Selected : {{ selectedOrders.length }}
                </span>
                <v-tooltip top>
                  <template v-slot:activator="{ on, attrs }">
                    <v-hover v-slot="{ hover }">
                      <v-btn
                        fab
                        x-small
                        depressed
                        color="primary"
                        class="rounded"
                        @click="deleteOrders"
                        v-bind="attrs"
                        v-on="on"
                      >
                        <v-icon v-if="hover">mdi-delete-empty</v-icon>
                        <v-icon v-else>mdi-delete</v-icon>
                      </v-btn>
                    </v-hover>
                  </template>
                  <span>Delete selected orders?</span>
                </v-tooltip>
              </v-col>
            </v-row>
          </v-col>
          <v-col cols="12" class="d-flex px-2 pb-4" v-if="loaderProgress">
            <v-scroll-x-transition mode="out-in">
              <v-progress-linear
                color="primary"
                indeterminate
                rounded
                height="6"
              ></v-progress-linear>
            </v-scroll-x-transition>
          </v-col>
        </v-row>
      </v-col>
      <v-col
        ref="orderParent"
        cols="12"
        class="px-4 pb-4 mt-4 overflow-y-auto"
        @scroll="scrollControlOrder"
        :style="{ height: listContainerHeight }"
      >
        <div v-for="(order, index) in Orders" :key="index">
          <OrderOrderdetailcard
            @selectOrder="get_order_details(order.id)"
            @orderSelected="orderSelected($event, order.id)"
            :selectedOrders="selectedOrders"
            :order="order"
          />
        </div>
      </v-col>
    </v-row>
    <LazyOrderOrderfilter
      ref="orderFilterDialog"
      v-model="openOrderFilterDialog"
      @filterChanged="filterChanged"
    />
    <LazyOrderOrderform v-model="openOrderForm" formType="add" />
    <LazyCommonDialogBulkUpload v-model="bulkUpload" :upload-to="uploadTo" />
  </div>
</template>

<script>
import { makeInstance, encryptLocal } from "~/assets/js/encryptLocal";

export default {
  data() {
    return {
      searchString: "",
      loaderProgress: false,
      containerHeight: null,
      openOrderFilterDialog: false,
      bulkUpload: false,
      uploadTo: "",
      openOrderForm: false,
      sortingType: null,
      selectedOrders: [],
      orderFilter: {},
      userPermissions: encryptLocal.getItem("permissions"),
      listContainerHeight: `${window.innerHeight - 200}px`,
    };
  },
  computed: {
    Orders() {
      return this.$store.state.order.orderListStore.Orders;
    },
    appliedFilters() {
      return Object.keys(this.orderFilter).map((filter) => {
        return filter.replace(/\_/, " ");
      });
    },
  },
  methods: {
    selectAllOrders(isChecked) {
      if (isChecked) {
        this.selectedOrders = [];
        this.$store.state.order.orderListStore.Orders.forEach(
          (order, index) => {
            this.selectedOrders.push(order.id);
          }
        );
      } else {
        this.selectedOrders = [];
      }
    },
    deleteOrders() {
      this.$store
        .dispatch(
          "order/orderListStore/DELETE_ORDERS",
          this.selectedOrders.join(",")
        )
        .then((reap) => {
          this.selectedOrders = [];
          this.get_order_list(true);
        })
        .catch((err) => {
          console.error(err);
        });
    },
    coloredOrderStatus(status) {
      switch (status) {
        case "unassigned":
          return "#90A4AE";
        case "assigned":
          return "#90CAF9";
        case "pickedup":
          return "#FFB300";
        case "partially_delivered":
          return "#CE93D8";
        case "successful":
          return "#66BB6A";
        case "failed":
          return "#E53935";
        case "cancelled":
          return "#880E4F";
      }
    },
    refreshHeight() {
      setTimeout(() => {
        if (document.getElementById("orderListHeaderContainer")) {
          let rowHeight = document.getElementById(
            "orderListHeaderContainer"
          ).offsetHeight;

          if (typeof rowHeight == typeof 1) {
            this.listContainerHeight = `${
              window.innerHeight - (rowHeight + 80)
            }px`;
          }
        }
      }, 100);
    },
    filterChanged() {
      let filters = localStorage.getItem("orderFilters");
      if (!filters) {
        filters = {};
      }
      if (typeof filters == typeof "string") {
        filters = JSON.parse(filters);
      }
      this.orderFilter = filters;
      this.get_order_list(true);
    },
    syncOrderFilter(value, key) {
      let filters = localStorage.getItem("orderFilters");
      if (!filters) {
        filters = {};
      }
      if (typeof filters == typeof "string") {
        filters = JSON.parse(filters);
      }
      filters[key] = value;
      localStorage.setItem("orderFilters", JSON.stringify(filters));
      if (value.length > 3) {
        this.filterChanged();
      }
    },
    scrollControlOrder() {
      let elem = this.$refs.orderParent;
      if (elem == null) {
        return false;
      } else if (
        Math.ceil(elem.offsetHeight + elem.scrollTop) == elem.scrollHeight
      ) {
        this.get_order_list(false);
      }
    },
    orderSelected(e, id) {
      if (e) {
        this.selectedOrders.push(id);
      } else {
        this.selectedOrders.splice(
          this.selectedOrders.indexOf(this.selectedOrders.find((v) => v == id)),
          1
        );
      }
    },
    get_order_list(reload) {
      if (
        reload ||
        this.$store.state.order.orderListStore.totalOrdersCount !=
          this.Orders.length
      ) {
        this.selectedOrders = [];
        this.loaderProgress = true;
        this.$store
          .dispatch("order/orderListStore/GET_ALL_ORDERS", reload)
          .then((result) => {
            this.loaderProgress = false;
            this.refreshHeight();
          })
          .catch((err) => {
            this.loaderProgress = false;
          });
      }
    },
    get_order_details(id) {
      this.$store
        .dispatch("order/orderDetailStore/GET_ORDER_DETAILS", id)
        .then((result) => {
          this.refreshHeight();
          this.$emit("showOrderDetails", {
            orders: [
              {
                reference_number: result.reference_number,
                address: result.address,
                status: result.status,
                coordinates: [
                  result.coordinates.longitude,
                  result.coordinates.latitude,
                ],
                actual_delivery_location: result.actual_delivery_location,
              },
            ],
            warehouse_details: result.warehouse_details,
          });
        })
        .catch((err) => {});
    },
    open_bulk_upload_dialog(uploadType) {
      this.uploadTo = uploadType;
      this.bulkUpload = true;
    },
    removeFilter(key) {
      let actualKey = key.replace(" ", "_");
      let orderFilters = JSON.parse(localStorage.getItem("orderFilters"));
      delete orderFilters[actualKey];
      this.orderFilter = orderFilters;
      localStorage.setItem("orderFilters", JSON.stringify(orderFilters));
      this.filterChanged();
    },
  },
  mounted() {
    var filters = localStorage.getItem("orderFilters");
    if (!filters) {
      filters = {};
    }
    if (typeof filters == typeof "string") {
      filters = JSON.parse(filters);
    }
    this.orderFilter = filters;
    this.get_order_list(true);
    setTimeout(this.$forceUpdate(), 500);
  },
  beforeCreate() {
    if (encryptLocal == null) {
      makeInstance(localStorage.getItem("user"));
    }
  },
};
</script>
