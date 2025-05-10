<template>
  <v-btn x-small fab icon @click="btnClickedHandler()">
    <v-icon>mdi-eye</v-icon>
  </v-btn>
</template>

<script>
export default {
  data() {
    return {
      openDriverDetails: false,
    };
  },
  methods: {
    async btnClickedHandler() {
      this.params.context.parentComponent.get_order_details(this.params.data.id)
    },
  },
};
</script>