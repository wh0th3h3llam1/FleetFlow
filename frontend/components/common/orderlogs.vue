<template>
  <div>
    <v-row no-gutters class="border-x-light_grey border-y-light_grey">
      <v-col
        cols="12"
        class="
          border-x-light_grey
          border-y-light_grey
          text-center
          pa-6
          text-h5 text-uppercase
          background-light_grey
          font-weight-bold
        "
      >
        Logs
      </v-col>
    </v-row>
    <v-row
      no-gutters
      class="px-3 overflow-y-auto order-details-container"
      v-if="orderDetail.logs.length !== 0"
    >
      <v-timeline dense>
        <v-timeline-item
          small
          v-for="(log, index) in orderDetail.logs"
          :key="index"
          class="pb-2"
          :color="orderDetail.status"
        >
          <v-card class="elevation-0 pa-3" outlined>
            <v-card-text class="pt-1">
              <v-row>
                <v-col class="ma-0 pb-0" cols="6">
                  <span
                    :class="`text-${orderDetail.status}`"
                    class="font-weight-bold"
                  >
                    {{ log.added_by }}
                  </span>
                </v-col>
                <v-col class="ma-0 pb-0 d-flex justify-end" cols="6">
                  <span class="caption font-weight-bold">
                    {{ log.created }}
                  </span>
                </v-col>
                <v-col class="ma-0 pt-0 pb-0 body-2" cols="12">
                  <span> {{ log.message }} </span>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-timeline-item>
      </v-timeline>
    </v-row>
    <v-row no-gutters class="px-3" v-if="orderDetail.logs.length == 0">
      <v-col cols="12" class="text-body-2 text-uppercase text-center pt-6">
        No Logs To show
      </v-col>
    </v-row>
  </div>
</template>

<script>
export default {
  props: {
    orderDetail: {
      required: true,
      type: Object,
    },
  },
};
</script>

<style>
.order-details-container {
  max-height: 600px !important;
}
</style>