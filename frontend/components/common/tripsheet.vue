<template>
  <v-dialog
    v-model="tripPDfDialog"
    persistent
    max-width="60%"
    scrollable
    overlay-opacity="0.9"
  >
    <v-card>
      <v-card-title style="pa-0 ma-0">
        <div>
          <v-btn
            class="white"
            x-large
            @click="printLoadSheetPreview"
            style="
              position: fixed !important;
              right: 50px !important;
              top: 50px !important;
            "
          >
            <v-icon class="mr-2 primary--text">mdi mdi-download</v-icon>
            <span class="primary--text">Download</span>
          </v-btn>
        </div>

        <v-btn
          depressed
          class="white"
          @click="closeDialogBox"
          style="position: absolute; right: 10px; top: 10px; z-index: 4"
        >
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>
      <v-card-text class="pa-12" style="position: relative">
        <div id="printtripSheet" v-if="type == 'trip'">
          <table border="0" style="table-layout: fixed; width: 100%">
            <tr>
              <td>
                <img src="../../static/logo.png" style="height: 40px" />

                <table style="margin-bottom: 30px; margin-top: 30px">
                  <tr>
                    <td>
                      <h3 class="trip-sheet-title set-color-title">
                        Driver name
                      </h3>
                    </td>
                    <td style="width: 40px"></td>
                    <td>
                      <h3 class="trip-sheet-title set-color-text">
                        {{ tripitemsheet.trip_details.driver }}
                      </h3>
                    </td>
                  </tr>
                  <tr>
                    <td>
                      <h3 class="trip-sheet-title set-color-title">
                        Vehicle No
                      </h3>
                    </td>
                    <td style="width: 40px"></td>
                    <td>
                      <h4 class="trip-sheet-title set-color-text">
                        {{ tripitemsheet.trip_details.vehicle_info.vehicle_plate_no }}
                      </h4>
                    </td>
                  </tr>
                </table>
              </td>
              <td style="padding-right: 20px">
                <table
                  style="
                    width: 100%;
                    border-collapse: collapse;
                    border: 1px solid #b6b6b6;
                  "
                >
                  <tr>
                    <td>
                      <table class="trip-sheet-table">
                        <tr>
                          <td>
                            <h4 class="trip-sheet-title">Trip Ref No.</h4>
                          </td>
                          <td style="width: 40px"></td>
                          <td>
                            <h4 class="trip-sheet-title">
                              {{ tripitemsheet.trip_details.reference_number }}
                            </h4>
                          </td>
                        </tr>
                      </table>
                      <table style="width: 100%; padding: 10px">
                        <tr>
                          <td>
                            <h5 class="trip-sheet-title-subtitle">
                              Vehicle Model
                            </h5>
                          </td>
                          <td style="width: 40px"></td>
                          <td>
                            <h6 class="trip-sheet-title-subtitle-text">
                              {{ tripitemsheet.trip_details.vehicle_model }}
                            </h6>
                          </td>
                        </tr>
                        <tr>
                          <td>
                            <h5 class="trip-sheet-title-subtitle">
                              No Of Orders
                            </h5>
                          </td>
                          <td style="width: 40px"></td>
                          <td>
                            <h6 class="trip-sheet-title-subtitle-text">
                              {{ tripitemsheet.orders.length }}
                            </h6>
                          </td>
                        </tr>
                        <tr>
                          <td>
                            <h5 class="trip-sheet-title-subtitle">
                              No Of Customers
                            </h5>
                          </td>
                          <td style="width: 40px"></td>
                          <td>
                            <h6 class="trip-sheet-title-subtitle-text">
                              {{ tripitemsheet.total_customers }}
                            </h6>
                          </td>
                        </tr>
                        <tr>
                          <td>
                            <h5 class="trip-sheet-title-subtitle">
                              Total Quantity
                            </h5>
                          </td>
                          <td style="width: 40px"></td>
                          <td>
                            <h6 class="trip-sheet-title-subtitle-text">
                              {{ tripitemsheet.trip_total_quantity }}
                            </h6>
                          </td>
                        </tr>
                      </table>
                    </td>
                  </tr>
                </table>
              </td>
              <td style="padding-right: 20px">
                <table
                  style="
                    width: 100%;
                    border-collapse: collapse;
                    border: 1px solid #b6b6b6;
                  "
                >
                  <tr>
                    <td>
                      <table class="trip-sheet-table">
                        <tr>
                          <td>
                            <h4 class="trip-sheet-title">Vehicle Fill Ratio</h4>
                          </td>
                          <td style="width: 40px"></td>
                          <td></td>
                        </tr>
                      </table>
                      <table style="width: 100%; padding: 10px">
                        <tr>
                          <td>
                            <h5 class="trip-sheet-title-subtitle">Frozon</h5>
                          </td>
                          <td style="width: 40px"></td>
                          <td>
                            <h6 class="trip-sheet-title-subtitle-text">
                              {{ tripitemsheet.partitions.frozen }}%
                            </h6>
                          </td>
                        </tr>
                        <tr>
                          <td>
                            <h5 class="trip-sheet-title-subtitle">Chilled</h5>
                          </td>
                          <td style="width: 40px"></td>
                          <td>
                            <h6 class="trip-sheet-title-subtitle-text">
                              {{ tripitemsheet.partitions.chilled }}%
                            </h6>
                          </td>
                        </tr>
                        <tr>
                          <td>
                            <h5 class="trip-sheet-title-subtitle">Dry</h5>
                          </td>
                          <td style="width: 40px"></td>
                          <td>
                            <h6 class="trip-sheet-title-subtitle-text">
                              {{ tripitemsheet.partitions.dry }}%
                            </h6>
                          </td>
                        </tr>
                        <tr>
                          <td>
                            <h5 class="trip-sheet-title-subtitle">Unused</h5>
                          </td>
                          <td style="width: 40px"></td>
                          <td>
                            <h6
                              style="
                                padding: 0;
                                margin: 0;
                                font-family: 'Roboto';
                              "
                            >
                              {{ tripitemsheet.partitions.unused }}%
                            </h6>
                          </td>
                        </tr>
                      </table>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
          </table>

          <h3 class="trip-sheet-table-title">Order Information</h3>

          <table
            style="
              width: 99%;
              border-collapse: collapse;
              border: 1px solid #b6b6b6;
            "
          >
            <tr class="trip-sheet-table-head">
              <td>
                <h5>Sr.No</h5>
              </td>
              <td>
                <h5>Reference No.</h5>
              </td>
              <td>
                <h5>invoice No.</h5>
              </td>
              <td>
                <h5>No Of item</h5>
              </td>
              <td>
                <h5>Customer</h5>
              </td>
              <td>
                <h5>Contact No.</h5>
              </td>
              <td>
                <h5>Payment Type</h5>
              </td>
              <td>
                <h5>Amount</h5>
              </td>
              <td>
                <h5>Address</h5>
              </td>
              <td>
                <h5>Delivery Time</h5>
              </td>
            </tr>
            <tr
              class="trip-sheet-table-body"
              v-for="(order, i) in tripitemsheet.orders"
              :key="i"
            >
              <td>
                <h5>
                  {{ i + 1 }}
                </h5>
              </td>
              <td>
                <h5>
                  {{ order.reference_number }}
                </h5>
              </td>
              <td>
                <h5>
                  {{ order.invoice_number }}
                </h5>
              </td>
              <td>
                <h5>
                  {{ order.no_of_items }}
                </h5>
              </td>
              <td>
                <h5>
                  {{ order.customer_name }}
                </h5>
              </td>
              <td>
                <h5>
                  {{ order.contact_number }}
                </h5>
              </td>
              <td>
                <h5>
                  {{ order.payment_type }}
                </h5>
              </td>
              <td>
                <h5>
                  {{ order.order_value }}
                </h5>
              </td>
              <td>
                <h5>
                  {{ order.drop_address }}
                </h5>
              </td>
              <td>
                <h5>
                  {{ order.execution_date }}
                </h5>
              </td>
            </tr>
          </table>
          <!-- <br class="html2pdf__page-break" /> -->
          <h3 class="trip-sheet-table-title">SKU Information</h3>

          <table
            style="
              width: 99%;
              border-collapse: collapse;
              border: 1px solid #b6b6b6;
            "
          >
            <tr class="trip-sheet-table-head">
              <td>
                <h5>Sr.no</h5>
              </td>
              <td>
                <h5>invoice No.</h5>
              </td>
              <td>
                <h5>Item No.</h5>
              </td>
              <td>
                <h5>Item Type</h5>
              </td>
              <td>
                <h5>Item Description</h5>
              </td>
              <td>
                <h5>Qty</h5>
              </td>
              <td>
                <h5>Delivered Qty</h5>
              </td>
            </tr>
            <tr
              class="trip-sheet-table-body"
              v-for="(item, i) in tripitemsheet.order_items"
              :key="i"
            >
              <td>
                <h5>
                  {{ i + 1 }}
                </h5>
              </td>
              <td>
                <h5>
                  {{ item.invoice_number }}
                </h5>
              </td>
              <td>
                <h5>
                  {{ item.item_no }}
                </h5>
              </td>
              <td>
                <h5>
                  {{ item.storage_type }}
                </h5>
              </td>
              <td>
                <h5>
                  {{ item.item_description }}
                </h5>
              </td>
              <td>
                <h5>
                  {{ item.total_quantity }}
                </h5>
              </td>
            </tr>
          </table>
        </div>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>
