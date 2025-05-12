<template>
  <v-menu
    v-model="openNotifications"
    :close-on-content-click="false"
    max-width="400px"
    nudge-left="345"
    offset-y
  >
    <template v-slot:activator="{ on, attrs }">
      <v-badge
        :content="unreadCount"
        :color="unreadCount == 0 ? '' : 'green'"
        class="mr-4"
        top
        overlap
      >
        <span>
          <v-btn
            text
            class="mr-n5"
            v-on="on"
            v-bind="attrs"
            @click="get_all_notifications(true)"
            :class="openNotifications ? 'text-primary' : ''"
          >
            <v-icon>mdi-bell</v-icon>
          </v-btn>
        </span>
      </v-badge>
    </template>
    <v-card width="400px" elevation="0">
      <v-card-title
        class="pt-4 pb-2 text-primary body-1 d-flex justify-space-between"
      >
        <span>Notifications</span>
        <v-btn
          :disabled="userNotifications.length == 0"
          small
          text
          depressed
          class="primary--text"
          @click="markAllAsRead"
          >Clear All</v-btn
        >
      </v-card-title>
      <v-card-text
        elevation-0
        style="max-height: 350px"
        class="pa-0 overflow-y-auto overflow-x-hidden"
        @scroll="handleScroll()"
        ref="notificationParent"
      >
        <div
          v-if="
            userNotifications &&
            userNotifications.length == 0 &&
            !noNewNotifications
          "
          class="d-flex justify-center py-2"
        >
          <v-progress-circular
            :width="3"
            color="grey"
            indeterminate
          ></v-progress-circular>
        </div>
        <div v-else-if="noNewNotifications" class="d-flex justify-center py-2">
          <span>No new Notifications!</span>
        </div>
        <div v-for="(noti, i) in userNotifications" :key="i" v-else>
          <v-row
            class="pl-4 pa-0 my-1 notiication"
            v-if="!noti.is_read"
            :style="{ backgroundColor: 'white' }"
          >
            <v-col cols="12" class="pa-0 ma-0">
              <hr style="opacity: 0.4" />
            </v-col>
            <v-col cols="2" class="d-flex align-center justify-center">
              <div
                style="
                  display: flex;
                  justiy-cotent: center;
                  align-items: center;
                  padding: 15px;
                "
                :class="[
                  noti.notification_type == 'success' ? 'successMessage' : '',
                  noti.notification_type == 'warning' ? 'warningMessage' : '',
                  noti.notification_type == 'info' ? 'infoMessage' : '',
                  noti.notification_type == 'error' ? 'errorMessage' : '',
                ]"
              >
                <v-icon
                  color="white"
                  v-if="noti.notification_category == 'driver'"
                  >mdi-card-account-details-outline</v-icon
                >
                <v-icon
                  color="white"
                  v-else-if="noti.notification_category == 'order'"
                  >mdi-archive-outline</v-icon
                >
                <v-icon
                  color="white"
                  v-else-if="noti.notification_category == 'trip'"
                  >mdi-truck-fast</v-icon
                >
                <v-icon
                  color="white"
                  v-else-if="noti.notification_category == 'trip_planning'"
                  >mdi-map-marker-distance</v-icon
                >
                <v-icon
                  color="white"
                  v-else-if="noti.notification_category == 'location'"
                  >mdi-map-marker</v-icon
                >
                <v-icon
                  color="white"
                  v-else-if="noti.notification_category == 'customer'"
                  >mdi-account</v-icon
                >
                <v-icon
                  color="white"
                  v-else-if="noti.notification_category == 'vehicle'"
                  >mdi-truck</v-icon
                >
                <v-icon
                  color="white"
                  v-else-if="noti.notification_category == 'report'"
                  >mdi-chart-areaspline</v-icon
                >
                <v-icon
                  color="white"
                  v-else-if="noti.notification_category == 'user'"
                  >mdi-account-check</v-icon
                >
              </div>
            </v-col>
            <v-col cols="8" class="d-flex align-center">
              <v-row no-gutters>
                <v-col cols="12" class="text-body-2">
                  <span>
                    {{ noti.title }}
                  </span>
                </v-col>
                <v-col cols="12" class="text-caption">
                  {{ noti.message }}
                </v-col>
                <v-col cols="12" class="text-caption font-weight-bold mt-1">
                  {{ noti.created }}
                </v-col>
              </v-row>
            </v-col>
            <v-col cols="2" class="d-flex align-center">
              <v-btn
                small
                icon
                @click="markAsRead(noti.id)"
                class="primary--text"
              >
                <v-icon small>mdi-close</v-icon>
              </v-btn>
            </v-col>
          </v-row>
        </div>
      </v-card-text>
    </v-card>
  </v-menu>
