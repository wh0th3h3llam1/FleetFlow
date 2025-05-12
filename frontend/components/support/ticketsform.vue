<template>
  <v-dialog
    v-model="ticketFormDialog"
    scrollable
    persistent
    width="60%"
    max-width="70%"
  >
    <v-card>
      <v-card-title class="background-primary text-white px-3 py-2">
        <span
          class="text-lg-subtitle-1 text-xl-h6 text-uppercase font-weight-black"
        >
          {{ formType }} Ticket
        </span>
        <v-spacer />
        <v-btn
          depressed
          text
          small
          icon
          class="text-white"
          @click="closeDialog()"
        >
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>

      <v-card-text>
        <v-form
          v-if="ticketFormDialog"
          v-model="isValid"
          ref="ticketForm"
          id="ticketForm"
        >
          <v-row class="pt-4">
            <v-col cols="12">
              <v-text-field
                hide-details="auto"
                label="Title*"
                name="title"
                :value="ticketDetails.title"
                :rules="[(v) => !!v || 'Title  is Required']"
                prepend-icon=""
                @input="syncData($event, 'title')"
                outlined
              ></v-text-field>
            </v-col>

            <v-col cols="6" lg="4">
              <v-select
                outlined
                hide-details="auto"
                class="background-white"
                :items="moduleName"
                item-text="title"
                name="module"
                item-value="value"
                label="Module Name*"
                :value="ticketDetails.module"
                :rules="[(v) => !!v || 'Module Name is Required']"
                @input="syncData($event, 'module')"
                :menu-props="{ offsetY: true }"
              ></v-select>
            </v-col>

            <v-col cols="6" lg="4">
              <v-select
                outlined
                hide-details="auto"
                class="background-white"
                :items="priority"
                name="priority"
                :value="ticketDetails.priority"
                item-text="title"
                item-value="value"
                label="Priority*"
                :rules="[(v) => !!v || 'Priority  is Required']"
                @input="syncData($event, 'priority')"
                :menu-props="{ offsetY: true }"
              ></v-select>
            </v-col>

            <v-col cols="6" lg="4" v-if="formType == 'add'">
              <v-file-input
                v-model="file"
                multiple="multiple"
                hide-details="auto"
                label="Upload Document*"
                :rules="
                  formType == 'add'
                    ? [(v) => !!v || 'Upload Document  is Required']
                    : []
                "
                prepend-inner-icon="mdi-attachment mdi-rotate-90"
                prepend-icon=""
                @change="syncData($event, 'ticket_attachments')"
                outlined
              ></v-file-input>
            </v-col>
            <v-col cols="6" lg="4" v-if="formType == 'edit'">
              <v-select
                hide-details="auto"
                :items="ticketStatus"
                name="status"
                :value="ticketDetails.status"
                item-text="title"
                item-value="value"
                label="Status"
                v-if="formType == 'edit'"
                @change="syncData($event, 'status')"
                :menu-props="{ offsetY: true }"
                outlined
              ></v-select>
            </v-col>

            <v-col cols="12">
              <v-textarea
                hide-details="auto"
                label="Description*"
                name="description"
                :value="ticketDetails.description"
                :rules="[(v) => !!v || 'Description  is Required']"
                prepend-icon=""
                outlined
                @input="syncData($event, 'description')"
              ></v-textarea>
            </v-col>
          </v-row>
        </v-form>
      </v-card-text>
      <v-card-actions class="pa-4 background-light_grey d-flex justify-end">
        <v-btn
          type="submit"
          class="primary text-uppercase mr-3"
          :disabled="!isValid"
          @click.prevent="submitTicketForm()"
        >
          <span>Submit</span>
        </v-btn>
        <v-btn
          type="reset"
          v-if="formType == 'add'"
          @click="clear()"
          class="primary text-uppercase"
        >
          <span>Reset</span>
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  props: {
    value: Boolean,
    formType: {
      type: String,
      default: "add",
    },
  },
  data() {
    return {
      error: {},
      file: null,
      nonFieldError: [],
      isValid: false,
      formData: null,
      moduleName: [
        {
          title: "Customer",
          value: "customer",
        },
        {
          title: "Order",
          value: "order",
        },
        {
          title: "Trip",
          value: "trip",
        },
        {
          title: "Trip Planning",
          value: "trip_planning",
        },
        {
          title: "Report",
          value: "report",
        },
        {
          title: "Driver",
          value: "driver",
        },
        {
          title: "Project",
          value: "project",
        },
        {
          title: "Zone",
          value: "zone",
        },
        {
          title: "Vehicle",
          value: "vehicle",
        },
        {
          title: "Item master",
          value: "item_master",
        },
        {
          title: "Other",
          value: "other",
        },
      ],
      priority: [
        {
          title: "High",
          value: "high",
        },
        {
          title: "Medium",
          value: "medium",
        },
        {
          title: "Low",
          value: "low",
        },
      ],
      ticketStatus: [
        {
          title: "Open",
          value: "open",
        },
        {
          title: "In Progress",
          value: "in_progress",
        },
        {
          title: "Resolved",
          value: "resolved",
        },
        {
          title: "Cancelled",
          value: "cancelled",
        },
        {
          title: "Closed",
          value: "closed",
        },
      ],
    };
  },
  computed: {
    ticketDetails: {
      get() {
        return this.$store.state.support.ticketDetails;
      },
      set(value) {
        this.$store.commit("support/SET_TICKET_DETAILS", value);
      },
    },
    ticketFormDialog: {
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
      this.clear();
      this.ticketFormDialog = false;
    },

    imageFileCheck() {
      if (this.file) {
        this.file.forEach((file, i) => {
          let extension = file.name.slice(
            (Math.max(0, file.name.lastIndexOf(".")) || Infinity) + 1
          );
          if (extension == "png" || extension == "jpeg" || extension == "jpg") {
            return true;
          } else {
            this.$notifier.showMessage({
              content: `Select file(s) are not supported.Support file Types: PNG, JPEG, JPG `,
              color: "error",
            });

            this.file = [];
            return false;
          }
        });
      }
    },
    genrateFormData(data) {
      const formData = new FormData();
      Object.keys(data).forEach((key) => {
        if (key != "ticket_attachments") {
          formData.set(key, data[key]);
        }
      });
      return formData;
    },
    submitTicketForm() {
      let postData = this.genrateFormData(this.ticketDetails);

      if (this.file != null) {
        this.ticketDetails.ticket_attachments.forEach((file) => {
          postData.append("ticket_attachments", file);
        });
      }

      if (this.formType == "add") {
        this.$store
          .dispatch("support/ADD_TICKET", postData)
          .then((response) => {
            this.$notifier.showMessage({
              content: "Successfully Created Ticket",
              color: "success",
            });
            this.closeDialog();
          })
          .catch((err) => {
            if ("non_field_errors" in err) {
              this.nonFieldError = err.non_field_errors;
            }
            this.error = err;
          });
      } else {
        let payload = {
          id: this.ticketDetails.id,
          data: postData,
        };
        this.$store
          .dispatch("support/UPDATE_TICKET", payload)
          .then((response) => {
            this.$notifier.showMessage({
              content: "Updated ticket Successfully",
              color: "success",
            });
            this.closeDialog();
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
      this.imageFileCheck();

      if (this.error[key]) {
        this.error[key] = null;
        delete this.error[key];
      }
      this.$store.commit("support/SYNC_TICKET_FORM_DETAILS", {
        key: key,
        value: input_value,
      });
    },
    clear() {
      this.ticketDetails = {
        description: null,
        module: null,
        priority: null,
        ticket_attachments: [],
        ticket_comments: [],
      };
      if(this.$refs.ticketForm) {
        this.$refs.ticketForm.reset();
      }
    },
  },
  mounted() {
    this.clear();
  }
};
</script>
