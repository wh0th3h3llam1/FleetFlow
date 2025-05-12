<template>
  <div style="overflow: hidden">
    <v-row class="pa-6" v-if="ticketDetails">
      <v-col cols="6">
        <span
          class="text-h5 text-uppercase font-weight-bold"
          v-if="ticketDetails.reference_number"
        >
          {{ ticketDetails.reference_number }}</span
        >
      </v-col>
      <v-col cols="6" class="text-right">
        <v-btn small depressed class="primary" @click="onBack()">
          <v-icon small class="mr-1">mdi-arrow-left</v-icon>
          <span>Back to List</span>
        </v-btn>
      </v-col>
      <v-col cols="9">
        <v-card elevation="0" outlined class="mt-4">
          <v-card-title
            class="
              light_grey
              px-4
              py-1
              d-flex
              justify-space-between
              align-center
            "
          >
            <div>
              <span class="cf-info-title font-weight-bold" style="opacity: 0.7">
                {{ ticketDetails.title }}</span
              >
            </div>
            <span
              class="cf-info-title text-caption font-weight-bold text-uppercase"
            >
              <v-btn color="white" class="primary" small outlined rounded text>
                {{ ticketDetails.status | titlecase}}
              </v-btn>
            </span>
          </v-card-title>

          <v-card-text class="pa-4">
            <h6 class="font-weight-normal text-subtitle-2 text-light_black">
              {{ ticketDetails.description }}
            </h6>
          </v-card-text>
        </v-card>
        <v-card-title class="px-4 py-1 light_grey mt-12">
          <span
            class="cf-info-title font-weight-bold text-uppercase"
            style="opacity: 0.7"
          >
            comments
          </span>
        </v-card-title>
        <v-card elevation="0" outlined class="pa-6">
          <v-card-text
            id="adminComment"
            class="overflow-y-auto"
            style="max-height: 420px"
          >
            <v-row
              v-for="(ticket, i) in ticketDetails.ticket_comments"
              :key="i"
            >
              <v-col cols="1">
                <v-img
                  :src="imageAdmin"
                  style="width: 60px !important; border-radius: 50%"
                  contain
                  alt="User"
                />
              </v-col>
              <v-col cols="11">
                <h6
                  class="
                    cf-info-title
                    pa-0
                    ma-0
                    font-weight-normal
                    text-primary
                  "
                >
                  {{ ticket.added_by_name }}
                </h6>
                <p class="text-caption font-weight-normal text-primary">
                  {{ ticket.created }}
                </p>
                <h6 class="font-weight-normal text-subtitle-2 text-black">
                  {{ ticket.comment }}
                </h6>
                <h4 v-if="ticket.attachment">
                  <a :href="ticket.attachment" target="_blank">
                    View Attachment
                  </a>
                </h4>
                <br>
              </v-col>
            </v-row>
          </v-card-text>
          <v-card-actions>
            <v-row>
              <v-col cols="12" class="mb-0 pb-0">
                <v-textarea
                  class="mt-2"
                  label="Comment Here..."
                  v-model="comment"
                  outlined
                  rows="3"
                  auto-grow
                ></v-textarea>
              </v-col>
              <v-col cols="10" class="my-0 py-0">
                <v-file-input
                  ref="attachmentInput"
                  :clearable="true"
                  hide-details
                  type="file"
                  v-model="attachment"
                  label="Attachment"
                  prepend-inner-icon="mdi-attachment mdi-rotate-90"
                  prepend-icon=""
                  accept="image/*"
                  outlined
                  dense
                  @change="getFileData($event)"
                ></v-file-input>
                <br>
              </v-col>
              <v-col cols="2" class="my-0 py-0">
                <div class="text-right">
                  <v-btn
                    class="primary text-uppercase"
                    @click="sendComment"
                  >
                    <span>Comment</span>
                  </v-btn>
                </div>
              </v-col>
            </v-row>
          </v-card-actions>
        </v-card>
      </v-col>
      <v-col cols="3">
        <v-card elevation="0" outlined class="my-4">
          <v-card-title class="px-4 py-1 light_grey">
            <span
              class="cf-info-title font-weight-bold text-uppercase"
              style="opacity: 0.7"
            >
              information
            </span>
          </v-card-title>
          <v-card-text>
            <v-row no-gutters class="pt-4">
              <v-col cols="6" class="py-1">
                <span class="cf-info-title font-weight-regular"> Date</span>
              </v-col>
              <v-col cols="6" class="d-flex justify-end text-right py-1">
                <span class="cf-info-title font-weight-bold">
                  {{ ticketDetails.created }}
                </span>
              </v-col>
              <v-col cols="6" class="py-1">
                <span class="cf-info-title font-weight-regular">
                  Added by
                </span>
              </v-col>
              <v-col cols="6" class="d-flex justify-end text-right py-1">
                <span class="cf-info-title font-weight-bold">
                  {{ ticketDetails.added_by_name }}</span
                >
              </v-col>
              <v-col cols="6" class="py-1">
                <span class="cf-info-title font-weight-regular">
                  Priority
                </span>
              </v-col>
              <v-col cols="6" class="d-flex justify-end text-right py-1">
                <span class="cf-info-title font-weight-bold text-capitalize">
                  {{ ticketDetails.priority | titlecase }}
                </span>
              </v-col>
              <v-col cols="6" class="py-1">
                <span class="cf-info-title font-weight-regular"> Module </span>
              </v-col>
              <v-col cols="6" class="d-flex justify-end text-right py-1">
                <span class="cf-info-title font-weight-bold text-capitalize">
                  {{ ticketDetails.module | titlecase }}
                </span>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>

        <v-card
          elevation="0"
          outlined
          v-if="
            ticketDetails.ticket_attachments &&
            ticketDetails.ticket_attachments.length != 0
          "
        >
          <v-card-title class="px-4 py-1 light_grey">
            <span
              class="cf-info-title font-weight-bold text-uppercase"
              style="opacity: 0.7"
            >
              Attachments
            </span>
          </v-card-title>
          <v-card-text class="pa-4">
            <v-row>
              <v-col
                cols="3"
                v-for="(image, i) in ticketDetails.ticket_attachments"
                :key="i"
              >
                <v-card  elevation="2" outlined>
                  <v-card-text class="pa-0">

                    <a :href="image" target="_blank">
                      <v-img
                        contain
                        :lazy-src="image"
                        width="100%"
                        min-height="40px"
                        :src="image"
                      ></v-img>
                    </a>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
        
        <v-card elevation="0" outlined class="my-4" v-if="ticketLogs.data">
          <v-card-title class="px-4 py-1 light_grey">
            <span class="cf-info-title font-weight-bold text-uppercase">
              Logs
            </span>
          </v-card-title>
          <v-card-text
            class="overflow-y-auto"
            style="max-height: 430px"
            >
            <v-timeline dense>
              <v-timeline-item
                small
                v-for="(ticketLog, index) in ticketLogs.data"
                :key="index"
                >
                <v-card elevation="0" outlined>
                  <v-card-title class="py-1 text-body-2">
                    <span>{{ ticketLog.message }}</span>
                  </v-card-title>
                  <v-card-text class="pt-1">
                    <span>{{ ticketLog.created }}</span>
                  </v-card-text>
                </v-card>
              </v-timeline-item>
            </v-timeline>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="9"></v-col>
      <v-col cols="3"></v-col>
    </v-row>
  </div>
