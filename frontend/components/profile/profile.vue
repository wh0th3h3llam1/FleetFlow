<template>
  <v-dialog v-model="openProfileDialog" max-width="400px">
    <v-card>
      <v-card-title class="background-primary text-white">
        <v-row>
          <v-col cols="10">
            <span class="text-h6" v-if="isEditMode"> Edit User Profile </span>
            <span class="text-h6" v-else> User Profile </span>
          </v-col>
          <v-col cols="2" class="d-flex justify-end">
            <v-btn small icon @click="openProfileDialog = false">
              <v-icon class="text-white">mdi-close</v-icon>
            </v-btn>
          </v-col>
          <v-col cols="12" v-if="nonFieldError.length">
            <v-alert dense type="error">
              <v-list
                class="pa-0"
                dense
                style="background: inherit !important"
                v-for="(error, i) in nonFieldError"
                :key="i"
              >
                <v-list-item dense style="min-height: 20px !important">
                  <span>{{ i }} . </span><span>{{ error }}</span>
                </v-list-item>
              </v-list>
            </v-alert>
          </v-col>
        </v-row>
      </v-card-title>
      <v-card-text>
        <v-row no-gutters>
          <v-col cols="12" class="d-flex justify-center py-2">
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
        <div class="my-2">
          <v-row class="py-2">
            <v-col cols="6">
              <span class="font-weight-bold text-body-1">User Details</span>
            </v-col>
            <v-col cols="6" class="d-flex justify-end">
              <v-tooltip left>
                <template v-slot:activator="{ on, attrs }">
                  <v-btn
                    v-on="on"
                    v-bind="attrs"
                    small
                    icon
                    @click="isEditMode = !isEditMode"
                  >
                    <v-icon class="text-primary">mdi-pencil</v-icon>
                  </v-btn>
                </template>
                <span>Edit Details</span>
              </v-tooltip>
            </v-col>
          </v-row>
          <hr />
          <v-row class="pa-4" v-if="!isEditMode">
            <v-col cols="6" class="d-flex justify-start">
              <span>Username</span>
            </v-col>
            <v-col cols="6" class="d-flex justify-start">
              <span class="font-weight-bold">{{ userDetails.username }}</span>
            </v-col>
            <v-col cols="6" class="d-flex justify-start">
              <span>Contact Number</span>
            </v-col>
            <v-col cols="6" class="d-flex justify-start">
              <span class="font-weight-bold">{{
                userDetails.contact_number
              }}</span>
            </v-col>
            <v-col cols="6" class="d-flex justify-start">
              <span>Email ID</span>
            </v-col>
            <v-col cols="6" class="d-flex justify-start">
              <span class="font-weight-bold">{{ userDetails.email }}</span>
            </v-col>
            <v-col cols="6" class="d-flex justify-start">
              <span>Role Name</span>
            </v-col>
            <v-col
              cols="6"
              class="d-flex justify-start text-capitalize"
              v-if="userDetails.role_name"
            >
              <span class="font-weight-bold">{{
                userDetails.role_name.replace("_", " ")
              }}</span>
            </v-col>
          </v-row>
          <v-form v-else v-model="isValid">
            <v-row no-gutters class="mt-2">
              <v-col cols="12" class="pt-2">
                <v-text-field
                  outlined
                  class="background-white"
                  label="First name"
                  hide-details="auto"
                  dense
                  :error-messages="error.first_name"
                  :value="userDetails.first_name"
                  @input="syncUserDetails($event, 'first_name')"
                ></v-text-field>
              </v-col>
              <v-col cols="12" class="pt-4">
                <v-text-field
                  outlined
                  class="background-white"
                  label="Last Name"
                  hide-details="auto"
                  dense
                  :error-messages="error.last_name"
                  :value="userDetails.last_name"
                  @input="syncUserDetails($event, 'last_name')"
                ></v-text-field>
              </v-col>
              <v-col cols="12" class="pt-4">
                <v-text-field
                  outlined
                  class="background-white"
                  type="number"
                  min="0"
                  step="01"
                  hide-details="auto"
                  dense
                  label="Contact number"
                  :error-messages="error.contact_number"
                  :value="userDetails.contact_number"
                  @input="syncUserDetails($event, 'contact_number')"
                ></v-text-field>
              </v-col>
              <v-col cols="12" class="pt-4">
                <v-text-field
                  outlined
                  class="background-white"
                  label="Email ID"
                  hide-details="auto"
                  dense
                  :error-messages="error.email"
                  :value="userDetails.email"
                  @input="syncUserDetails($event, 'email')"
                ></v-text-field>
              </v-col>
            </v-row>
          </v-form>
        </div>
      </v-card-text>
      <v-card-actions v-if="isEditMode" class="d-flex justify-end">
        <v-btn
          type="submit"
          @click="submitUserDetails"
          class="primary"
          :disabled="!isValid"
          >Submit</v-btn
        >
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import UserImage from "@/static/default-user.jpg";

export default {
  props: {
    value: Boolean,
  },
  data() {
    return {
      userimage: UserImage,
      isValid: false,
      isEditMode: false,
      nonFieldError: [],
      error: {},
    };
  },
  computed: {
    openProfileDialog: {
      get() {
        return this.value;
      },
      set(value) {
        this.$emit("input", value);
      },
    },
    userDetails: {
      get() {
        return this.$store.state.profile.userProfile;
      },
      set(value) {
        this.$store.commit("profile/SET_USER_DETAILS");
      },
    },
  },
  methods: {
    syncUserDetails(value, key) {
      if (key in this.error) {
        this.error[key] = null;
        delete this.error.key;
      }
      this.$store.commit("profile/SYNC_USER_DETAILS", {
        key: key,
        value: value,
      });
    },
    submitUserDetails() {
      this.$store
        .dispatch("profile/UPDATE_USER_DETAILS", this.userDetails)
        .then((result) => {
          
          this.openProfileDialog = false;
        })
        .catch((err) => {
          if ("non_field_errors" in err) {
            this.nonFieldError = err.non_field_errors;
          }
          this.error = err.errors;
        });
    },
  },
};
</script>