</template>

<style scoped>
.notiication:hover {
  background-color: #ebf7fc !important;
}

.successMessage {
  background-color: #d1d3d4;
}
.errorMessage {
  background-color: #ee919d;
}
.warningMessage {
  background-color: #e1af0f;
}
.infoMessage {
  background-color: #6bcadc;
}
</style>

<script>
export default {
  props: {
    value: {
      type: Boolean,
      require: true,
      default: false,
    },
  },
  data() {
    return {
      limit: 10,
      unreadCount: 0,
      noNewNotifications: false,
    };
  },
  computed: {
    openNotifications: {
      get() {
        return this.value;
      },
      set(value) {
        this.$emit("input", value);
      },
    },
    userNotifications() {
      return this.$store.state.user_notification.userNotifications;
    },
    totalCount() {
      return this.$store.state.user_notification.totalCount;
    },
    workerInstance: {
      get() {
        return this.$store.state.user_notification.workerInstance;
      },
      set(value) {
        this.$store.commit("user_notification/SET_WORKER_INSTANCE", value);
      },
    },
  },
  methods: {
    handleScroll() {
      let elem = this.$refs.notificationParent;
      if (elem == null) {
        return false;
      } else if (
        Math.ceil(elem.offsetHeight + elem.scrollTop) == elem.scrollHeight
      ) {
        this.get_all_notifications(false);
      }
    },
    get_all_notifications(reload) {
      this.noNewNotifications = false;
      if (!reload || !this.openNotifications) {
        this.$store
          .dispatch("user_notification/GET_ALL_NOTIFICATIONS", reload)
          .then((result) => {
            if (result.count == 0 && result.results.length == 0) {
              this.noNewNotifications = true;
            }
          })
          .catch((err) => {
            if (err.message) {
              this.$notifier.showMessage({
                content: err.message,
                color: "error",
              });
            } else {
              this.$notifier.showMessage({
                content: "Error Fetching data!",
                color: "error",
              });
            }
          });
      }
    },
    markAllAsRead() {
      let ids = this.userNotifications.map((notification) => {
        return notification.id;
      });
      this.$store
        .dispatch("user_notification/MARK_ALL_AS_READ", ids)
        .then((result) => {
          this.openNotifications = false;
          this.unreadCount = this.unreadCount - this.userNotifications.length;
        })
        .catch((err) => {
          if (err.message) {
            this.$notifier.showMessage({
              content: err.message,
              color: "error",
            });
          } else {
            this.$notifier.showMessage({
              content: "Error Fetching data!",
              color: "error",
            });
          }
        });
    },
    markAsRead(id) {
      this.$store
        .dispatch("user_notification/MARK_AS_READ", id)
        .then((result) => {
          this.$store.commit("user_notification/UPDATE_NOTIFICATIONS", id);
          if (this.userNotifications && this.userNotifications.length == 0) {
            this.openNotifications = true;
          }
        })
        .catch((err) => {
          if (err.message) {
            this.$notifier.showMessage({
              content: err.message,
              color: "error",
            });
          } else {
            this.$notifier.showMessage({
              content: "Error Fetching data!",
              color: "error",
            });
          }
        });
    },
    workerNotificationHandler(url) {
      if (this.workerInstance) {
        this.workerInstance.postMessage({
          event: "get_unread_notification",
          token: localStorage.getItem("user"),
          url: url,
        });
        let self = this;
        this.workerInstance.onmessage = function (e) {
          if (e.data && e.data.event == "unread_notification_count") {
            self.unreadCount = e.data.unreadNotificationCount;
          }
        };
      }
    },
  },
  mounted() {},
  created() {
    if (process.browser) {
      // Remember workers just work in client?.. This will poll for unread notifications
      this.workerInstance = this.$notiWorker.createWorker(); // Instruction assigned in plugin
      const url = `${this.$axios.defaults.baseURL}api/v1/notification/get_notification_count/`;
      this.workerNotificationHandler(url);
    }
  },
  beforeDestroy() {
    if (this.workerInstance) {
      this.workerInstance.terminate();
    }
    this.$store.commit("user_notification/SET_ALL_NOTIFICATIONS", {
      results: [],
      count: 0,
    });
  },
};
</script>
