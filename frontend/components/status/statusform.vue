<template>
  <v-dialog
    v-model="statusFormDialog"
    persistent
    scrollable
    width="50%"
    max-width="60%"
  >
    <v-card class="pa-6">
      <v-card-title class="mb-4">
        <span
          class="
            text-lg-subtitle-1 text-xl-h6 text-uppercase
            font-weight-black
            primary--text
          "
          >{{ formType }} Status</span
        >
        <v-spacer />
        <v-btn
          depressed
          text
          small
          icon
          class="primary-text"
          @click="closeDialog()"
        >
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>
      <v-form
        v-if="statusFormDialog"
        v-model="isValid"
        ref="statusForm"
        id="statusForm"
      >
        <v-card-text>
          <v-row>
            <v-col cols="6" lg="4">
              <v-select
                outlined
                hide-details="auto"
                :items="statusCategoty"
                item-text="name"
                item-value="value"
                :rules="[(v) => !!v || 'Status Category is a required']"
                :value="statusDetails.status_category"
                readonly
                class="background-white mt-1"
                label="Status Category *"
                @change="syncData($event, 'status_category')"
                :menu-props="{ offsetY: true }"
              ></v-select>
            </v-col>
            <v-col cols="6" lg="4">
              <v-text-field
                outlined
                hide-details="auto"
                class="background-white mt-1"
                label="Status Name *"
                ref="statusName"
                :value="statusDetails.name"
                :error-messages="this.error.name"
                @input="syncData($event, 'name')"
                :rules="[(v) => !!v || 'Status Name is a required']"
              ></v-text-field>
            </v-col>
            <v-col cols="6" lg="4">
              <v-select
                outlined
                hide-details="auto"
                :items="statusType"
                item-text="name"
                item-value="value"
                :value="statusDetails.keyword"
                class="background-white mt-1"
                label="Status Type *"
                :rules="[(v) => !!v || 'Status Type is a required']"
                @change="syncData($event, 'keyword')"
                :menu-props="{ offsetY: true }"
              ></v-select>
            </v-col>
            <v-col cols="12">
              <v-textarea
                outlined
                hide-details="auto"
                class="background-white"
                label="Description"
                :value="statusDetails.description"
                @input="syncData($event, 'description')"
              ></v-textarea>
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions class="pb-4 pt-4 d-flex justify-center">
          <v-btn class="primary mr-4" @click="clear()" v-show="formType == 'add'">
            <span>Reset</span>
          </v-btn>
          <v-btn
            class="primary"
            :disabled="!isValid"
            @click.prevent="submitStatusForm()"
          >
            <span>Submit</span>
          </v-btn>
        </v-card-actions>
      </v-form>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  props: {
    value: Boolean,
    formType: { type: String, default: "add" },
  },
  data() {
    return {
      error: {},
      isValid: false,
      nonFieldError: [],
      radioGroup: "active",
      statusCategoty: [
        {
          name: "Order",
          value: "order",
        },
        {
          name: "Driver",
          value: "driver",
        },
        {
          name: "Trip",
          value: "trip",
        },
        {
          name: "Vehicle",
          value: "vehicle",
        },
      ],
      statusType: [
        {
          name: "Delivered",
          value: "successful",
        },
        {
          name: "Returned",
          value: "failed",
        },
      ],
    };
  },
  computed: {
    statusDetails: {
      get() {
        return this.$store.state.status.statusDetail;
      },
      set(value) {
        this.$store.commit("status/SET_STATUS_DETAILS", value);
      },
    },
    statusFormDialog: {
      get() {
        return this.value;
      },
      set(value) {
        this.$emit("input", value);
      },
    },
  },
  methods: {
    closeDialog() {
      this.statusFormDialog = false;
      this.clear();
    },
    submitStatusForm() {
      if (this.formType == "add") {
        this.$store
          .dispatch("status/ADD_STATUS", this.statusDetails)
          .then((response) => {
            this.closeDialog();
            this.$notifier.showMessage({
              content: "Status Added successfully",
              color: "success",
            });
          })
          .catch((err) => {
            if ("non_field_errors" in err) {
              this.nonFieldError = err.non_field_errors;
            }
            this.error = err;
          });
      } else {
        this.$store
          .dispatch("status/UPDATE_STATUS_DETAILS", this.statusDetails)
          .then((response) => {
            this.closeDialog();
            this.$notifier.showMessage({
              content: "Status Updated successfully",
              color: "success",
            });
          })
          .catch((err) => {
            if ("non_field_errors" in err) {
              this.nonFieldError = err.non_field_errors;
            }
            this.error = err;
          });
      }
    },
    syncData(input_value, key) {
      if (this.error[key]) {
        this.error[key] = null;
        delete this.error[key];
      }
      this.$store.commit("status/SYNC_STATUS_FORM_DETAILS", {
        key: key,
        value: input_value,
      });
    },
    clear() {
      this.statusDetails = {
        added_by: null,
        description: null,
        keyword: "failed",
        name: null,
        status_category: "order",
      };
      this.$refs.statusName.reset();
    },
  },
};
</script>