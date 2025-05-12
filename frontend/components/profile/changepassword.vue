<template>
  <v-dialog v-model="openChangePasswordDialog" max-width="400px">
    <v-card>
      <v-card-title class="background-primary text-white">
        <v-row>
          <v-col cols="10">
            <span class="text-h6"> Change Password </span>
          </v-col>
          <v-col cols="2" class="d-flex justify-end">
            <v-btn small icon @click="closeDialog">
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
        <v-form v-model="isValid" ref="passwordForm">
          <v-row no-gutters class="mt-2">
            <v-col cols="12" class="pt-2">
              <v-text-field
                outlined
                class="background-white"
                label="Existing Password"
                type="password"
                hide-details="auto"
                dense
                :rules="[(v) => !!v || 'Old password is required']"
                :error-messages="error.old_password"
                v-model="user.old_password"
              ></v-text-field>
            </v-col>
            <v-col cols="12" class="pt-4">
              <v-text-field
                outlined
                class="background-white"
                label="New Password"
                hide-details="auto"
                type="password"
                :rules="[
                  (v) => !!v || 'New Password is required',
                  (v) =>
                    v !== user.old_password ||
                    'New password & Old password can not be same',
                ]"
                dense
                :error-messages="error.new_password"
                v-model="user.new_password"
              ></v-text-field>
            </v-col>
            <v-col cols="12" class="pt-4">
              <v-text-field
                outlined
                class="background-white"
                label="Confirm Password"
                hide-details="auto"
                type="password"
                :rules="[
                  (v) =>
                    confirm_password === user.new_password ||
                    'Passwords do not match',
                  (v) => !!v || 'Confirm Password is required',
                ]"
                dense
                :error-messages="error.new_password"
                v-model="confirm_password"
              ></v-text-field>
            </v-col>
          </v-row>
        </v-form>
      </v-card-text>
      <v-card-actions class="d-flex justify-end">
        <v-btn
          type="submit"
          @click="submitUserPassword"
          class="primary"
          :disabled="!isValid"
          >Submit</v-btn
        >
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  props: {
    value: Boolean,
  },
  data() {
    return {
      isValid: false,
      nonFieldError: [],
      error: {},
      confirm_password: null,
      user: {
        old_password: null,
        new_password: null,
      },
    };
  },
  computed: {
    openChangePasswordDialog: {
      get() {
        return this.value;
      },
      set(value) {
        this.$emit("input", value);
      },
    },
  },
  methods: {
    submitUserPassword() {
      this.$store
        .dispatch("profile/UPDATE_USER_PASSWORD", this.user)
        .then((result) => {
          
          this.$notifier.showMessage({
            content: "Please login with new password",
            color: "success",
          });
          this.closeDialog();
          let self = this;
          setTimeout(function () {
            self.$store.dispatch("auth/LOGOUT");
          }, 3000);
        })
        .catch((err) => {
          if ("non_field_errors" in err) {
            this.nonFieldError = err.non_field_errors;
          }
          this.error = err;
        });
    },
    closeDialog() {
      this.$refs.passwordForm.reset();
      this.openChangePasswordDialog = false;
    },
  },
};
</script>