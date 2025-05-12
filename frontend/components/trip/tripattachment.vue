<template>
  <v-dialog
    v-model="opentripAttachmentDialog"
    scrollable
    max-width="60%"
    overlay-opacity="0.9"
  >
    <v-card class="pb-12 pr-12 pl-12">
      <v-card-title>
        <span> </span>
        <v-spacer />
        <v-btn
          depressed
          text
          small
          icon
          class="primary-text mb-n16"
          style="z-index: 2"
          @click="closeDialog()"
        >
          <v-icon>mdi-close</v-icon>
        </v-btn>

        <div>
          <v-btn
            class="white"
            x-large
            @click="downloadTripAttachment"
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
      </v-card-title>
      <v-card-text
        id="tripPodAttachment"
        class="px-0 overflow-y-auto"
        style="position: relative"
      >
        <div>
          <div style="background-color: white; position: sticky; top: 0">
            <img
              src="../../static/logo.png"
              style="height: 40px; margin-bottom: 20px"
            />
          </div>
          <table class="trip-attachments-table">
            <tr>
              <td>
                <h4 class="trip-attachments-table-title">Trip Details</h4>
              </td>
            </tr>
          </table>

          <table
            class="trip-attachments-table-light-grey"
            border="0"
            style="table-layout: fixed; width: 100%"
          >
            <tr>
              <td style="padding-right: 20px">
                <table style="width: 100%; border-collapse: collapse">
                  <tr>
                    <td>
                      <table style="width: 100%; padding: 10px">
                        <tr>
                          <td>
                            <h5 class="trip-attachments-table-sub-title">
                              Reference Number
                            </h5>
                          </td>
                          <td style="width: 40px"></td>
                          <td>
                            <h6 class="trip-attachments-table-sub-text">
                              {{ currentTrip.reference_number }}
                            </h6>
                          </td>
                        </tr>
                        <tr>
                          <td>
                            <h5 class="trip-attachments-table-sub-title">
                              Number of orders
                            </h5>
                          </td>
                          <td style="width: 40px"></td>
                          <td>
                            <h6 class="trip-attachments-table-sub-text">
                              {{ currentTrip.order_count.total }}
                            </h6>
                          </td>
                        </tr>
                        <tr>
                          <td>
                            <h5 class="trip-attachments-table-sub-title">
                              Total Quantity
                            </h5>
                          </td>
                          <td style="width: 40px"></td>
                          <td>
                            <h6 class="trip-attachments-table-sub-text">
                              {{ currentTrip.trip_statistics.total_items }}
                            </h6>
                          </td>
                        </tr>
                        <tr>
                          <td>
                            <h5 class="trip-attachments-table-sub-title">
                              Vehicle Number
                            </h5>
                          </td>
                          <td style="width: 40px"></td>
                          <td>
                            <h6 class="trip-attachments-table-sub-text">
                              {{ currentTrip.vehicle }}
                            </h6>
                          </td>
                        </tr>
                      </table>
                    </td>
                  </tr>
                </table>
              </td>
              <td style="padding-right: 20px">
                <table style="width: 100%; border-collapse: collapse">
                  <tr>
                    <td>
                      <table style="width: 100%; padding: 10px">
                        <tr>
                          <td>
                            <h5 class="trip-attachments-table-sub-title">
                              Trip Date
                            </h5>
                          </td>
                          <td style="width: 40px"></td>
                          <td>
                            <h6 class="trip-attachments-table-sub-text">
                              {{ currentTrip.trip_date }}
                            </h6>
                          </td>
                        </tr>
                        <tr>
                          <td>
                            <h5 class="trip-attachments-table-sub-title">
                              Driver Name
                            </h5>
                          </td>
                          <td style="width: 40px"></td>
                          <td>
                            <h6 class="trip-attachments-table-sub-text">
                              {{ currentTrip.driver }}
                            </h6>
                          </td>
                        </tr>
                        <tr>
                          <td>
                            <h5 class="trip-attachments-table-sub-title">
                              Driver Number
                            </h5>
                          </td>
                          <td style="width: 40px"></td>
                          <td>
                            <h6 class="trip-attachments-table-sub-text">
                              {{ currentTrip.driver_number }}
                            </h6>
                          </td>
                        </tr>
                        <tr>
                          <td>
                            <h5 class="trip-attachments-table-sub-title">
                              Helper name
                            </h5>
                          </td>
                          <td style="width: 40px"></td>
                          <td>
                            <h6 class="trip-attachments-table-sub-text">
                              {{ currentTrip.helper_name }}
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

          <table
            border="0"
            class="trip-attachments-table"
            style="margin-top: 40px"
          >
            <tr>
              <td>
                <h4 class="trip-attachments-table-title">Trip Attachments</h4>
              </td>
            </tr>
          </table>

          <div v-for="(order, i) in currentTrip.trip_orders" :key="i">
            <table
              border="0"
              style="padding: 10px 0px; width: 100%"
              v-if="order.pod_attachments.length !== 0"
            >
              <tr>
                <td>
                  <table
                    border="0"
                    class="trip-attachments-table-grey"
                    style="margin-top: 40px"
                  >
                    <tr>
                      <td>
                        <h4 class="trip-attachments-table-title">
                          {{ order.reference_number }}
                        </h4>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
              <tr>
                <td>
                  <table
                    style="padding: 10px 20px; width: 100%"
                    class="trip-attachments-table-light-grey"
                  >
                    <tr>
                      <td>
                        <table
                          border="0"
                          style="table-layout: fixed; width: 100%"
                        >
                          <tr>
                            <td>
                              <h4 class="trip-attachments-table-sub-title">
                                Order Type
                              </h4>
                            </td>
                            <td>
                              <h4 class="trip-attachments-table-title-grey">
                                {{ order.order_type }}
                              </h4>
                            </td>

                            <td>
                              <h4 class="trip-attachments-table-sub-title">
                                Order Status
                              </h4>
                            </td>
                            <td>
                              <h4 class="trip-attachments-table-title-grey">
                                {{
                                  order.status == "successful"
                                    ? "Delivered"
                                    : order.status == "failed"
                                    ? "Returned"
                                    : order.status == "partially_delivered"
                                    ? "Partially Delivered"
                                    : order.status == "pickedup"
                                    ? "Shipped"
                                    : order.status
                                }}
                              </h4>
                            </td>
                          </tr>
                          <tr>
                            <td>
                              <h4 class="trip-attachments-table-sub-title">
                                Customer Name
                              </h4>
                            </td>
                            <td>
                              <h4 class="trip-attachments-table-title-grey">
                                {{ order.customer_name }}
                              </h4>
                            </td>

                            <td>
                              <h4 class="trip-attachments-table-sub-title">
                                Quantity
                              </h4>
                            </td>
                            <td>
                              <h4 class="trip-attachments-table-title-grey">
                                {{ order.no_of_items }}
                              </h4>
                            </td>
                          </tr>
                          <tr>
                            <td>
                              <h4 class="trip-attachments-table-sub-title">
                                Address
                              </h4>
                            </td>
                            <td colspan="3">
                              <h4 class="trip-attachments-table-title-grey">
                                {{ order.address }}
                              </h4>
                            </td>
                          </tr>
                        </table>
                      </td>
                    </tr>
                    <tr>
                      <td>
                        <table
                          border="0"
                          class="trip-attachments-table-light-grey"
                        >
                          <tr>
                            <td>
                              <div
                                v-for="(image, i) in order.pod_attachments"
                                :key="i"
                              >
                                <img
                                  :src="image.url"
                                  style="
                                    margin: 20px 0px;
                                    padding: 20px;
                                    max-width: 100%;
                                    max-height: 550px;
                                  "
                                />
                              </div>
                            </td>
                          </tr>
                        </table>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>
          </div>
        </div>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>
