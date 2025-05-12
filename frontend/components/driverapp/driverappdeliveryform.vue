<template>
  <v-dialog v-model="openDelivereditemForm" width="500" persistent scrollable>
    <v-form v-model="isValid" ref="deliveryForm">
      <v-card>
        <v-card-title class="primary py-0 pl-5 pr-2" style="height: 45px">
          <h5 class="white--text">Delivered</h5>
          <v-spacer></v-spacer>
          <v-btn color="white" text @click="closeDeliveryForm">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>

        <v-card-text>
          <v-row no-gutters>
            <v-col cols="5" class="d-flex justify-end align-baseline"> </v-col>
            <v-col cols="12" class="my-5 d-flex align-center">
              <h3 class="primary--text">Items</h3>
              <v-spacer></v-spacer>
              <v-file-input
                type="file"
                id="file"
                v-model="file"
                style="display: none"
                @change="uploadAttachment($event, orderDetails.id)"
              ></v-file-input>
              <v-btn
                dense
                class="primary"
                @click="getFile"
                style="font-size: 12px"
              >
                Upload POD
              </v-btn>
            </v-col>

            <v-col cols="12" class="mt-2">
              <div>
                <p class="blue--text text-capitalize">
                  <b>Note :</b> you can change Qty Delivered
                </p>
              </div>
              <v-row no-gutters>
                <v-col cols="4" class="ba text-center light_grey"
                  >Item Name</v-col
                >
                <v-col cols="4" class="ba text-center light_grey">Qty</v-col>
                <v-col cols="4" class="ba text-center light_grey"
                  >Qty Delivered</v-col
                >
              </v-row>
              <v-row
                no-gutters
                v-for="(item, itemIndex) in orderDetails.order_items"
                :key="itemIndex"
              >
                <v-col
                  cols="4"
                  class="ba text-center py-1 d-flex justify-center align-center"
                >
                  {{ item.item_no }}
                </v-col>
                <v-col
                  cols="4"
                  class="ba text-center py-1 d-flex justify-center align-center"
                >
                  {{ item.original_quantity }}
                </v-col>
                <v-col cols="4" class="ba text-center">
                  <v-text-field
                    hide-details="auto"
                    :id="'item' + itemIndex"
                    outlined
                    dense
                    type="number"
                    :rules="[
                      (value) => !!value || 'This Field is Required.',
                      (value) =>
                        (value && value <= item.original_quantity) ||
                        `Less ${item.original_quantity} characters`,
                    ]"
                    @input="
                      itemChange(orderDetails.total_quantity),
                        syncOrderItemData(
                          $event,
                          'delivered_quantity',
                          itemIndex
                        )
                    "
                    :value="item.delivered_quantity"
                    class="w-100 py-1 text-center"
                  />
                </v-col>
              </v-row>
            </v-col>
            <v-col
              cols="12"
              class="mt-4"
              v-if="orderDetails.payment_type == 'cod'"
            >
              <v-row no-gutters>
                <v-col cols="12">
                  <h3 class="primary--text">COD Amount</h3>
                </v-col>
                <v-col cols="12" class="d-flex justify-end align-baseline my-4">
                  <v-text-field
                    type="number"
                    dense
                    hide-details="auto"
                    outlined
                    :rules="[(v) => !!v || 'Cod Amount is required']"
                    v-model.number="codAmount"
                    label="Amount"
                    placeholder="0.00 AED"
                  ></v-text-field>
                </v-col>
              </v-row>
            </v-col>
            <v-col cols="12" v-if="isReasonVisible">
              <v-row>
                <v-col cols="12" class="mt-5">
                  <h3 class="primary--text">Reason</h3>
                </v-col>
                <v-col cols="12">
                  <v-select
                    outlined
                    hide-details="auto"
                    dense
                    v-model="selectPartiallyReason"
                    :rules="[(v) => !!v || 'Reason is required']"
                    label="Select reason"
                    :items="partiallyReason"
                    item-text="title"
                    item-value="value"
                    name="project"
                    class="background-white"
                    :menu-props="{ offsetY: true }"
                  ></v-select>
                </v-col>
              </v-row>
            </v-col>

            <v-col cols="12" class="my-5">
              <h3 class="primary--text">Driver Remark</h3>
            </v-col>
            <v-col cols="12">
              <v-textarea
                v-model="driverRemakers"
                outlined
                label="Comment here..."
              ></v-textarea>
            </v-col>
          </v-row>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions class="d-flex justify-end px-4 py-2 light_grey">
          <v-btn
            @click.prevent="submitForm()"
            :disabled="!isValid"
            class="primary"
            >submit</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-form>
  </v-dialog>
