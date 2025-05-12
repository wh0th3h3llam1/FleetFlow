<template>
  <v-card
    v-if="chatbox"
    class="mx-auto chatMainContainer"
    max-width="400"
    elevation="5"
  >
    <v-list-item two-line>
      <v-list-item-avatar color="grey darken-3">
        <v-img class="elevation-6" alt="" :src="driverImage"></v-img>
      </v-list-item-avatar>

      <v-list-item-content>
        <v-list-item-title class="text-h5">
          {{ driverDetails.driverName }}
        </v-list-item-title>
        <v-list-item-subtitle
          v-if="driverDetails.status == 'on_duty'"
          class="green--text"
        >
          online</v-list-item-subtitle
        >
      </v-list-item-content>

      <v-icon class="mt-n3" @click="chatbox = false">mdi-close</v-icon>
    </v-list-item>
    <v-divider></v-divider>
    <v-card-text
      style="height: 270px; overflow-y: scroll; position: relative"
      id="chatBoxContainer"
      class="pa-0"
    >
      <v-img
        :src="audiaImage"
        v-show="isImageVisible"
        contain
        class="audio-listening"
      />
      <v-list v-for="(chat, index) in chats" :key="index">
        <v-list-item v-if="chat.send_by_driver">
          <v-card outlined class="pa-3 mb-2" style="max-width: 80%">
            <v-list-item-title class="d-flex align-center ma-0 pa-0">
              <div>
                <v-img
                  alt=""
                  style="height: 19px; width: 19px; border-radius: 50%"
                  contain
                  class="mr-2"
                  :src="sendImage"
                ></v-img>
              </div>
              <span class="caption mt-n2 pt-2">{{ chat.sender }}</span>
            </v-list-item-title>
            <v-divider class="mt-2"></v-divider>
            <div v-if="chat.message_format == 'audio'">
              <audio controls style="width: 220px" class="mt-4">
                <source :src="chat.attachment" type="audio/mp3" />
                Your browser does not support the audio element.
              </audio>
            </div>
            <div v-else-if="chat.message_format == 'document'">
              <a
                target="_blank"
                :href="chat.attachment"
                style="text-decoration: none"
              >
                <v-card elevation="0" class="mt-2" outlined>
                  <v-card-text>
                    <v-icon
                      x-large
                      color="primary"
                      v-if="getFileIcon(chat.message) == 'pdf'"
                      >mdi-file-pdf</v-icon
                    >
                    <v-icon x-large color="green" v-else>mdi-file-excel</v-icon>
                  </v-card-text>
                </v-card>
              </a>
            </div>
            <div v-else-if="chat.message_format == 'image'">
              <a target="_blank" :href="chat.attachment">
                <v-img
                  :src="chat.attachment"
                  width="200px"
                  height="150px"
                  contain
                />
              </a>
            </div>
            <div v-else class="px-2 py-1">
              <span>{{ chat.message }}</span>
            </div>
          </v-card>
        </v-list-item>
        <v-list-item v-else class="d-flex justify-end">
          <v-card outlined class="pa-3 mb-2" style="max-width: 80%">
            <v-list-item-title class="d-flex align-center ma-0 pa-0">
              <div>
                <v-img
                  alt=""
                  style="height: 19px; width: 19px; border-radius: 50%"
                  contain
                  class="mr-2"
                  :src="sendImage"
                ></v-img>
              </div>
              <span class="caption mt-n2 pt-2">{{ chat.sender }}</span>
            </v-list-item-title>
            <v-divider class="mt-2"></v-divider>

            <div v-if="chat.message_format == 'audio'">
              <audio controls style="width: 220px" class="mt-4">
                <source :src="chat.attachment" type="audio/mp3" />
                Your browser does not support the audio element.
              </audio>
            </div>
            <div v-else-if="chat.message_format == 'document'">
              <a
                target="_blank"
                :href="chat.attachment"
                style="text-decoration: none"
              >
                <v-card elevation="0" class="mt-2" outlined>
                  <v-card-text>
                    <v-icon
                      x-large
                      color="primary"
                      v-if="getFileIcon(chat.message) == 'pdf'"
                      >mdi-file-pdf</v-icon
                    >
                    <v-icon x-large color="green" v-else>mdi-file-excel</v-icon>
                  </v-card-text>
                </v-card>
              </a>
            </div>
            <div v-else-if="chat.message_format == 'image'">
              <a target="_blank" :href="chat.attachment">
                <v-img
                  :src="chat.attachment"
                  width="200px"
                  height="150px"
                  contain
                />
              </a>
            </div>
            <div v-else class="px-2 py-1">
              <span>{{ chat.message }}</span>
            </div>
          </v-card>
        </v-list-item>
      </v-list>
    </v-card-text>
    <v-divider></v-divider>

    <v-card-actions>
      <v-row>
        <v-col cols="12" class="d-flex">
          <v-text-field
            dense
            hide-details="auto"
            solo
            class="chat-box"
            @keyup.enter.native="SendMessage"
            placeholder="Message"
            v-model="chatText"
          ></v-text-field>
          <v-icon class="mr-2" @click="SendMessage">mdi-send</v-icon>
          <v-icon class="mr-2" @click="listeningAudio" v-if="!isImageVisible">
            mdi-microphone-settings
          </v-icon>
          <v-icon class="mr-2 text-red" @click="listeningAudio" v-else
            >mdi-stop</v-icon
          >

          <form ref="chatForm" id="chatForm" enctype="multipart/form-data">
            <input
              name="attachment"
              ref="uploadImage"
              class="d-none"
              type="file"
              @change="SendMessage"
              accept=".pdf, image/png, image/jpg, image/jpeg"
            />
            <v-icon class="mdi-rotate-90 mb-n4" @click="uploadMethod">
              mdi-attachment
            </v-icon>
          </form>
        </v-col>
      </v-row>
    </v-card-actions>
  </v-card>
