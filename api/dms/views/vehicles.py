import logging
import os

from django.db.models import Q
from django.http import JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated

from common.constants import ProjectStatus
from common.mixins import CreateListMixin
from dms.filters import VehicleListFilter
from dms.helpers import generate_excel_report
from dms.models import Vehicle, Project, VehicleDocument
from dms.serializers import VehicleSerializer, VehicleDocumentSerializer

logger = logging.getLogger(__name__)


class VehicleViewSet(
    CreateListMixin,
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    serializer_class = VehicleSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_class = VehicleListFilter
    search_fields = (
        "vehicle_plate_no",
        "project__project_id",
        "status",
        "project__project_name",
        "fuel_type",
    )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["all_projects"] = Project.objects.filter(
            status=ProjectStatus.ACTIVE, project_id__in=self.request.user.projects_with_access
        )
        existing_vehicles = Vehicle.objects.values_list("vehicle_plate_no", flat=True)
        context["existing_vehicles"] = existing_vehicles
        return context

    def get_serializer(self, *args, **kwargs):
        read_only_fields = None
        exclude = None
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True

        if self.action == "create":
            exclude = ["deactivated_on", "deactivated_by", "added_by"]

        if self.action in [
            "list",
        ]:
            exclude = (
                "insurance_policy_number",
                "insurance_expiry_date",
                "insurance_type",
                "insurance_image",
                "permits",
                "added_by",
                "updated_by",
                "deactivated_by",
                "deactivated_on",
                "sensor_info",
                "sensors",
            )

        if exclude:
            kwargs["exclude"] = exclude

        if read_only_fields:
            kwargs["read_only_fields"] = read_only_fields

        return super().get_serializer(*args, **kwargs)

    def get_queryset(self):
        return Vehicle.objects.filter(
            project__project_id__in=self.request.user.projects_with_access
        )

    def paginate_queryset(self, queryset):
        limit = self.request.query_params.get("limit")
        if limit == "all":
            page = None
        else:
            page = super(VehicleViewSet, self).paginate_queryset(queryset)
        return page

    @action(methods=["POST"], detail=True)
    def upload(self, request, *args, **kwargs):
        vehicle_id = kwargs.get("pk", None)
        if vehicle_id:
            added_by = request.user.id
            data = {
                "vehicle": vehicle_id,
                "document_type": request.data.get("document_type", None),
                "document": request.data.get("document", None),
                "description": request.data.get("description", None),
                "added_by": added_by,
            }
            response = VehicleDocumentSerializer(data=data)
            if response.is_valid():
                response.save()
                return JsonResponse(
                    {"message": "File Uploaded Successfully"}, status=status.HTTP_200_OK
                )
            return JsonResponse({"errors": response.errors}, status=status.HTTP_400_BAD_REQUEST)
        return JsonResponse({"message": "No vehicle found"}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["GET"], detail=False)
    def download(self, request):
        report_name = "Vehicles"
        headers = [
            "Licence Plate No",
            "Project Id",
            "Fuel Type",
            "Tonnage Capacity",
            "CBM Capacity",
            "Box Capacity",
            "Permits",
            "Insurance Policy Number",
            "Insurance Expiry Date",
            "Insurance Type",
            "RC Number",
            "RC Expiry Date",
            "Vehicle Make",
            "Vehicle Model",
            "Vehicle Year",
            "Vehicle Cost",
            "Mileage",
            "Status",
            "Storages",
            "Sensor Ids",
        ]
        project_list = request.query_params.get("project__project_id")
        if not project_list:
            project_list = self.request.user.projects_with_access
        else:
            project_list = project_list.split(",")
        vehicles = (
            Vehicle.objects.select_related("project")
            .prefetch_related("vehicle_storages")
            .filter(project__project_id__in=project_list)
        )
        rows = []
        for vehicle in vehicles:
            vehicle_storages = vehicle.vehicle_storages.all()
            storages = []
            sensor_ids = []
            for vehicle_storage in vehicle_storages:
                storages.append(vehicle_storage.get_storage_type_display())
                sensor_ids.append(vehicle_storage.sensor_id if vehicle_storage.sensor_id else "")
            storages = ",".join(storages)
            sensor_ids = ",".join(sensor_ids)
            project_id = vehicle.project.project_id if vehicle.project else ""
            rows.append(
                [
                    vehicle.vehicle_plate_no,
                    project_id,
                    vehicle.fuel_type,
                    vehicle.tonnage_capacity,
                    vehicle.cbm_capacity,
                    vehicle.box_capacity,
                    vehicle.permits,
                    vehicle.insurance_policy_number,
                    vehicle.insurance_expiry,
                    vehicle.insurance_type,
                    vehicle.rc_number,
                    vehicle.rc_expiry,
                    vehicle.vehicle_make,
                    vehicle.vehicle_model,
                    vehicle.vehicle_year,
                    vehicle.vehicle_cost,
                    vehicle.mileage,
                    vehicle.status,
                    storages,
                    sensor_ids,
                ]
            )

        response = generate_excel_report(rows, report_name, headers)
        return response


class VehicleDocumentViewSet(
    viewsets.GenericViewSet,
    mixins.DestroyModelMixin,
):
    serializer_class = VehicleDocumentSerializer
    permission_classes = (IsAuthenticated,)
    queryset = VehicleDocument.objects.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        response = self.perform_destroy(instance)
        if response:
            return JsonResponse(
                {"message": "Document Deleted Successfully"}, status=status.HTTP_200_OK
            )
        return JsonResponse({"message": "Document Not deleted"}, status=status.HTTP_400_BAD_REQUEST)

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
