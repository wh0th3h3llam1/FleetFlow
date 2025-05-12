import logging
import os

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q, Sum, When, Case, Value
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.cache import cache_control
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_200_OK

from common.constants import (
    SystemRoles,
    ProjectStatus,
    TripStatus,
    OrderConstants,
    DriverStatus,
    TripStatusLogs,
)
from common.mixins import CreateListMixin
from users.models import Role
from users.serializers import UserSerializer
from dms.filters import DriverListFilter
from dms.helpers import generate_excel_report
from dms.models import Driver, StatusKeyword, Project, Vehicle, Zone, Trip, Order, DriverDocument
from dms.serializers import (
    DriverSerializer,
    TripSerializer,
    DriverDocumentSerializer,
    OrderSerializer,
)

logger = logging.getLogger(__name__)


class DriverViewSet(
    CreateListMixin,
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    serializer_class = DriverSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_class = DriverListFilter
    search_fields = (
        "project__project_id",
        "user__first_name",
        "user__last_name",
        "project__project_name",
        "user__username",
        "status",
        "vehicle_assigned__vehicle_plate_no",
        "zone__zone_name",
    )

    def get_queryset(self):
        return Driver.objects.select_related("user", "project", "vehicle_assigned", "zone").filter(
            project__project_id__in=self.request.user.projects_with_access
        )

    def list(self, request, *args, **kwargs):
        project_id = request.query_params.get("project__project_id", False)
        if request.query_params.get("trip_date"):
            trip_date = request.query_params.get("trip_date")
            queryset = self.get_queryset().exclude(
                driver_trips__status__in=[TripStatus.ACTIVE, TripStatus.PAUSED]
            )
            queryset = queryset.exclude(
                driver_trips__status=TripStatus.SCHEDULED, driver_trips__trip_date=trip_date
            )
            if project_id:
                queryset = queryset.filter(project__project_id=project_id)
            queryset = queryset.filter(vehicle_assigned__isnull=False)
        else:
            limit = request.query_params.get("limit")
            queryset = self.filter_queryset(self.get_queryset())
            if limit == "all":
                page = None
            else:
                page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

        is_active = request.query_params.get("is_active")
        if is_active in ["true", "True"]:
            queryset = queryset.filter(is_active=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True
        exclude = kwargs.pop("exclude", [])
        if self.action in [
            "list",
        ]:
            exclude.extend(
                [
                    "projects",
                    "zones",
                    "vehicles",
                    "health_card_number",
                    "health_card_expiry",
                    "national_id_expiry",
                    "national_id_image",
                    "salary",
                ]
            )

        if exclude:
            kwargs["exclude"] = exclude
        return super().get_serializer(*args, **kwargs)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["role"] = Role.objects.get(role_name=SystemRoles.DRIVER, is_system_defined=True)
        projects = Project.objects.filter(
            Q(status=ProjectStatus.ACTIVE)
            & Q(project_id__in=self.request.user.projects_with_access)
        )
        context["all_projects"] = projects
        context["all_vehicles"] = Vehicle.objects.filter(
            project__project_id__in=self.request.user.projects_with_access
        )
        context["all_zones"] = Zone.objects.filter(project__in=projects)
        return context

    def bulk_upload_driver(self, data, context):
        user_list = []
        for rec in data:
            username = rec.get("username", None)
            password = rec.get("password", None)
            first_name = rec.get("first_name", None)
            last_name = rec.get("last_name", None)
            contact_number = rec.get("contact_number", None)
            profile_image = rec.get("profile_image", None)
            role = context["role"]

            errors = {}
            user_serializer = None

            if not (username and password and contact_number and first_name and last_name):
                if not first_name:
                    errors["first_name"] = "First Name is a required field."
                if not last_name:
                    errors["last_name"] = "Last Name is a required field."
                if not username:
                    errors["username"] = "Username is a required field."
                if not password:
                    errors["password"] = "Password is a required field."
                if not contact_number:
                    errors["contact_number"] = "Contact number is a required field."

            else:
                user_details = {
                    "username": username,
                    "password": password,
                    "contact_number": contact_number,
                    "role": role.id,
                    "profile_image": profile_image,
                    "first_name": first_name,
                    "last_name": last_name,
                }
                user_list.append(user_details)

        user_serializer = UserSerializer(data=user_list, many=True)
        error_list = []
        if not user_serializer.is_valid():
            for errors in user_serializer.errors:
                errors_dict = {}
                for field in errors:
                    errors_dict[field] = [str(i) for i in errors[field]]
                error_list.append(errors_dict)
        driver_serializer = self.get_serializer(
            data=data, exclude=["projects", "vehicles", "zones"], many=True
        )
        if not driver_serializer.is_valid():
            for index, driver_errors in enumerate(driver_serializer.errors):
                driver_errors_dict = {}
                for field in driver_errors:
                    try:
                        error_list[index][field] = [str(i) for i in driver_errors[field]]
                    except IndexError:
                        driver_errors_dict[field] = [str(i) for i in driver_errors[field]]
                        error_list.append(driver_errors_dict)

        if error_list:
            return Response(error_list, status=HTTP_400_BAD_REQUEST)

        users = user_serializer.save()
        for index, rec in enumerate(users):
            driver_serializer.validated_data[index].update({"user": rec})
        driver_serializer.save()
        headers = self.get_success_headers(driver_serializer.data)
        return Response(
            {"data": driver_serializer.data, "success": True},
            status=HTTP_201_CREATED,
            headers=headers,
        )

    def create(self, request, *args, **kwargs):
        context = self.get_serializer_context()
        if isinstance(request.data, list):
            response = self.bulk_upload_driver(request.data, context)
            return response
        username = request.data.get("username", None)
        password = request.data.get("password", None)
        first_name = request.data.get("first_name", None)
        last_name = request.data.get("last_name", None)
        contact_number = request.data.get("contact_number", None)
        profile_image = request.data.get("profile_image", None)
        role = context["role"]

        errors = {}
        user_serializer = None

        if not (username and password and contact_number):
            if not username:
                errors["username"] = "Username is a required field."
            if not password:
                errors["password"] = "Password is a required field."
            if not contact_number:
                errors["contact_number"] = "Contact number is a required field."

        else:
            user_details = {
                "username": username,
                "password": password,
                "contact_number": contact_number,
                "role": role.id,
                "profile_image": profile_image,
                "first_name": first_name,
                "last_name": last_name,
            }

            user_serializer = UserSerializer(data=user_details)
            if not user_serializer.is_valid():
                for field in user_serializer.errors:
                    errors[field] = str(user_serializer.errors[field][0])

        driver_serializer = self.get_serializer(
            data=request.data, exclude=["projects", "vehicles", "zones"]
        )
        if not driver_serializer.is_valid():
            for field in driver_serializer.errors:
                errors[field] = str(driver_serializer.errors[field][0])

        if errors:
            return Response({"errors": errors, "success": False}, status=HTTP_400_BAD_REQUEST)

        user = user_serializer.save()
        driver_serializer.save(user=user)
        headers = self.get_success_headers(driver_serializer.data)
        return Response(
            {"data": driver_serializer.data, "success": True},
            status=HTTP_201_CREATED,
            headers=headers,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        context = self.get_serializer_context()
        username = request.data.get("username", None)
        password = request.data.get("password", None)
        first_name = request.data.get("first_name", None)
        last_name = request.data.get("last_name", None)
        contact_number = request.data.get("contact_number", None)
        profile_image = request.data.get("profile_image", None)
        role = context["role"]

        errors = {}

        user_details = {
            "password": password,
            "contact_number": contact_number,
            "role": role.id,
            "profile_image": profile_image,
            "first_name": first_name,
            "last_name": last_name,
        }

        user_details = {k: v for k, v in user_details.items() if v is not None}

        if username and username != instance.user.username:
            user_details.update({"username": username})

        user_serializer = UserSerializer(instance.user, data=user_details, partial=True)
        if not user_serializer.is_valid():
            for field in user_serializer.errors:
                errors[field] = str(user_serializer.errors[field][0])

        driver_serializer = self.get_serializer(
            instance, data=request.data, exclude=["projects", "vehicles", "zones"], partial=partial
        )
        if not driver_serializer.is_valid():
            for field in driver_serializer.errors:
                errors[field] = str(driver_serializer.errors[field][0])

        if errors:
            return Response({"errors": errors, "success": False}, status=HTTP_400_BAD_REQUEST)

        if user_serializer:
            user = user_serializer.save()
        else:
            user = instance.user
        driver_serializer.save(user=user)
        headers = self.get_success_headers(driver_serializer.data)
        return Response(
            {"data": driver_serializer.data, "success": True}, status=HTTP_200_OK, headers=headers
        )

    @action(methods=["GET"], detail=False)
    def download(self, request):
        report_name = "Drivers"
        headers = [
            "First Name",
            "Last Name",
            "Username",
            "Password",
            "Contact Number",
            "Project Id",
            "Zone",
            "Shift Start",
            "Shift End",
            "Status",
            "License Number",
            "License Expiry",
            "Nationality",
            "National Id Expiry",
            "Health Card Number",
            "Health Card Expiry",
            "Salary",
            "Service Type",
            "Vehicle Assigned",
        ]

        driver_status_mapping = {
            DriverStatus.ON_DUTY: "On Duty",
            DriverStatus.OFF_DUTY: "Off Duty",
            DriverStatus.ON_TRIP: "On Trip",
            DriverStatus.ON_BREAK: "Break",
            DriverStatus.DEACTIVATED: "Deactivated",
        }
        driver_status_whens = [
            When(status=k, then=Value(v)) for k, v in driver_status_mapping.items()
        ]
        project_list = request.query_params.get("project__project_id")
        if not project_list:
            project_list = self.request.user.projects_with_access
        else:
            project_list = project_list.split(",")
        drivers = (
            Driver.objects.select_related("project", "user", "zone", "vehicle_assigned")
            .filter(project__project_id__in=project_list)
            .annotate(drv_status=Case(*driver_status_whens, output_field=models.CharField()))
        )
        data = []
        for driver in drivers:
            project_id = driver.project.project_id if driver.project else ""
            data.append(
                [
                    driver.user.first_name,
                    driver.user.last_name,
                    driver.user.username,
                    "",
                    driver.user.contact_number,
                    project_id,
                    driver.zone_name,
                    driver.shift_start_time,
                    driver.shift_end_time,
                    driver.drv_status,
                    driver.license_number,
                    driver.license_expiry_date,
                    driver.nationality,
                    driver.national_id_expiry_date,
                    driver.health_card_number,
                    driver.health_card_expiry_date,
                    driver.salary,
                    driver.service_type,
                    driver.vehicle,
                ]
            )
        response = generate_excel_report(data, report_name, headers)
        return response

    @action(methods=["POST"], detail=True)
    def upload(self, request, *args, **kwargs):
        driver_id = kwargs.get("pk", None)
        if driver_id:
            added_by = request.user.id
            data = {
                "driver": driver_id,
                "document_type": request.data.get("document_type", None),
                "document": request.data.get("document", None),
                "description": request.data.get("description", None),
                "added_by": added_by,
            }
            response = DriverDocumentSerializer(data=data)
            if response.is_valid():
                response.save()
                return JsonResponse(
                    {"message": "File Uploaded Successfully"}, status=status.HTTP_200_OK
                )
            return JsonResponse({"errors": response.errors}, status=status.HTTP_400_BAD_REQUEST)
        return JsonResponse({"message": "No vehicle found"}, status=status.HTTP_400_BAD_REQUEST)


class DriverDocumentViewSet(
    viewsets.GenericViewSet,
    mixins.DestroyModelMixin,
):
    serializer_class = DriverDocumentSerializer
    permission_classes = (IsAuthenticated,)
    queryset = DriverDocument.objects.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        response = self.perform_destroy(instance)
        if response:
            return JsonResponse(
                {"message": "Document Deleted Successfully"}, status=status.HTTP_200_OK
            )
        else:
            return JsonResponse(
                {"message": "Document Not deleted"}, status=status.HTTP_400_BAD_REQUEST
            )

    def perform_destroy(self, instance):
        file_path = instance.document.path
        try:
            os.remove(f"{file_path}")
        except Exception as e:
            logger.exception(e)
            return False
        else:
            instance.delete()
            return True


@login_required(login_url=settings.LOGIN_DRIVER_URL)
def update_trip_status(request, id=None, status=None):
    trip = Trip.objects.get(id=id)
    trip_statuses = [TripStatus.ACTIVE, TripStatus.COMPLETED, TripStatus.PAUSED]

    order_statuses = list(trip.trip_orders.all().values("status"))

    driver = trip.driver

    if status == TripStatus.COMPLETED:
        if any(OrderConstants.OrderStatus.ASSIGNED == i["status"] for i in order_statuses) or any(
            OrderConstants.OrderStatus.PICKED_UP == i["status"] for i in order_statuses
        ):
            messages.add_message(
                request,
                messages.ERROR,
                "You must mark all orders as successful/failed before completing trip",
            )
            return redirect(to=driver_trip_detail)
        trip.complete_trip()

    # Turning Trip from SCHEDULED to ACTIVE
    if trip.status == TripStatus.SCHEDULED and status == TripStatus.ACTIVE:
        helper_name = request.POST.get("helper_name")
        trip.helper_name = helper_name
        trip.start_trip()

    # Turning Trip from ACTIVE to PAUSED / Driver is ON_BREAK
    elif trip.status == TripStatus.ACTIVE and status == TripStatus.PAUSED:
        trip.add_driver_break(driver, None)

        driver.status = DriverStatus.ON_BREAK
        driver.save()

        trip.status = TripStatus.PAUSED
        trip.save()
        return redirect(to=driver_trip_detail)

    # Turning Trip from PAUSED to ACTIVE
    elif trip.status == TripStatus.PAUSED and status == TripStatus.ACTIVE:
        driver.status = DriverStatus.ON_DUTY
        trip.complete_driver_break(driver, None)
        driver.save()

        trip.status = TripStatus.ACTIVE
        trip.save()
        return redirect(to=driver_trip_detail)

    if status in trip_statuses:
        trip.status = status
        trip.save()
    else:
        messages.add_message(request, messages.ERROR, "Incorrect Trip status provided.")
    return redirect(to=driver_trip_detail)


@login_required(login_url=settings.LOGIN_DRIVER_URL)
def update_order_status(request, status=None):
    if request.method == "POST":
        order_id = request.POST.get("order_id")
        status_keyword_id = request.POST.get(f"{status}_keyword")
        driver_remarks = request.POST.get("driver_remarks")
        try:
            order = Order.objects.prefetch_related("order_items").get(id=order_id)
        except Exception as e:
            logger.exception(e)
            messages.add_message(request, messages.ERROR, "No Order Found")
            return redirect(to=driver_trip_detail)

        if status in OrderConstants.OrderStatus.SUCCESSFUL:
            try:
                quantity_delivered_list = list()

                for key, value in request.POST.items():
                    if key.startswith("item_"):
                        quantity_delivered_list.append(int(value))

            except Exception as e:
                logger.exception(e)
                return redirect(to=driver_trip_detail)

            error = False
            for index, order_item in enumerate(order.order_items.all()):
                if order_item.original_quantity < quantity_delivered_list[index]:
                    error = True
                    messages.add_message(
                        request,
                        messages.ERROR,
                        "Delivered Quantity must be less than Original Quantity",
                    )
                else:
                    order_item.delivered_quantity = quantity_delivered_list[index]
                    order_item.save()
            if error:
                return redirect(to=driver_trip_detail)
        elif status in OrderConstants.OrderStatus.FAILED:
            pass
        else:
            messages.add_message(request, messages.ERROR, "Incorrect Order status provided.")
            return redirect(to=driver_trip_detail)

        try:
            sk = StatusKeyword.objects.get(id=status_keyword_id)
            order.status_keyword = sk
        except Exception as e:
            logger.exception(e)
        finally:
            order.status = status
            order.driver_remarks = driver_remarks
            order.save()

        return redirect(to=driver_trip_detail)
    return redirect(to=driver_trip_detail)


@login_required(login_url=settings.LOGIN_DRIVER_URL)
def upload_order_pod(request):
    if request.method == "POST":
        try:
            pod = request.FILES["pod"]
            order_id = request.POST["order_id"]
            order = Order.objects.get(id=order_id)
            success = order.upload_pod(pod, request.user)
            if success:
                order.save()
                messages.add_message(
                    request, messages.SUCCESS, "Proof of Delivery uploaded successfully."
                )
            else:
                messages.add_message(request, messages.ERROR, "Error Uploading Proof of Delivery.")
        except Exception as e:
            logger.exception(e)
            messages.add_message(request, messages.ERROR, "Error Uploading Proof of Delivery.")
    return redirect(to=driver_trip_detail)


@login_required(login_url=settings.LOGIN_DRIVER_URL)
def upload_order_cod(request):
    if request.method == "POST":
        try:
            amount_collected = request.POST.get("amount_collected")
            order_id = request.POST.get("order_id")
            try:
                order = Order.objects.get(id=order_id)
            except Order.DoesNotExist as odne:
                logger.exception(odne)
                return redirect(to=driver_trip_detail)
            if order.payment_type == OrderConstants.PaymentMethod.COD:
                order.payment_collected = int(amount_collected)
                order.save()
                messages.add_message(request, messages.SUCCESS, "COD added successfully.")
            else:
                messages.add_message(
                    request, messages.ERROR, "Payment can only be collected for COD Order"
                )
        except ValueError as ve:
            logger.exception(ve)
            messages.add_message(request, messages.ERROR, "COD Amount must be a number.")
        except ValidationError as ve:
            logger.exception(ve)
            messages.add_message(request, messages.ERROR, "COD Amount must be a number.")
        except Exception as e:
            logger.exception(e)
            messages.add_message(request, messages.ERROR, "Error Uploading COD Amount.")
    return redirect(to=driver_trip_detail)


@login_required(login_url=settings.LOGIN_DRIVER_URL)
def update_driver_status(request, status=None):
    if request.user.is_authenticated:

        driver_statuses = [DriverStatus.OFF_DUTY, DriverStatus.ON_BREAK, DriverStatus.ON_DUTY]
        if status in driver_statuses:
            driver = Driver.objects.prefetch_related("driver_trips").get(user=request.user)

            try:
                current_trip = driver.current_trip
                # Turning Driver from OFF_DUTY to ON_DUTY
                if status == DriverStatus.ON_DUTY:
                    # driver.add_attendance_log(DriverStatus.ON_DUTY)
                    current_trip.add_trip_log(TripStatusLogs.on_duty)

                # Turning Driver from ON_DUTY to OFF_DUTY
                if status == DriverStatus.OFF_DUTY:

                    order_statuses = list(driver.current_trip.trip_orders.all().values("status"))
                    if any("assigned" == i["status"] for i in order_statuses) or any(
                        "pickedup" == i["status"] for i in order_statuses
                    ):
                        messages.add_message(
                            request,
                            messages.ERROR,
                            "You must mark all orders as successful/failed before going off duty",
                        )
                        return redirect(to=driver_trip_detail)

                    if driver.current_trip.status != "completed":
                        messages.add_message(
                            request,
                            messages.ERROR,
                            "You must complete your trip before going off duty",
                        )
                        return redirect(to=driver_trip_detail)

                    # driver.add_attendance_log(DriverStatus.OFF_DUTY)
                    current_trip.add_trip_log(TripStatusLogs.off_duty)

            except AttributeError as ae:
                logger.exception(ae)

            driver.status = status
            driver.save()
            driver.add_attendance_log(status)

        return redirect(to=driver_trip_detail)
    return redirect(to=driver_trip_detail_login)


@login_required(login_url=settings.LOGIN_DRIVER_URL)
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def driver_trip_detail(request):
    user = request.user

    if user is not None and user.role.role_name == "Driver":

        driver_details = None
        current_trip = None
        upcoming_trip = None
        driver_trip_orders = None
        order_success_keywords = None
        order_failed_keywords = None
        trip_items = 0
        order_info = None

        try:
            driver_details = (
                Driver.objects.prefetch_related("driver_trips__trip_orders__customer_address")
                .select_related("vehicle_assigned")
                .get(user=user)
            )
        except Driver.DoesNotExist as drdne:
            logger.exception(drdne)
            messages.add_message(request, messages.ERROR, "No Driver Found")
            return redirect(to=driver_trip_detail_login)

        try:
            current_trip = driver_details.current_trip
            trip_orders = (
                current_trip.trip_orders.prefetch_related("order_items")
                .all()
                .order_by("sequence_number")
            )
            trip_items = trip_orders.aggregate(items=Sum("order_items__original_quantity")).get(
                "items"
            )

            order_fields = (
                "reference_number",
                "execution_date",
                "pickup_address",
                "drop_address",
                "order_type",
                "delivery_window_start",
                "delivery_window_end",
                "order_value",
                "payment_type",
                "pod_required",
                "status",
                "status_keyword",
                "payment_collected",
                "sequence_number",
                "address",
                "is_pod_uploaded",
                "no_of_items",
                "pod_attachments",
                "items",
            )
            order_info = OrderSerializer(trip_orders, context={"request": request}, many=True).data
        except AttributeError as ae:
            logger.exception(ae)
            upcoming_trip = driver_details.upcoming_trip
            if upcoming_trip:
                trip_items = (
                    upcoming_trip.trip_orders.prefetch_related("order_items")
                    .aggregate(items=Sum("order_items__original_quantity"))
                    .get("items")
                )
        except Exception as e:
            logger.exception(e)

        order_success_keywords = StatusKeyword.objects.filter(
            Q(status_category="order") & Q(keyword__icontains="Success")
        )
        order_failed_keywords = StatusKeyword.objects.filter(
            Q(status_category="order") & Q(keyword__icontains="Failed")
        )

        context = {
            "orders": order_info,
            "current_trip": current_trip,
            "trip_items": trip_items,
            "driver": driver_details,
            "order_success_keywords": order_success_keywords,
            "order_failed_keywords": order_failed_keywords,
            "upcoming_trip": upcoming_trip,
        }
        return render(request, "dms/driver_trip_detail.html", context=context)

    else:
        return redirect(to=driver_trip_detail_login)


@login_required(login_url=settings.LOGIN_DRIVER_URL)
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def driver_trip_order_detail(request, id):
    user = request.user

    if user is not None and user.role.role_name == "Driver":
        order = Order.objects.get(id=id)

        order_items = order.get_detailed_order_items
        no_of_items = (
            order.order_items.all()
            .aggregate(total_quantity=Sum("original_quantity"))
            .get("total_quantity")
        )

        context = {
            "order": order,
            "order_items": order_items,
            "no_of_items": no_of_items,
        }
        return render(request, "dms/driver_trip_order_detail.html", context=context)

    else:
        return redirect(to=driver_trip_detail_login)


def driver_trip_detail_login(request):
    user = request.user

    if user.is_authenticated and user.role.role_name == "Driver":
        return redirect(to="driver_trip_detail")

    else:
        try:
            logout(request)
        except Exception as e:
            logger.exception(e)

            context = {"authenticated": False, "error": "does_not_exist"}
            return render(request, "dms/login.html", context=context)

        if request.method == "POST":
            username = request.POST["username"]
            password = request.POST["password"]
            try:
                driver = Driver.objects.get(user__username=username)
            except Driver.DoesNotExist:
                context = {"authenticated": False, "error": "does_not_exist"}
                return render(request, "dms/login.html", context=context)

            user = authenticate(request=request, username=username, password=password)
            if user is not None:
                login(request, user)

                return redirect(to="driver_trip_detail")

            context = {"authenticated": False, "error": "does_not_exist"}
            return render(request, "dms/login.html", context=context)

        else:
            return render(request, "dms/login.html")


@login_required(login_url=settings.LOGIN_DRIVER_URL)
def driver_trip_detail_logout(request):
    logout(request)
    return redirect(to=driver_trip_detail_login)


@login_required(login_url=settings.LOGIN_DRIVER_URL)
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def driver_trip_map(request):
    user = request.user

    if user is not None and user.role.role_name == "Driver":
        driver_details = Driver.objects.prefetch_related("driver_trips").get(user=user)

        context = {
            "driver_status": driver_details.status,
        }
        return render(request, "dms/driver_trip_map.html", context=context)

    else:
        return redirect(to=driver_trip_detail_login)


@login_required(login_url=settings.LOGIN_DRIVER_URL)
def driver_trip_map_details(request):
    user = request.user

    if user is not None and user.role.role_name == "Driver":
        driver_details = Driver.objects.prefetch_related("driver_trips").get(user=user)
        trip = None
        trip_details = None
        order_locations = None

        try:
            trip = driver_details.current_trip

            fields = ("id", "reference_number", "locations", "trip_route")

            trip_details = TripSerializer(trip, fields=fields).data

            order_locations = trip_details.pop("locations", None)

            [order.pop("eta") for order in order_locations.get("locations", None)]
        except AttributeError as ae:
            logger.exception(ae)

        data = {
            "driver_status": driver_details.status,
            "trip_details": trip_details,
            "order_locations": order_locations,
        }
        return JsonResponse(data, status=HTTP_200_OK)

    else:
        return redirect(to=driver_trip_detail_login)
