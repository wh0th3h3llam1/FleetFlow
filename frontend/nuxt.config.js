import colors from "vuetify/es5/util/colors";
import customColors from "./assets/colors";

export default {
  // Target: https://go.nuxtjs.dev/config-target
  target: "static",
  ssr: false,
  bridge: true,

  loadingIndicator: { name: "chasing-dots" },

  // Global page headers: https://go.nuxtjs.dev/config-head
  head: {
    titleTemplate: "Fleet Flow",
    title: "chefme",
    htmlAttrs: {
      lang: "en",
    },
    meta: [
      { charset: "utf-8" },
      { name: "viewport", content: "width=device-width, initial-scale=1" },
      { hid: "description", name: "description", content: "" },
    ],
    link: [{ rel: "icon", type: "image/x-icon", href: "/favicon.png" }],
  },

  env: {
    mapsKey: "AIzaSyBSDsacsBXhb8vOapAUoDk1ETaoVfmBHMo",
  },

  // Global CSS: https://go.nuxtjs.dev/config-css
  css: [
    "~/assets/scss/aggrid.scss",
    "~/assets/scss/global.scss",
    "node_modules/vue-multiselect/dist/vue-multiselect.min.css",
  ],

  // Plugins to run before rendering page: https://go.nuxtjs.dev/config-plugins
  plugins: [
    { src: "~/plugins/axios", ssr: false },
    { src: "~/plugins/notification.js", ssr: false },
    { src: "~/plugins/workerLoader.js", ssr: false },
  ],

  // Auto import components: https://go.nuxtjs.dev/config-components
  components: true,

  // Modules for dev and build (recommended): https://go.nuxtjs.dev/config-modules
  buildModules: [
    // https://go.nuxtjs.dev/vuetify
    "@nuxtjs/vuetify",
  ],

  router: {
    mode: "hash",
  },

  // Modules: https://go.nuxtjs.dev/config-modules
  modules: [
    // https://go.nuxtjs.dev/axios
    "@nuxtjs/axios",
  ],

  // Axios module configuration: https://go.nuxtjs.dev/config-axios
  axios: {
    // baseURL: "https://uat.chefme.fero.ai/"
    // baseURL: "http://127.0.0.1:8000/"
    // baseURL: "http://3.17.173.193/"
    baseURL: "https://fleetflow.aarsheth.com/"
  },
  // Vuetify module configuration: https://go.nuxtjs.dev/config-vuetify
  vuetify: {
    customVariables: ["~/assets/scss/variables.scss"],
    theme: {
      dark: false,
      themes: {
        dark: {
          primary: colors.blue.darken2,
          accent: colors.grey.darken3,
          secondary: colors.amber.darken3,
          info: colors.teal.lighten1,
          warning: colors.amber.base,
          error: colors.deepOrange.accent4,
          success: colors.green.accent3,
        },
        light: {
          ...customColors.light,
          ...customColors.solid,
        },
      },
    },
  },

  // Build Configuration: https://go.nuxtjs.dev/config-build
  build: {
    extend(config, ctx) {
      if (ctx.isClient) {
        config.module.rules.push({
          test: /\.worker\.js$/,
          loader: "worker-loader",
          exclude: /(node_modules)/,
        });
      }
    },
    // transpile: ["ag-grid-vue"],
    transpile: [({ isLegacy }) => isLegacy && "ag-grid-vue"],
  },
};