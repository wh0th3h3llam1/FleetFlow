<template>
  <v-dialog v-model="openReturnOrderForm" width="500">
    <v-form v-model="isValid">
      <v-card>
        <v-card-title class="primary py-0 pl-5 pr-2" style="height: 45px">
          <h5 class="white--text">Return</h5>
          <v-spacer></v-spacer>
          <v-btn color="white" text @click="closeReturnForm">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>

        <v-card-text>
          <v-row no-gutters>
            <v-col cols="12" class="py-4">
              <h3 class="primary--text">Reason</h3>
            </v-col>
            <v-col cols="12">
              <v-select
                outlined
                hide-details="auto"
                dense
                v-model="returnReason"
                label="Select Reason"
                :items="failedReasons"
                 :rules="[(v) => !!v || 'Reason is required']"
                item-text="title"
                item-value="value"
                name="project"
                class="background-white"
                :menu-props="{ offsetY: true }"
              ></v-select>
            </v-col>
            <v-col cols="12" class="my-5">
              <h3 class="primary--text">Driver Remark</h3>
            </v-col>
            <v-col cols="12">
              <v-textarea
                v-model="driverRamrks"
                outlined
                 :rules="[(v) => !!v || 'Remarks is required']"
                label="Comment here..."
              ></v-textarea>
            </v-col>
          </v-row>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions class="d-flex justify-end px-4 py-2 light_grey">
          <v-btn
            class="primary"
            :disabled="!isValid"
            @click.prevent="submitForm(orderDetails.id)"
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
      driverRamrks: null,
      isValid: false,
      returnReason: null,
      image: image,
    };
  },
  computed: {
    failedReasons() {
      return this.$store.state.driverapp.failedReasons.map((item, i) => {
        return { title: item.name, value: item.id };
      });
    },
    orderDetails() {
      return this.$store.state.driverapp.orderDetails;
    },
    openReturnOrderForm: {
      get() {
        return this.value;
      },
      set(value) {
        this.$emit("input", value);
      },
    },
  },
  methods: {
    submitForm(id) {
      let payload = {
        id: id,
        data: {
          status: "failed",
          status_keyword: this.returnReason,
          driver_remarks: this.driverRamrks,
        },
      };
      this.$store
        .dispatch("driverapp/DELIVERED_ORDER", payload)
        .then((result) => {
          this.$store.dispatch("driverapp/GET_DRIVER_DETAILS").then((res) => {
            if (res.trip != null) {
              this.$store.dispatch("driverapp/GET_TRIP_DETAILS", res.trip);
            }
          });

          this.$notifier.showMessage({
            content: "Returned Order Successfuly!",
            color: "success",
          });
          this.closeReturnForm();
        })
        .catch((err) => {
          console.error(err);
        });
    },
    closeReturnForm() {
      this.clear();
      this.openReturnOrderForm = false;
    },
    clear() {
      this.returnReason = null;
      this.driverRamrks = null;
    },
  },
};
</script>