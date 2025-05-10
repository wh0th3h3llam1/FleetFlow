<template>
  <v-dialog
    v-model="orderPodListDialog"
    persistent
    scrollable
    max-width="30%"
    @keydown.esc="closeDialog()"
  >
    <v-card class="pa-6">
      <v-card-title class="mb-4">
        <span
          class="
            text-lg-subtitle-1 text-xl-h6 text-uppercase
            font-weight-black
            primary--text
          "
          >Proof of Delivery</span
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
      <v-card-text>
        <v-row no-gutters class="mt-2">
          <v-col cols="9">
            <v-file-input
              class="mr-2"
              ref="fileInput"
              :clearable="true"
              hide-details
              type="file"
              v-model="newPOD"
              label="Upload POD"
              prepend-inner-icon="mdi-attachment mdi-rotate-90"
              prepend-icon=""
              accept="image/*, .pdf"
              outlined
              dense
              @change="getFileData($event)"
              @click:clear="clearFileSelection()"
            ></v-file-input>
          </v-col>
          <v-col cols="3">
            <v-btn
              depressed
              color="primary"
              class="rounded"
              @click="uploadPOD"
            >
              <v-icon small class="mr-1">mdi-file-upload</v-icon>
              Upload POD
            </v-btn>
          </v-col>
        </v-row>
        <v-row no-gutters>
          <v-col cols="12" class="mt-4">
            <span class="text-subtitle-1 font-weight-bold text-grey" v-if="podList.length">
              Uploaded POD
            </span>
            <v-list v-if="podList.length">
              <v-list-item v-for="(image, i) in podList" :key="i" class="pa-0 mt-4">
                <v-list-item-title>
                  <v-card elevation="0" outlined class="pa-0 ma-0">
                    <v-card-text
                      style="position: relative"
                      class="d-flex justify-space-between"
                    >
                      <a
                        :href="image.url"
                        download
                        target="_newtab"
                        class="primary--text"
                      >
                        {{ image.name }}
                      </a>
                      <v-icon
                        @click="download(image.url, image.name)"
                        color="primary"
                        >mdi-download</v-icon
                      >
                    </v-card-text>
                  </v-card>
                </v-list-item-title>
              </v-list-item>
            </v-list>
            <span class="font-weight-bold text-subtitle-1" v-else>
              No POD Available
            </span>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
import authHeader from "~/store/authHeader";
export default {
  props: {
    value: Boolean,
  },
  data() {
    return {
      newPOD: null,
    };
  },
  computed: {
    orderPodListDialog: {
      get() {
        return this.value;
      },
      set(value) {
        this.$emit("input", value);
      },
    },
    podList() {
      return this.$store.state.order.orderDetailStore.order.pod_attachments;
    },
  },
  methods: {
    closeDialog() {
      this.orderPodListDialog = false;
    },
    download(url, name) {
      this.$axios({
        url: url,
        method: "GET",
        responseType: "blob",
      }).then((response) => {
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement("a");
        link.href = url;
        link.setAttribute("download", name);
        document.body.appendChild(link);
        link.click();
      });
    },
    getFileData(file) {
      if (file && this.imageFileCheck(file.name)) {
        this.newPOD = file;
        return true
      } else {
        this.clearFileSelection();
        this.newPOD = null;
        return false
      }
    },
    clearFileSelection() {
      this.$refs.fileInput.reset();
      this.newPOD = null;
    },
    imageFileCheck(fileName) {
      let extension = fileName.slice(
        (Math.max(0, fileName.lastIndexOf(".")) || Infinity) + 1
      );
      if (extension == "png" || extension == "jpeg" || extension == "jpg") {
        return true;
      } else {
        this.$notifier.showMessage({
          content: `Select file is not supported. Support file Types: PNG, JPEG, JPG, PDF`,
          color: "error",
        });
        return false;
      }
    },
    uploadPOD() {
      const postData = new FormData();
      postData.append("attachment_type", "pod");
      postData.append("attachments", this.newPOD);
      let order_id = this.$store.state.order.orderDetailStore.order.id
      let payload = {
        id: order_id,
        data: postData,
      }
      this.$store
        .dispatch(
          "order/orderFormStore/ADD_ATTACHMENT_INTO_ORDER",
          payload
        )
        .then((response) => {
          this.$store.dispatch("order/orderDetailStore/GET_ORDER_DETAILS", order_id)
          this.newPOD = null;
          this.$notifier.showMessage({
            content: "POD uploaded!",
            color: "success",
          });
        })
        .catch((err) => {
          this.error = err;
        });
    },
  },
};
</script>