<script>
import html2pdf from "~/node_modules/html2pdf.js";
import authHeader from "~/store/authHeader";
export default {
  props: {
    value: Boolean,
  },
  computed: {
    currentTrip() {
      return this.$store.state.trip.currentTrip;
    },
    opentripAttachmentDialog: {
      get() {
        return this.value;
      },
      set(value) {
        return this.$emit("input", value);
      },
    },
  },

  methods: {
    downloadTripAttachment() {
      this.openTripAttachmentDialog = true;

      let filename = "trip-pod-attachments.pdf";

      var opt = {
        margin: 0.25,
        filename: filename,
        pagebreak: { mode: ["avoid-all", "css", "legacy"] },
        image: { type: "jpeg", quality: 0.98 },
        html2canvas: {
          scale: 1,
          dpi: 300,
          letterRendering: true,
          useCORS: true,
        },
        jsPDF: { unit: "in", format: "a4", orientation: "portrait" },
      };
      let element = document.getElementById("tripPodAttachment");
      html2pdf().set(opt).from(element).save();
    },

    closeDialog() {
      this.opentripAttachmentDialog = false;
    },
  },
};
</script>

<style lang="scss" scoped>
@import "@/assets/scss/variables.scss";

.trip-attachments-table {
  width: 100%;
  background-color: map-get($colors-custom, "solid", "primary");
  // padding: 3px 4px;
}
.trip-attachments-table-grey {
  width: 100%;
  background-color: map-get($colors-custom, "solid", "primary");
  padding: 0px 4px;
}
.trip-attachments-table-light-grey {
  width: 100%;
  background-color: map-get($colors-custom, "light", "light_grey");
  padding: 3px 4px;
  border: 1px solid map-get($colors-custom, "light", "light_grey") !important ;
}
.trip-attachments-table-title {
  padding: 8px 16px;
  margin: 0;
  color: white;
  font-size: 13px;
}
.trip-attachments-table-title-grey {
  color: map-get($colors-custom, "solid", "grey");
  padding: 2px 0px;
  margin: 0;
  font-family: "Roboto";
  font-weight: 500 !important;
  font-size: 9px;
}
.trip-attachments-table-sub-title {
  padding: 2px 0px;
  margin: 0;
  color: map-get($colors-custom, "solid", "primary");
  font-family: "Roboto";
  font-weight: 500 !important;
  font-size: 9px;
  letter-spacing: 0.5px;
}
.trip-attachments-table-sub-text {
  padding: 0;
  margin: 0;
  color: #767779;
  font-family: "Roboto";
}
</style>