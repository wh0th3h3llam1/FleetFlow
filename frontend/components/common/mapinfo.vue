<template>
  <div
    v-if="legends.length !== 0"
    class="position-absolute map-info-card background-white"
  >
    <v-row no-gutters class="pa-2 d-flex text-center" style="max-width: 170px">
      <v-col cols="12" class="text-body-2">-- Information --</v-col>
      <v-col cols="12" class="text-caption">
        <slot></slot>
      </v-col>
      <v-col
        cols="12"
        class="text-caption"
        v-for="(legend, index) in legends"
        :key="index"
      >
        <div>
          <v-img
            width="12%"
            class="ma-1 float-left"
            :src="legend.marker"
          ></v-img>
          <span class="my-1 mx-2 text-caption float-left">
            {{ legend.text }}
          </span>
        </div>
      </v-col>
    </v-row>
  </div>
</template>

<script>
export default {
  props: {
    legends: {
      required: true,
      type: Array,
    },
  },
};
</script>

<style>
.map-info-card {
  bottom: 20px;
  right: 5px;
}
</style>