</template>

<script>
import image from "@/static/user.png";
export default {
  props: {
    value: Boolean,
  },
  data() {
    return {
      isValid: false,
      file: null,
      image: image,
      codAmount: null,
      selectPartiallyReason: null,
      driverRemakers: null,
      isReasonVisible: false,
      radioGroup: 1,
    };
  },
  computed: {
    partiallyReason() {
      return this.$store.state.driverapp.partiallyReason.map((item, i) => {
        return { title: item.name, value: item.id };
      });
    },
    orderDetails() {
      return this.$store.state.driverapp.orderDetails;
    },
    openDelivereditemForm: {
      get() {
        return this.value;
      },
      set(value) {
        this.$emit("input", value);
      },
    },
  },
  methods: {
    getFile() {
      document.getElementById("file").click();
    },
    uploadAttachment(input, id) {
      let newForm = new FormData();
      newForm.append("attachment", input);
      newForm.append("attachment_type", "pod");
      let payload = {
        id: id,
        data: newForm,
      };

      if (input) {
        this.$store
          .dispatch("driverapp/DRIVER_ATTACHMENT_UPLOAD", payload)
          .then((result) => {
            alert("Attachment Upload Successfuly!");
            this.$store.dispatch("driverapp/GET_DRIVER_DETAILS").then((res) => {
              if (res.trip != null) {
                this.$store.dispatch("driverapp/GET_TRIP_DETAILS", res.trip);
              }
            });
          })
          .catch((err) => {
            console.error(err);
          });
      }
    },
    submitForm() {
      let originalItem = this.orderDetails.order_items.map((item, i) => {
        return {
          item_no: item.item_no,
          quantity: item.original_quantity,
          delivered_quantity: item.delivered_quantity,
        };
      });
      let payload = {
        id: this.orderDetails.id,
        data: {
          status: "successful",
          items: originalItem,
          driver_remarks: this.driverRemakers,
        },
      };
      if (this.orderDetails.payment_type == "cod") {
        payload.data.payment_collected = parseFloat(this.codAmount);
      }

      if (this.selectPartiallyReason != null) {
        payload.data.status_keyword = this.selectPartiallyReason;
      }

      this.$store
        .dispatch("driverapp/DELIVERED_ORDER", payload)
        .then((result) => {
          this.isReasonVisible = false;
          this.$forceUpdate();

          this.$store.dispatch("driverapp/GET_DRIVER_DETAILS").then((res) => {
            if (res.trip != null) {
              this.$store.dispatch("driverapp/GET_TRIP_DETAILS", res.trip);
            }
          });

          this.$notifier.showMessage({
            content: "Delivered Order Successfuly!",
            color: "success",
          });
          setTimeout(() => {
            this.closeDeliveryForm();
          }, 200);
        })
        .catch((err) => {
          console.error(err);
        });
    },
    syncOrderItemData(value, key, index) {
      this.$store.commit("driverapp/SYNC_ORDER_ITEM", {
        value: value,
        key: key,
        index: index,
      });
    },
    itemChange(totalQuantity) {
      let total = 0;
      this.orderDetails.order_items.forEach((element, i) => {
        let number = parseFloat(document.getElementById("item" + i).value);
        if (number) {
          total += number;
        } else {
          total += 0;
        }
      });
      if (total < totalQuantity) {
        this.isReasonVisible = true;
      } else {
        this.isReasonVisible = false;
      }
    },
    closeDeliveryForm() {
      this.selectPartiallyReason = null;
      this.driverRemakers = null;
      this.openDelivereditemForm = false;
    },
  },
};
</script>