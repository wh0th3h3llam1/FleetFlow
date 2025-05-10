<template>
  <v-dialog v-model="itemFormDialog" persistent scrollable max-width="60%">
    <v-card class="pa-4">
      <v-card-title>
        <span
          class="
            text-lg-subtitle-1 text-xl-h6 text-uppercase
            font-weight-black
            primary--text
            mb-4
          "
          >{{ formType }} Item</span
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
      <v-card-text v-if="itemFormDialog" class="pt-3">
        <v-alert v-if="nonFieldError.length" dense type="error">
          <v-list
            class="pa-0"
            dense
            style="background: inherit !important"
            v-for="(error, i) in nonFieldError"
            :key="i"
          >
            <v-list-item dense style="min-height: 20px !important">
              <span>{{ i }} .</span><span>{{ error }}</span>
            </v-list-item>
          </v-list>
        </v-alert>
        <v-form ref="itemForm" v-model="isValid">
          <v-row>
            <v-col cols="6" lg="4">
              <v-text-field
                hide-details="auto"
                outlined
                label="Item name*"
                class="background-white"
                :rules="[
                  (v) =>
                    (!!v && v.trim().length > 0) || 'Item Name is required',
                ]"
                :error-messages="error.item_description"
                :value="itemFormDetails.item_description"
                @input="syncData($event, 'item_description')"
              ></v-text-field>
            </v-col>
            <v-col cols="6" lg="4">
              <v-text-field
                outlined
                hide-details="auto"
                :rules="[(v) => !!v || 'Item number is required']"
                type="text"
                class="background-white"
                label="Item Number*"
                :error-messages="error.item_no"
                :value="itemFormDetails.item_no"
                @input="syncData($event, 'item_no')"
              ></v-text-field>
            </v-col>
            <v-col cols="12" lg="2"></v-col>
            <v-col cols="6" lg="3">
              <v-select
                outlined
                hide-details="auto"
                :rules="[(v) => !!v || 'Item Group is required']"
                type="number"
                class="background-white"
                label="Item Group*"
                :items="storageType"
                item-text="title"
                item-value="value"
                :error-messages="error.storage_type"
                :value="itemFormDetails.storage_type"
                @change="syncData($event, 'storage_type')"
                :menu-props="{ offsetY: true }"
              ></v-select>
            </v-col>
            <v-col cols="6" lg="3">
              <v-select
                outlined
                hide-details="auto"
                :rules="[(v) => !!v || 'Unit is required']"
                class="background-white"
                label="Unit*"
                :items="unitType"
                item-text="text"
                item-value="value"
                :value="itemFormDetails.unit"
                :error-messages="error.unit"
                @change="syncData($event, 'unit')"
                 :menu-props="{ offsetY: true }"
              ></v-select>
            </v-col>
            <v-col cols="6" lg="3">
              <v-text-field
                outlined
                hide-details="auto"
                :rules="[(v) => !!v || 'Case Factor is required']"
                type="number"
                class="background-white"
                label="Case Factor*"
                min="0"
                :value="itemFormDetails.case_factor"
                :error-messages="error.case_factor"
                @input="syncData($event, 'case_factor')"
              ></v-text-field>
            </v-col>
            <v-col cols="6" lg="3">
              <v-text-field
                outlined
                hide-details="auto"
                :rules="[(v) => !!v || 'Length is required']"
                step="0.00001"
                type="number"
                class="background-white"
                label="Length*"
                min="0.00000"
                :value="itemFormDetails.length"
                :error-messages="error.length"
                @input="syncData($event, 'length')"
              ></v-text-field>
            </v-col>
            <v-col cols="6" lg="3">
              <v-text-field
                outlined
                hide-details="auto"
                :rules="[(v) => !!v || 'Width is required']"
                step="0.00001"
                type="number"
                class="background-white"
                label="Width*"
                min="0.00000"
                :value="itemFormDetails.width"
                :error-messages="error.width"
                @input="syncData($event, 'width')"
              ></v-text-field>
            </v-col>
            <v-col cols="6" lg="3">
              <v-text-field
                outlined
                hide-details="auto"
                :rules="[(v) => !!v || 'Height is required']"
                step="0.00001"
                type="number"
                class="background-white"
                label="Height*"
                min="0.00000"
                :value="itemFormDetails.height"
                :error-messages="error.height"
                @input="syncData($event, 'height')"
              ></v-text-field>
            </v-col>
            <v-col cols="6" lg="3">
              <v-text-field
                outlined
                hide-details="auto"
                :rules="[(v) => !!v || 'Volume is required']"
                type="number"
                class="background-white"
                label="Volume (CBM)*"
                min="0.0000000"
                :value="itemFormDetails.cbm"
                :error-messages="error.cbm"
                @input="syncData($event, 'cbm')"
              ></v-text-field>
            </v-col>
            <v-col cols="6" lg="3">
              <v-text-field
                outlined
                hide-details="auto"
                :rules="[(v) => !!v || 'Weight is required']"
                step="0.0000001"
                type="number"
                class="background-white"
                label="Weight*"
                min="0.00000"
                :error-messages="error.weight"
                :value="itemFormDetails.weight"
                @input="syncData($event, 'weight')"
              ></v-text-field>
            </v-col>
          </v-row>
        </v-form>
      </v-card-text>
      <v-card-actions class="d-flex justify-center pb-4">
        <v-btn
          type="submit"
          class="primary text-uppercase mr-3"
          lg="6"
          @click.prevent="submitItemForm()"
          :disabled="!isValid"
        >
          <span>Submit</span>
        </v-btn>
        <v-btn
          v-if="formType == 'add'"
          type="reset"
          class="primary text-uppercase"
          lg="6"
          @click="clear()"
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
      isValid: false,
      error: {},
      nonFieldError: [],
      storageType: [
        { title: "Chilled", value: "Chilled" },
        { title: "Dry", value: "Dry" },
        { title: "Frozen", value: "Frozen" },
      ],
      unitType: [
        {
          text: "KG",
          value: "Kg",
        },
        {
          text: "Case",
          value: "Case",
        },
        {
          text: "Each",
          value: "Each",
        },
      ],
    };
  },
  computed: {
    itemFormDetails: {
      get() {
        return this.$store.state.item.formItem;
      },
      set(value) {
        this.$store.commit("item/SET_ITEM_FORM_DETAILS", value);
      },
    },
    // Form Dialog reference
    itemFormDialog: {
      get() {
        return this.value;
      },
      set(value) {
        this.$emit("input", value);
      },
    },
  },
  methods: {
    async closeDialog() {
      await this.clear();
      this.itemFormDialog = false;
    },
    syncData(input_value, key) {
      if (this.error[key]) {
        this.error[key] = null;
        delete this.error[key];
      }
      this.$store.commit("item/SYNC_ITEM_FORM_DETAILS", {
        key: key,
        value: input_value,
      });
    },
    submitItemForm() {
      if (this.formType == "add") {
        let payload = {
          isBulkupload: true,
          data: this.itemFormDetails,
        };
        this.$store
          .dispatch("item/ADD_ITEM", payload)
          .then((result) => {
            this.closeDialog();
            this.$notifier.showMessage({
              content: "Item entry created!",
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
        let id = this.itemFormDetails.id;
        // delete this.itemFormDetails.id;
        this.$store
          .dispatch("item/UPDATE_ITEM_DETAILS", {
            id: id,
            payload: this.itemFormDetails,
          })
          .then((result) => {
            this.closeDialog();
            this.$notifier.showMessage({
              content: "Item updated successfully!",
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
    clear() {
      this.itemFormDetails = {
        case_factor: null,
        cbm: null,
        height: null,
        item_description: null,
        item_no: null,
        length: null,
        storage_type: null,
        unit: null,
        weight: null,
        width: null,
      };
      if (this.$refs.itemForm) {
        this.$refs.itemForm.reset();
      }
    },
  },
};
</script>