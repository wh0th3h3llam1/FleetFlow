<template>
  <div>
    <v-tooltip top>
      <template v-slot:activator="{ on, attrs }">
        <v-btn
          class="mt-2 edit text-white"
          small
          @click="btnClickedHandler"
          depressed
          v-bind="attrs"
          v-on="on"
        >
          <v-icon small class="ma-0">mdi-pencil</v-icon>
        </v-btn>
      </template>
      <span>Edit Details</span>
    </v-tooltip>

    <v-tooltip top>
      <template v-slot:activator="{ on, attrs }">
        <v-btn
          class="mt-2 delete text-white"
          small
          v-bind="attrs"
          v-on="on"
          @click="btnDeleteUser"
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
    async btnClickedHandler() {
      this.$parent.$parent.editStatus(this.params.data.id);
    },
    async btnDeleteUser() {
      this.$parent.$parent.deleteStatus(this.params.data.id);
    },
  },
};
</script>