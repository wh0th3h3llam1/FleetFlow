<template>
  <div>
    <DriverDriverlist />
    <BulkUpload v-model="bulkUploadDialog" upload-to="Drivers" />
  </div>
</template>

<script>
import BulkUpload from "~/components/common/dialog/bulk-upload.vue";
export default {
  components: {
    BulkUpload,
  },
  data() {
    return {
      bulkUploadDialog: false,
    };
  },
  methods: {},
};
</script>

<style>
</style>