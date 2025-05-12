<template>
  <v-dialog v-model="userFormDialog" persistent width="60%" max-width="70%">
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
          {{ formType }} User
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
      <v-form
        v-if="userFormDialog"
        v-model="isValid"
        ref="userForm"
        id="userForm"
      >
        <v-card-text>
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
          <v-row class="pa-2">
            <v-col cols="12" lg="8">
              <v-row>
                <v-col cols="6" lg="4">
                  <v-text-field
                    :rules="[(v) => !!v || 'First name is required']"
                    outlined
                    hide-details="auto"
                    class="background-white"
                    label="First Name*"
                    :value="userDetails.first_name"
                    @input="syncData($event, 'first_name')"
                  ></v-text-field>
                </v-col>
                <v-col cols="6" lg="4">
                  <v-text-field
                    :rules="[(v) => !!v || 'Last name is required']"
                    outlined
                    hide-details="auto"
                    class="background-white"
                    label="Last Name*"
                    :value="userDetails.last_name"
                    @input="syncData($event, 'last_name')"
                  ></v-text-field>
                </v-col>
                <v-col cols="6" lg="4">
                  <v-text-field
                    :rules="[(v) => !!v || 'User name is required']"
                    outlined
                    hide-details="auto"
                    class="background-white"
                    label="User Name*"
                    :error-messages="error.username"
                    :value="userDetails.username"
                    @input="syncData($event, 'username')"
                  ></v-text-field>
                </v-col>
                <v-col cols="6" lg="4">
                  <v-text-field
                    :rules="[rules.required, rules.email]"
                    outlined
                    hide-details="auto"
                    class="background-white"
                    label="Email*"
                    :value="userDetails.email"
                    @input="syncData($event, 'email')"
                  ></v-text-field>
                </v-col>
                <v-col cols="6" lg="4">
                  <v-text-field
                    :rules="[(v) => !!v || 'Contact Number is required']"
                    outlined
                    type="number"
                    hide-details="auto"
                    class="background-white"
                    label="Contact Number*"
                    :value="userDetails.contact_number"
                    @input="syncData($event, 'contact_number')"
                  ></v-text-field>
                </v-col>
                <v-col cols="6" lg="4">
                  <v-select
                    :rules="[
                      (v) =>
                        (v != null && v.length > 0) || 'Project is required',
                    ]"
                    outlined
                    multiple
                    :items="allProjects"
                    hide-details="auto"
                    class="background-white"
                    label="Project*"
                    :value="userDetails.projects"
                    @change="syncData($event, 'projects_assigned')"
                    :menu-props="{ offsetY: true }"
                  >
                    <template v-slot:selection="{ item, index }">
                      <span v-if="index === 0">{{ item.text }}</span>
                      <span
                        v-if="index === 1 && formType == 'add'"
                        class="grey--text text-caption"
                      >
                        (+{{ userDetails.projects_assigned.length - 1 }} others)
                      </span>
                      <span
                        v-if="index === 1 && formType == 'edit'"
                        class="grey--text text-caption"
                      >
                        (+{{ userDetails.projects.length - 1 }} others)
                      </span>
                    </template>
                  </v-select>
                </v-col>
                <v-col cols="6" lg="4">
                  <v-text-field
                    :rules="
                      formType == 'add'
                        ? [(v) => !!v || 'Password is required']
                        : []
                    "
                    outlined
                    type="password"
                    hide-details="auto"
                    class="background-white"
                    label="Password*"
                    :error-messages="error.password"
                    @change="syncData($event, 'password')"
                  ></v-text-field>
                </v-col>

                <v-col cols="6" lg="4">
                  <v-text-field
                    :rules="
                      formType == 'add'
                        ? [
                            (v) => !!v || 'Confirm Password is required',
                            (v) =>
                              !v ||
                              v == userDetails.password ||
                              'Password does not match',
                          ]
                        : [
                            (v) =>
                              !v ||
                              v == userDetails.password ||
                              'Password does not match',
                          ]
                    "
                    outlined
                    type="password"
                    hide-details="auto"
                    class="background-white"
                    label="Confirm Password*"
                  ></v-text-field>
                </v-col>
                <v-col cols="6" lg="4">
                  <v-select
                    outlined
                    :rules="[(v) => !!v || 'Role is required']"
                    :items="allRoles"
                    label="Select Role*"
                    :value="userDetails.role"
                    @change="syncData($event, 'role')"
                    :menu-props="{ offsetY: true }"
                  >
                  </v-select>
                </v-col>
              </v-row>
            </v-col>

            <v-col
              cols="12"
              lg="4"
              class="px-6 pt-2 pb-6 d-flex justify-center"
            >
              <v-img
                contain
                :src="userimage"
                max-height="200"
                max-width="200"
                height="200"
                width="200"
                class="rounded-circle"
              />
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions class="d-flex justify-center pt-6 pb-4">
          <v-btn
            type="submit"
            :disabled="!isValid"
            class="primary text-uppercase mr-3"
            @click.prevent="submitUserForm()"
          >
            <span>Submit</span>
          </v-btn>
          <v-btn
            type="reset"
            v-if="formType == 'add'"
            class="primary text-uppercase"
            @click="clear()"
          >
            <span>Reset</span>
          </v-btn>
        </v-card-actions>
      </v-form>
    </v-card>
  </v-dialog>
</template>

<script>
import UserImage from "@/static/default-user.jpg";
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
      userimage: UserImage,
      nonFieldError: [],
      error: {},
      isValid: false,
      rules: {
        required: (value) => !!value || "Email is required",
        email: (value) => {
          const pattern =
            /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
          return pattern.test(value) || "Invalid Email ID.";
        },
      },
    };
  },
  computed: {
    userDetails: {
      get() {
        return this.$store.state.user.userdetail;
      },
      set(value) {
        this.$store.commit("user/SET_USER_DETAILS", value);
      },
    },
    allProjects() {
      return this.$store.getters["project/PROJECT_LIST_FOR_DROPDOWN"];
    },
    allRoles() {
      return this.$store.getters["role/ROLE_LIST_FOR_DROPDOWN"];
    },
    userFormDialog: {
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
      this.userFormDialog = false;
      this.clear();
    },
    submitUserForm() {
      if (this.formType == "add") {
        this.$store
          .dispatch("user/ADD_USER", this.userDetails)
          .then((result) => {
            this.closeDialog();
            this.$notifier.showMessage({
              content: "User Added successfully",
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
          .dispatch("user/UPDATE_USER_DETAILS", this.userDetails)
          .then((result) => {
            this.$notifier.showMessage({
              content: "User Updated successfully",
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
      this.$store.commit("user/SYNC_USER_FORM_DETAILS", {
        key: key,
        value: input_value,
      });
    },
    clear() {
      this.userDetails = {
        first_name: null,
        all_projects: null,
        last_name: null,
        username: null,
        email: null,
        contact_number: null,
        id: null,
        is_active: null,
        permissions: null,
        profile_image: null,
        role: null,
        role_name: null,
        roles: null,
      };
      this.$refs.userForm.reset();
    },
  },
};
</script>