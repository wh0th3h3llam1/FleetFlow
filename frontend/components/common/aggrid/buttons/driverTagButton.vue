<template>
  <div>
    <v-tooltip top>
      <template v-slot:activator="{ on, attrs }">
        <v-btn
          class="delete darken-1 text-white mt-2"
          small
          v-bind="attrs"
          v-on="on"
          @click="btnedit"
          depressed
        >
          <v-icon small class="ma-0">mdi-delete</v-icon>
        </v-btn>
      </template>
      <span>Delete Details</span>
    </v-tooltip>
  </div>
</template>

<script>
export default {
  data() {
    return {};
  },
  methods: {
    btnedit() {
      this.$store.dispatch('driver/DELETE_TAG',this.params.data.id)
    },
  },
};
</script>