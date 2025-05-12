<template>
  <v-navigation-drawer
    permanent
    clipped
    app
    mini-variant
    expand-on-hover
    width="250"
    class="primary navigation-shadow"
    style="z-index:11 !important"
    dark
  >
    <v-list dense>
      <v-list-item
        class="border-bottom-light_maroon"
        v-for="(item, i) in navMenu"
        :key="i"
        :to="item.to"
        router
        exact
      >
        <v-list-item-action>
          <v-icon class="text-h6 font-weight-light">{{ item.icon }}</v-icon>
        </v-list-item-action>
        <v-list-item-content>
          <v-list-item-title v-text="item.title" />
        </v-list-item-content>
      </v-list-item>
    </v-list>
  </v-navigation-drawer>
</template>

<script>
export default {
  data() {
    return {};
  },
  computed: {
    navMenu() {
      return this.$store.getters["profile/MENU"];
    },
  },
};
</script>

<style lang="scss">
.navigation-shadow {
  &:hover {
    box-shadow: black 4px 0px 20px -10px !important;
  }
}
</style>