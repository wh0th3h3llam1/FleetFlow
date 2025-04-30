import logging

from django.db.models import Case, When, BooleanField
from django.http import JsonResponse
from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.response import Response
from drf_extra_fields.geo_fields import PointField

from dms.mixins import CreateListMixin
from dms.models import (
    Driver, Trip, Order, DriverExpense, TripChatLog,
    OrderItem, TelemetryConfig, TripMetrics)
from dms.permissions import IsDriver
from driver_api.serializers import (
    DriverAppSerializer, DriverDetailSerializer,
    DriverAppTripSerializer, DriverAppOrderSerializer,
    PODUploadSerializer, DriverExpenseSerializer,
    TripChatLogSerializer, DriverAppOrderItemSerializer,
    DriverStatusUpdateSerializer, TelemetryConfigSerializer,
    DriverTripMetricsSerializer, UpdateOrderAddressSerializer)
from lib.choices import DRIVER_EXPENSE_CATEGORY
from lib.constants import OrderConstants

logger = logging.getLogger(__name__)


class DriverAppViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
):
    serializer_class = DriverAppSerializer
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    # permission_classes = [IsDriver,]

    def get_queryset(self):
        return Driver.objects.all()

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.action == "profile":
            serializer_class = DriverDetailSerializer
        if self.action == "status_update":
            serializer_class = DriverStatusUpdateSerializer
        return serializer_class

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated, IsDriver])
    def profile(self, request):
        driver = request.user.driver
        serializer = self.get_serializer(driver)
        return Response(serializer.data)

    @action(methods=['post'], detail=True, permission_classes=[IsAuthenticated, IsDriver])
    def status_update(self, request, pk):
        driver = self.get_object()
        serializer = self.get_serializer(driver, data=request.data)
        if serializer.is_valid():
            self.perform_update(serializer)
        else:
            return Response(serializer.errors, status=400)
        serializer = DriverDetailSerializer(driver)
        return Response(serializer.data)    


class DriverAppTripViewSet(
        viewsets.GenericViewSet,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,):

    serializer_class = DriverAppTripSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = (IsAuthenticated, IsDriver)
    lookup_field = "trip_id"

    def get_queryset(self):
        try:
            driver = self.request.user.driver
            trips = Trip.objects.filter(driver=driver)
            return trips
        except:
            trips = Trip.objects.none()
            return trips

    def get_object(self):
        url_kwargs = self.kwargs[self.lookup_field]
        pk = Trip.get_trip_pk(url_kwargs)
        self.lookup_field = "id"
        self.kwargs[self.lookup_field] = pk
        return super(DriverAppTripViewSet, self).get_object()

    @action(methods=['get'], detail=True, permission_classes=[IsAuthenticated, IsDriver])
    def get_order_items(self, request, trip_id=None):
        instance = self.get_object()
        order = [OrderConstants.StorageTypes.FROZEN, OrderConstants.StorageTypes.CHILLED,
                 OrderConstants.StorageTypes.DRY]
        order_items = OrderItem.objects.filter(order__in=instance.trip_orders.all())
        order_items = sorted(order_items, key=lambda x: order.index(x.item.storage_type))
        serializer = DriverAppOrderItemSerializer(order_items, many=True)
        return Response(serializer.data)


