export default () => ({
    formOrder: {
        execution_date: new Date().toISOString().slice(0, 10),
        order_type: "delivery",
        barcode_scanning: false,
        pod_required: true,
        customer_notifications: true,
        payment_type: "prepaid",
        order_attachments : [],
        coordinates: {
            latitude: null,
            longitude: null
        }
    },
    items: [{
        quantity: null,
    }]
})