</template>

<script>
import imageAdmin from "@/static/user.png";

export default {
  data() {
    return {
      imageAdmin: imageAdmin,
      comment: null,
      attachment: null,
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
    ticketLogs: {
      get() {
        return this.$store.state.support.ticketLogs;
      },
      set(value) {
        this.$store.commit("support/SET_TICKET_LOGS", value);
      },
    },
  },
  methods: {
    sendComment() {
      let commentForm = new FormData();
      commentForm.append("comment", this.comment);
      if(this.attachment) {
        commentForm.append("attachment", this.attachment);
      }

      let payload = {
        id: this.ticketDetails.id,
        data: commentForm
      };
      this.$store
        .dispatch("support/ADD_COMMENT_IN_TICKET_DETAILS", payload)
        .then((response) => {
          let scrollingElement = document.getElementById("adminComment");
          scrollingElement.scrollTop = scrollingElement.scrollHeight;
        });

      this.comment = null;
      this.attachment = null;
    },
    imageFileCheck(fileName) {
      let extension = fileName.slice(
        (Math.max(0, fileName.lastIndexOf(".")) || Infinity) + 1
      );
      if (extension == "png" || extension == "jpeg" || extension == "jpg") {
        return true;
      } else {
        this.$notifier.showMessage({
          content: `Select file(s) are not supported.Support file Types: PNG, JPEG, JPG `,
          color: "error",
        });
        return false;
      }
    },
    getFileData(attachmentInput) {
      if (attachmentInput && attachmentInput.name && !this.imageFileCheck(attachmentInput.name)) {
        this.$refs.attachmentInput.reset();
        this.attachment = null;
        return false;
      }
      if (attachmentInput) {
        this.attachment = attachmentInput;
      }
    },
    onBack() {
      this.$router.push("support");
    }
  },
  mounted() {
    if (document.getElementById("adminComment")) {
      let scrollingElement = document.getElementById("adminComment");
      scrollingElement.scrollTop = scrollingElement.scrollHeight;
    }
    if (!this.ticketDetails.id) {
      this.$router.push({
        name: "support",
        path: "/support",
      });
    }
  },
  filters: {
    titlecase: function (text) {
      try {
        let string = text.replace("_", " ").replace("-", " ")
        return string.replace(/(^|\s)\S/g, function(t) { return t.toUpperCase() });
      }
      catch(TypeError) {
        return text
      }
    }
  }
};
</script>