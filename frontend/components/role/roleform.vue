<template>
  <v-dialog
    v-model="userRoleDialog"
    scrollable
    persistent
    width="60%"
    max-width="70%"
  >
    <v-card class="pa-4">
      <v-card-title>
        <span
          class="
            text-lg-subtitle-1 text-xl-h6 text-uppercase
            font-weight-black
            primary--text
            mb-4
          "
        >
          {{ formType }} Role
        </span>
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

      <v-card-text>
        <v-form
          v-if="userRoleDialog"
          v-model="isValid"
          ref="roleForm"
          id="roleForm"
        >
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
          <v-row class="pt-4">
            <v-col cols="6" lg="4">
              <v-text-field
                outlined
                hide-details="auto"
                class="background-white"
                label="Role Name*"
                :value="roleDetails.role_name"
                :rules="[(v) => !!v || 'Role Name is Required']"
                :error-messages="error.role_name"
                @input="syncData($event, 'role_name')"
              ></v-text-field>
            </v-col>
            <v-col cols="12" class="mt-4 mb-4">
              <span class="font-weight-bold text-subtitle-1" color="grey"
                >Permissions</span
              >
              <hr class="mt-3" />
            </v-col>

            <v-col cols="12">
              <v-row>
                <v-col cols="12" class="primary px-10">
                  <v-row>
                    <v-col><span class="text-white">Module</span></v-col>
                    <v-col><span class="text-white">View</span></v-col>
                    <v-col><span class="text-white">Change</span></v-col>
                    <v-col><span class="text-white">Add</span></v-col>
                    <v-col><span class="text-white">Delete</span></v-col>
                  </v-row>
                </v-col>
                <v-col
                  class="px-10"
                  cols="12"
                  v-for="(permission, index) in permissions"
                  :key="index"
                >
                  <v-row>
                    <v-col>{{ permission.Modules }}</v-col>
                    <v-col>
                      <v-checkbox
                        color="success"
                        class="mt-1"
                        v-model="Permissionselected"
                        @change="valueChanged($event, permission.view)"
                        :value="permission.view"
                        hide-details
                      >
                      </v-checkbox>
                    </v-col>
                    <v-col>
                      <v-checkbox
                        color="success"
                        class="mt-1"
                        v-model="Permissionselected"
                        :value="permission.change"
                        hide-details
                      >
                      </v-checkbox>
                    </v-col>
                    <v-col>
                      <v-checkbox
                        color="success"
                        class="mt-1"
                        v-model="Permissionselected"
                        :value="permission.add"
                        hide-details
                      >
                      </v-checkbox>
                    </v-col>
                    <v-col>
                      <v-checkbox
                        color="success"
                        class="mt-1"
                        hide-details
                        @change="valueChanged($event, permission.delete)"
                        v-model="Permissionselected"
                        :value="permission.delete"
                      >
                      </v-checkbox>
                    </v-col>
                  </v-row>
                </v-col>
              </v-row>
            </v-col>
          </v-row>
        </v-form>
      </v-card-text>
      <v-card-actions class="d-flex justify-center pt-6 pb-4">
        <v-btn
          type="submit"
          class="primary text-uppercase mr-3"
          :disabled="!isValid || Permissionselected.length == 0"
          @click.prevent="submitRoleForm()"
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
      nonFieldError: [],
      Permissionselected: [],
      isValid: false,
      typeOfPermission: ["delete", "change", "view", "add"],
      permissions: [
        {
          Modules: "Role",
          view: "view_role",
          change: "change_role",
          add: "add_role",
          delete: "delete_role",
        },
        {
          Modules: "User",
          view: "view_dashuser",
          change: "change_dashuser",
          add: "add_dashuser",
          delete: "delete_dashuser",
        },
        {
          Modules: "Project",
          view: "view_project",
          change: "change_project",
          add: "add_project",
          delete: "delete_project",
        },
        {
          Modules: "Item Master",
          view: "view_itemmaster",
          change: "change_itemmaster",
          add: "add_itemmaster",
          delete: "delete_itemmaster",
        },
        {
          Modules: "Order",
          view: "view_order",
          change: "change_order",
          add: "add_order",
          delete: "delete_order",
        },
        {
          Modules: "Customer",
          view: "view_customeraddress",
          change: "change_customeraddress",
          add: "add_customeraddress",
          delete: "delete_customeraddress",
        },
        {
          Modules: "Trip",
          view: "view_trip",
          change: "change_trip",
          add: "add_trip",
          delete: "delete_trip",
        },
        {
          Modules: "Driver",
          view: "view_driver",
          change: "change_driver",
          add: "add_driver",
          delete: "delete_driver",
        },
        {
          Modules: "Vehicle",
          view: "view_vehicle",
          change: "change_vehicle",
          add: "add_vehicle",
          delete: "delete_vehicle",
        },
        {
          Modules: "Zone",
          view: "view_zone",
          change: "change_zone",
          add: "add_zone",
          delete: "delete_zone",
        },
        {
          Modules: "Support",
          view: "view_ticket",
          change: "change_ticket",
          add: "add_ticket",
          delete: "delete_ticket",
        },
      ],
    };
  },
  computed: {
    roleDetails: {
      get() {
        this.Permissionselected = this.$store.state.role.roledetail.permissions
          ? this.$store.state.role.roledetail.permissions
          : [];
        return this.$store.state.role.roledetail;
      },
      set(value) {
        this.$store.commit("role/SET_ROLE_DETAILS", value);
      },
    },
    userRoleDialog: {
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
      this.userRoleDialog = false;
      this.clear();
    },
    valueChanged(e, input) {
      let module_name = input.split("_")[1];
      let permission = input.split("_")[0];
      this.typeOfPermission.forEach((value) => {
        if (permission == "delete") {
          if (
            permission != value &&
            !this.Permissionselected.includes(`${value}_${module_name}`)
          ) {
            this.Permissionselected.push(`${value}_${module_name}`);
          }
        } else if (permission == "view") {
          let index = this.Permissionselected.indexOf(
            `${value}_${module_name}`
          );
          if (index > -1 && value != permission) {
            this.Permissionselected.splice(index, 1);
          }
        }
      });
    },
    submitRoleForm() {
      if (this.formType == "add") {
        this.roleDetails.updated_permissions = this.Permissionselected;
        this.$store
          .dispatch("role/ADD_ROLE", this.roleDetails)
          .then((result) => {
            this.closeDialog();
            this.$notifier.showMessage({
              content: "Role Added successfully",
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
        this.roleDetails.updated_permissions = this.Permissionselected;
        this.$store
          .dispatch("role/UPDATE_ROLE_DETAILS", this.roleDetails)
          .then((result) => {
            this.$notifier.showMessage({
              content: "Role Updated successfully",
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
      if (this.error[key]) {
        this.error[key] = null;
        delete this.error[key];
      }
      this.$store.commit("role/SYNC_ROLE_FORM_DETAILS", {
        key: key,
        value: input_value,
      });
    },
    clear() {
      this.Permissionselected = [];
      this.roleDetails = {
        all_permissions: [],
        id: null,
        is_deletable: null,
        permissions: [],
        role_name: null,
      };
      this.$refs.roleForm.reset();
    },
  },
};
</script>