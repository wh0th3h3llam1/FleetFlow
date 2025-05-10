export default {
    SET_TICKETS_DATA(state, data) {
        state.ticketList = data.results;
        state.totalItems = data.count
    },
    ADD_TICKET_DETAILS(state, payload) {
        state.ticketList.unshift(payload);
    },
    SET_TICKET_DETAILS_INTO_LIST(state, payload) {
        state.ticketList.splice(state.ticketList.indexOf(state.ticketList.find(v => v.id == payload.id)), 1, payload);
    },
    SET_TICKET_DETAILS(state, payload) {
        state.ticketDetails = payload;
    },
    SET_TICKET_LOGS(state, payload) {
        state.ticketLogs = payload;
    },
    SYNC_TICKET_FORM_DETAILS(state, data) {
        state.ticketDetails[data.key] = data.value;
    },
    SET_COMMENT_INTO_TICKET_DETAILS(state, data) {
        state.ticketDetails.ticket_comments.push(data);
    },
}