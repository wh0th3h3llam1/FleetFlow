<template>
  <div>
    <v-tooltip top>
      <template v-slot:activator="{ on, attrs }">
        <v-btn
          class="mt-2 mr-2 edit text-white"
          depressed
          small
          v-bind="attrs"
          v-on="on"
          @click="btnedit"
          v-if="ticket_permissions.change == true"
        >
          <v-icon small class="ma-0"> mdi-pencil </v-icon>
        </v-btn>
      </template>
      <span>Edit</span>
    </v-tooltip>

    <v-tooltip top>
      <template v-slot:activator="{ on, attrs }">
        <v-btn
          class="mt-2 mr-2 grey text-white"
          depressed
          small
          v-bind="attrs"
          v-on="on"
          @click="btnClickedHandler"
        >
          <v-icon small class="ma-0"> mdi-eye </v-icon>
        </v-btn>
      </template>
      <span>View</span>
    </v-tooltip>
  </div>
</template>

<script>
export default {
  data() {
    return {};
  },
  computed: {
    ticket_permissions() {
      return this.$store.state.profile.permissions.ticket;
    }
  },
  methods: {
    btnedit() {
      this.$store.dispatch("support/GET_TICKET_DETAILS", this.params.data.id);
      this.params.context.parentComponent.editTicket(this.params.data.id);
    },
    btnClickedHandler() {
      this.$store
        .dispatch("support/GET_TICKET_DETAILS", this.params.data.id)
        .then((response) => {
          this.$store.dispatch("support/GET_TICKET_LOGS", this.params.data.id)
            .then((res) => {
              this.$router.push({
                name: "support_ticket",
                path: "/support_ticket",
              });
            })
        }
      );
    },
  },
};
</script>