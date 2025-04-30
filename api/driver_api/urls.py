from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (DriverAppViewSet, DriverAppTripViewSet,
                    DriverAppOrderViewSet, DriverExpenseViewSet,
                    TripChatLogViewSet, DriverAppOrderItemViewSet,
                    TelemetryConfigDetailViewSet, DriverTripMetricsViewSet)

router = DefaultRouter()

router.register('driver-api', DriverAppViewSet, basename='driver-api')
router.register('driver-trip', DriverAppTripViewSet, basename='driver-trip')
router.register('driver-orders', DriverAppOrderViewSet,
                basename='driver-orders')
router.register('driver-expenses', DriverExpenseViewSet,
                basename='driver-expenses')

router.register('trip-chat', TripChatLogViewSet,
                basename='trip-chat')
router.register('driver-order-item', DriverAppOrderItemViewSet,
                basename='driver-order-item')
router.register('telementry-config', TelemetryConfigDetailViewSet,
                basename='telementry-config')
router.register('trip-metrics', DriverTripMetricsViewSet,
                basename='trip-metrics')

urlpatterns = router.urls