class DriverAppOrderViewSet(
        viewsets.GenericViewSet,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,):

    serializer_class = DriverAppOrderSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = (IsAuthenticated, IsDriver)

    def get_queryset(self):
        if self.request.user.id:
            try:
                trip = self.request.user.driver.current_trip
                orders = trip.trip_orders.prefetch_related('attachments', 'order_items').all()
            except AttributeError as e:
                orders = Order.objects.none()
            return orders
        return Order.objects.none()

    def get_serializer(self, *args, **kwargs):
        kwargs['context'] = self.get_serializer_context()
        read_only_fields = None
        exclude = None
        serializer_class = self.serializer_class
        if self.action == "retrieve":
            exclude = ["order_detail_url", ]

        if self.action == "pod_upload":
            serializer_class = PODUploadSerializer

        if exclude:
            kwargs["exclude"] = exclude

        if read_only_fields:
            kwargs["read_only_fields"] = read_only_fields

        return serializer_class(*args, **kwargs)

    @action(methods=['post'], detail=True, permission_classes=[IsAuthenticated, IsDriver])
    def pod_upload(self, request, pk=None):
        serializer = PODUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.get_object()
        instance.upload_pod(request.data.get("attachment"), request.user)
        order_serializer = DriverAppOrderSerializer(instance)
        return Response(order_serializer.data)

    @action(methods=['patch'], detail=True, permission_classes=[IsAuthenticated, IsDriver])
    def update_address(self, request, *args, **kwargs):
        order_id = kwargs.get("pk", None)
        try:
            order = Order.objects.get(id=order_id)
        except Exception as e:
            logger.exception(e)
            return Response ({"message": "No Order Found"}, status=400)
        if order:
            serializer = UpdateOrderAddressSerializer(instance=order, data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data, status=200)
            else:
                return Response(serializer.errors, status=400)
        else:
            return Response({"message": "No Order Found"}, status=400)

class DriverExpenseViewSet(
        viewsets.GenericViewSet,
        mixins.ListModelMixin,
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin):

    serializer_class = DriverExpenseSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = (IsAuthenticated, IsDriver)
    filter_backends = [SearchFilter]
    search_fields = ['expense_name', 'expense_category', 'amount']

    def get_queryset(self):
        if self.request.user.id:
            try:
                current_trip = self.request.user.driver.current_trip
                trip_expense = DriverExpense.objects.filter(trip=current_trip)
                return trip_expense
            except:
                trip_expense = DriverExpense.objects.none()
                return trip_expense
        return DriverExpense.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = self.get_paginated_response(serializer.data)
            data.data.update({'expense_category_list': DRIVER_EXPENSE_CATEGORY})
            return data
        serializer = self.get_serializer(queryset, many=True)
        data = {'results': serializer.data, 'expense_category_list': DRIVER_EXPENSE_CATEGORY}
        return Response(data)


class DriverAppOrderItemViewSet(
        viewsets.GenericViewSet,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,):

    serializer_class = DriverAppOrderItemSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = (IsAuthenticated, IsDriver)

    def get_queryset(self):
        if self.request.user.id:
            try:
                trip = self.request.user.driver.current_trip
                orders = trip.trip_orders.all()
                order_items = OrderItem.objects.filter(order__in=orders)
            except AttributeError as e:
                order_items = OrderItem.objects.none()
            return order_items
        return OrderItem.objects.none()


class TripChatLogViewSet(
        viewsets.GenericViewSet,
        mixins.ListModelMixin,
        mixins.CreateModelMixin,):

    serializer_class = TripChatLogSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsDriver]

    def get_queryset(self):
        if self.request.user.id:
            trip = None
            try:
                trip = self.request.user.driver.current_trip
            except AttributeError as e:
                trip = self.request.user.driver.upcoming_trip
            except Exception as e:
                logger.exception(e)

            if trip:
                return TripChatLog.objects.filter(trip=trip).annotate(send_by_driver=Case(When(
                    sender__username=self.request.user.username,
                    then=True), output_field=BooleanField(), default=False)).order_by('-created')
        return TripChatLog.objects.none()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        trip = None
        if self.request.user.id:
            try:
                trip = self.request.user.driver.current_trip
            except AttributeError as e:
                trip = self.request.user.driver.upcoming_trip
            except Exception as e:
                logger.exception(e)
            if trip:
                context['trip'] = trip
                context['driver'] = self.request.user.driver
        return context


class TelemetryConfigDetailViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin):

    serializer_class = TelemetryConfigSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsDriver]

    def get_queryset(self):
        return TelemetryConfig.objects.all()


class DriverTripMetricsViewSet(
    CreateListMixin,
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,):

    serializer_class = DriverTripMetricsSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsDriver]

    def get_queryset(self):
        if self.request.user.id:
            try:
                driver_trip = self.request.user.driver.current_trip
            except:
                driver_trip = self.request.user.driver.upcoming_trip
            return TripMetrics.objects.filter(trip=driver_trip)
        else:
            return TripMetrics.objects.none()
