<template>
  <div>
    <ReportCreatereport :reportType="reportType" />
  </div>
</template>

<script>
export default {
  data() {
    return {
      reportType: null,
    };
  },
  methods: {
    changeReportType(input) {
    },
  },
};
</script>