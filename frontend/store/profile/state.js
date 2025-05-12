export default () => ({
    userProfile: {},
    permissions: {},
    menu: [
        {
            title: "Dashboard",
            icon: "mdi-monitor-dashboard",
            to: "/",
            key: "project"
        },
        {
            title: "Operations",
            icon: "mdi-cog-transfer-outline",
            to: "/operations",
            key: "trip"
        },
        {
            title: "Trips",
            icon: "mdi-truck-fast-outline",
            to: "/trips",
            key: "trip"
        },
        {
            title: "Trip Planning",
            icon: "mdi-map-marker-distance",
            to: "/plan_trips",
            key: "trip"
        },
        {
            title: "Trip Planning Templates",
            icon: "mdi-file-cad",
            to: "/trip_planning_templates",
            key: "trip"
        },
        {
            title: "Drivers",
            icon: "mdi-card-account-details-outline",
            to: "/drivers",
            key: "driver"
        },
        {
            title: "Orders",
            icon: "mdi-archive-outline",
            to: "/orders",
            key: "order"
        },
        {
            title: "Vehicles",
            icon: "mdi-truck",
            to: "/vehicles",
            key: "vehicle"
        },
        {
            title: "Projects",
            icon: "mdi-file-document-outline",
            to: "/projects",
            key: "project"
        },
        {
            title: "Zones",
            icon: "mdi-shape-square-plus",
            to: "/zones",
            key: "zone"
        },
        {
            title: "Statuses",
            icon: "mdi-list-status",
            to: "/statuses",
            key: "order"
        },
        {
            title: "Item Master",
            icon: "mdi-inbox-multiple",
            to: "/items",
            key: "itemmaster"
        },
        {
            title: "Customers",
            icon: "mdi-account-group",
            to: "/customer_addresses",
            key: "customeraddress"
        },
        {
            title: "Reports",
            icon: "mdi-chart-areaspline",
            to: "/reports",
            key: "project"
        },
        {
            title: "Users",
            icon: "mdi-account-check",
            to: "/users",
            key: "dashuser"
        },
        {
            title: "Roles",
            icon: "mdi-account-key",
            to: "/roles",
            key: "role"
        },
        // {
        //     title: "Support",
        //     icon: "mdi-face-agent",
        //     to: "/support",
        //     key: "ticket"
        // },
    ],
    restrictedMenu: []
})