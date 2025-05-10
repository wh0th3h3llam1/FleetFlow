<template>
  <v-snackbar v-model="show" :color="color" :right="right">
    {{ message }}
    <template v-slot:action="{ attrs }">
      <v-btn text v-bind="attrs" @click="show = false"> Close </v-btn>
    </template>
  </v-snackbar>
</template>

<script>
export default {
  data() {
    return {
      show: false,
      message: "",
      color: "",
      right: null,
    };
  },

  created() {
    this.$store.subscribe((mutation, state) => {
      if (mutation.type === "notification/showMessage") {
        this.message = state.notification.content;
        this.color = state.notification.color;
        this.show = true;
        this.right = state.notification.right;
      }
    });
  },
};
</script>