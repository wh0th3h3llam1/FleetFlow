from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import operations as operations_views
from .views.common import (
    ProjectViewSet,
    StatusKeywordViewSet,
    ZoneViewset,
    PlanningTemplateViewSet,
    UserNotificationViewSet,
    TagViewSet,
)
from .views.dashboard import Dashboard
from .views.drivers import DriverViewSet, DriverDocumentViewSet
from .views.orders import (
    BulkUploadB2COrderView,
    CustomerAddressViewSet,
    ItemMasterViewSet,
    UpdateDeliveryDetails,
    BulkUploadOrderItemView,
    OrderViewSet,
    OrderItemViewSet,
    BulkUpdateOrderView,
    OrderAttachmentViewSet,
    OrderListView,
)
from .views.profiles import ProfileView
from .views.reports import (
    VehicleReportsViewSet,
    DriverReportsViewSet,
    OrderReportsViewSet,
    TripReportsViewSet,
)
from .views.roles import RoleViewSet
from .views.trips import TripViewSet, TripOrdersViewSet
from .views.users import UserViewSet
from .views.vehicles import VehicleViewSet, VehicleDocumentViewSet

from .reports.views import ReportsViewSet

router = DefaultRouter()

# core URLS

router.register("order", OrderViewSet, basename="order")
router.register("order-attachments", OrderAttachmentViewSet, basename="order-attachments")

router.register("order-item", OrderItemViewSet, basename="order-item")
router.register("project", ProjectViewSet, basename="project")
router.register("statuses", StatusKeywordViewSet, basename="statuses")
router.register("tags", TagViewSet, basename="tags")
router.register("driver", DriverViewSet, basename="driver")
router.register("driver-document", DriverDocumentViewSet, basename="driver-document")

router.register("customer_address", CustomerAddressViewSet, basename="customer_address")
router.register("items", ItemMasterViewSet, basename="items")
router.register("vehicle", VehicleViewSet, basename="vehicle")
router.register("vehicle-document", VehicleDocumentViewSet, basename="vehicle-document")

router.register("trip", TripViewSet, basename="trip")
router.register("zones", ZoneViewset, basename="zones")
router.register("filter_trip_orders", TripOrdersViewSet, basename="filter_trip_orders")

router.register("role", RoleViewSet, basename="role")
router.register("user", UserViewSet, basename="user")

router.register("planning_template", PlanningTemplateViewSet, basename="planning_template")

# Report Urls:
router.register("reports", ReportsViewSet, basename="reports")
router.register("trip_reports", TripReportsViewSet, basename="trip-reports")
router.register("vehicle_reports", VehicleReportsViewSet, basename="vehicle-reports")
router.register("driver_reports", DriverReportsViewSet, basename="driver-reports")
router.register("order_reports", OrderReportsViewSet, basename="order-reports")
router.register("notification", UserNotificationViewSet, basename="user-notifications")

# Dashboard:
router.register("dashboard", Dashboard, basename="dashboard"),


urlpatterns = [
    path("orders/bulk_upload", BulkUploadOrderItemView.as_view(), name="order-bulk-upload"),
    path("orders/bulk_upload_b2c", BulkUploadB2COrderView.as_view(), name="order-bulk-upload-b2c"),
    path("orders/bulk_update", BulkUpdateOrderView.as_view(), name="order-bulk-update"),
    path("profile/", ProfileView.as_view(), name="user-profile"),
    path(
        "orders/delivery_details/<str:notification_id>",
        UpdateDeliveryDetails.as_view(),
        name="update-delivery-details",
    ),
    path("operations/drivers/", operations_views.DriverListView.as_view(), name="op-driver-list"),
    path(
        "operations/trips/<int:trip_id>/",
        operations_views.TripDetailView.as_view(),
        name="op-trip-detail",
    ),
    path("operations/overview/", operations_views.OperationOverview.as_view(), name="op-operview"),
    path("", include(router.urls)),
    path("order-list/", OrderListView.as_view(), name="order-list"),
]