</template>

<script>
import defaultDriverImage from "@/static/user.png";
import defaultSendImage from "@/static/default-user.jpg";
import audiaImage from "@/static/startrecording.gif";
export default {
  props: {
    value: Boolean,
    driverDetails: Object,
  },
  data() {
    return {
      chatDialogBox: true,
      chatText: "",
      driverName: null,
      isImageVisible: false,
      file: "",
      audiaImage: audiaImage,
      driverImage: defaultDriverImage,
      sendImage: defaultSendImage,
      ChatData: {
        message_format: null,
      },
      mediaRecorder: null,
      chunks: [],
    };
  },
  methods: {
    getFileIcon(file) {
      return file.slice((Math.max(0, file.lastIndexOf(".")) || Infinity) + 1);
    },
    listeningAudio() {
      this.isImageVisible = !this.isImageVisible;

      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        if (this.isImageVisible) {
          navigator.mediaDevices
            .getUserMedia({
              audio: true,
            })
            .then((stream) => {
              this.mediaRecorder = new MediaRecorder(stream, {
                mimeType: "audio/webm",
              });
              this.mediaRecorder.start();
              this.mediaRecorder.ondataavailable = (e) => {
                this.chunks.push(e.data);
              };
              this.mediaRecorder.onstop = (e) => {
                let b = new File(this.chunks, `${Date()}.mp3`, {
                  type: "audio/mp3",
                });
                const formdata = new FormData();
                formdata.append("message_format", "audio");
                formdata.append("attachment", b);
                this.SubmitData(formdata);
              };
            })
            .catch((err) => {
              console.error(
                "The following getUserMedia error occurred: " + err
              );
            });
        } else {
          this.mediaRecorder.stop();
        }
      } else {
        console.error("getUserMedia not supported on your browser!");
      }
    },
    uploadMethod() {
      this.$refs.uploadImage.click();
    },
    SendMessage() {
      const file = this.$refs.uploadImage.files[0];
      this.file = file;

      if (!this.chatText && !this.file) {
        return false;
      }

      if (this.chatText) {
        this.ChatData = {
          message: this.chatText,
          message_format: "text",
        };
        this.SubmitData(this.ChatData);
      } else if (this.file) {
        const formdata = new FormData();
        formdata.append("message_format", "image");
        formdata.append("attachment", this.file);
        this.SubmitData(formdata);
      }
    },
    SubmitData(data) {
      this.$store
        .dispatch("operation/SEND_MESSAGE", {
          id: this.driverDetails.id,
          data: data,
        })
        .then((response) => {
          this.chatText = "";
          this.file = "";
          this.autoScroll();
        });
    },
    autoScroll() {
      if (document.getElementById("chatBoxContainer")) {
        let nid = document.getElementById("chatBoxContainer");
        nid.scrollTop = nid.scrollHeight;
      }
    },
  },
  computed: {
    chats: {
      get() {
        let chatListData = this.$store.state.operation.chatList;
        this.ChatData.trip = chatListData.trip;
        this.driverName = chatListData.driver;
        return chatListData;
      },
      set(value) {
        this.$store.commit("operation/SET_DRIVER_CHAT_DATA", value);
      },
    },

    chatbox: {
      get() {
        return this.value;
      },
      set(value) {
        this.$emit("input", value);
      },
    },
  },
  updated() {
    this.autoScroll();
  },
  mounted() {
    this.autoScroll();
  },
  beforeMount() {
    this.autoScroll();
  },
};
</script>

<style scoped lang="scss">
.chatMainContainer {
  position: fixed;
  bottom: 5%;
  right: 5%;
  z-index: 999;
  width: 350px;
}
.chat-box .v-input__slot {
  box-shadow: none !important;
  border: 11px solid red !important;
}
.audio-listening {
  position: sticky;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 1;
  height: 150px;
  width: 150px;
}
</style>