<script>
import html2pdf from "~/node_modules/html2pdf.js";
export default {
  props: {
    value: Boolean,
    type: String,
  },
  data() {
    return {};
  },
  computed: {
    tripitemsheet() {
      return this.$store.state.trip.tripitemlist;
    },
    tripPDfDialog: {
      get() {
        return this.value;
      },
      set(value) {
        this.$emit("input", value);
      },
    },
  },
  methods: {
    closeDialogBox() {
      this.tripPDfDialog = false;
    },
    printLoadSheetPreview() {
      let element = null;
      let filename = "";
      element = document.getElementById("printtripSheet");
      filename = "trip-sheet.pdf";

      var opt = {
        margin: 0.25,
        filename: filename,
        image: { type: "jpeg", quality: 0.98 },
        html2canvas: { scale: 1 },
        jsPDF: { unit: "in", format: "letter", orientation: "landscape" },
      };
      html2pdf(element, opt);
    },
  },
};
</script>

<style lang="scss" scoped>
thead {
  display: table-header-group;
}
tfoot {
  display: table-row-group;
}
tr {
  page-break-inside: avoid;
}

.trip-sheet-title {
  padding: 0;
  margin: 0;
  color: #767779;
  font-size: 13px;
}
.trip-sheet-title {
  padding: 6px;
  margin: 0;
  color: white;
  font-size: 13px;
}
.trip-sheet-title-subtitle {
  padding: 2px 0px;
  margin: 0;
  color: map-get($colors-custom, "solid", "primary");
  font-family: "Roboto";
  font-weight: 500 !important;
  font-size: 9px;
}
.trip-sheet-title-subtitle-text {
  padding: 0;
  margin: 0;
  color: #767779;
  font-family: "Roboto";
}

.trip-sheet-table-title {
  color: map-get($colors-custom, "solid", "primary");
  margin: 20px 0px;
  font-size: 16px !important;
}

.trip-sheet-table {
  width: 100%;
  background-color: map-get($colors-custom, "solid", "primary");
  padding: 3px 4px;
}

.trip-sheet-table-head h5 {
  padding: 6px 7px;
  font-size: 11px;
  color: white;
}

.trip-sheet-table-head {
  background-color: map-get($colors-custom, "solid", "primary");
}
.trip-sheet-table-body h5 {
  font-size: 9px !important;
  font-family: "Roboto";
  font-weight: 500 !important;
  padding: 6px;
  margin: 0;
  color: #767779;
}
.set-color-title {
  color: map-get($colors-custom, "solid", "primary") !important;
}
.set-color-text {
  color: map-get($colors-custom, "solid", "grey") !important;
  font-weight: 400 !important;
  font-size: 12px;
}
</style>