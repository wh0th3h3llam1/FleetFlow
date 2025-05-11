from django_filters import (
    rest_framework as filters,
    DateFilter,
    CharFilter,
    BooleanFilter,
    OrderingFilter,
)

from dms.models import Driver, Trip, Vehicle, Order, Zone, Project


class DriverListFilter(filters.FilterSet):
    project__project_id = CharFilter(method="project_id__in")
    project__id = CharFilter(method="project_in")
    project = CharFilter(method="project_id__in")
    ordering = OrderingFilter(
        fields=[
            "user__first_name",
            "license_number",
            "license_expiry",
            "shift_start",
            "shift_end",
            "status",
            "is_active",
        ]
    )
    vehicle_assigned = BooleanFilter(method="is_vehicle_assigned")
    zone_assigned = BooleanFilter(method="is_zone_assigned")
    is_active = BooleanFilter(method="is_driver_active")
    status = CharFilter(method="duty_status")

    def duty_status(self, queryset, key, value):
        try:
            duty_statuses = value.split(",")
            queryset = queryset.filter(status__in=duty_statuses)
        except ValueError:
            pass
        return queryset

    def is_driver_active(self, queryset, value, *args, **kwargs):
        try:
            is_active = args[0]
            queryset = queryset.filter(is_active=is_active)
        except ValueError:
            pass
        return queryset

    def is_zone_assigned(self, queryset, key, value):
        try:
            is_zone_assigned = value
            queryset = queryset.filter(zone__isnull=not is_zone_assigned)
        except ValueError:
            pass
        return queryset

    def is_vehicle_assigned(self, queryset, value, *args, **kwargs):
        try:
            is_vehicle_assigned = args[0]
            queryset = queryset.filter(vehicle_assigned__isnull=not is_vehicle_assigned)
        except ValueError:
            pass
        return queryset

    def project_in(self, queryset, value, *args, **kwargs):
        try:
            return queryset.filter(project__id=args[0])
        except Exception as e:
            return queryset

    def project_id__in(self, queryset, value, *args, **kwargs):
        try:
            if args:
                project_ids = args[0].split(",")
                queryset = queryset.filter(project__project_id__in=project_ids)
        except ValueError:
            pass
        return queryset

    class Meta:
        model = Driver
        fields = ("project__project_id", "project__id", "ordering", "vehicle_assigned")


class VehicleListFilter(filters.FilterSet):
    project_id = CharFilter(method="project_id__in", label="Project ID")
    project = CharFilter(method="project_id__in", label="Project ID")
    status = CharFilter(method="get_status")
    ordering = OrderingFilter(
        fields=[
            "vehicle_plate_no",
            "tonnage_capacity",
            "cbm_capacity",
            "fuel_type",
            "rc_expiry_date",
            "status",
            "mileage",
        ]
    )

    zone = CharFilter(method="vehicle_zone")
    tags = CharFilter(method="vehicle_tags")

    def vehicle_tags(self, queryset, key, value):

        selected_tags = value.split(",")
        queryset = queryset.filter(vehicle_tags__tag__tag__in=selected_tags)
        return queryset

    def get_status(self, queryset, key, value):
        try:
            statuses = value.split(",")
            if statuses:
                queryset = queryset.filter(status__in=statuses)
        except ValueError:
            pass
        return queryset

    def vehicle_zone(self, queryset, value, *args, **kwargs):
        try:
            if args:
                zones = args[0].split(",")
                queryset = queryset.filter(vehicle_drivers__zone__in=zones)
        except Exception:
            pass
        return queryset

    def project_id__in(self, queryset, value, *args, **kwargs):
        try:
            if args:
                project_ids = args[0].split(",")
                queryset = queryset.filter(project__project_id__in=project_ids)
        except ValueError:
            pass
        return queryset

    class Meta:
        model = Vehicle
        fields = ("project_id", "ordering")


class ZoneListFilter(filters.FilterSet):
    project_id = CharFilter(method="project_id__in", label="Project ID")
    project = CharFilter(method="project_id__in", label="Project ID")
    ordering = OrderingFilter(fields=["zone_name", "project", "added_by", "updated_by"])
    zone_name = CharFilter(method="zone_name__in", label="Zone Name")

    def zone_name__in(self, queryset, value, *args, **kwargs):
        try:
            if args:
                zones = [z.strip() for z in args[0].split(",")]
                queryset = queryset.filter(zone_name__in=zones)
        except ValueError:
            pass
        return queryset

    def project_id__in(self, queryset, value, *args, **kwargs):
        try:
            if args:
                project_ids = args[0].split(",")
                queryset = queryset.filter(project__project_id__in=project_ids)
        except ValueError:
            pass
        return queryset

    class Meta:
        model = Zone
        fields = ("project_id", "ordering")


class ProjectsListFilter(filters.FilterSet):
    ordering = OrderingFilter(fields=["project_name", "project_id"])

    class Meta:
        model = Project
        fields = ("ordering",)


class TripFilter(filters.FilterSet):

    project = CharFilter(method="project_id__in", label="Project")
    status = CharFilter(method="status__in")
    start_date = DateFilter(field_name="trip_date", lookup_expr="gte")
    end_date = DateFilter(field_name="trip_date", lookup_expr="lte")
    ordering = OrderingFilter(fields=["trip_date", "reference_number", "status", "driver"])

    def project_id__in(self, queryset, value, *args, **kwargs):
        try:
            if args:
                projects = self.request.query_params.get("project")
                if projects:
                    project_list = projects.split(",")
                    queryset = queryset.filter(driver__project__project_id__in=project_list)
        except ValueError:
            pass
        return queryset

    def status__in(self, queryset, value, *args, **kwargs):
        try:
            statuses = self.request.query_params.get("status")
            if statuses:
                statuses = statuses.split(",")
                queryset = queryset.filter(status__in=statuses)
        except ValueError:
            pass
        return queryset

    class Meta:
        model = Trip
        fields = ("status", "reference_number", "ordering", "project")


class VehicleReportFilter(filters.FilterSet):

    vehicle = CharFilter(method="vehicle__in")
    project_id = CharFilter(method="project_id__in")
    download = BooleanFilter()
    start_date = DateFilter(field_name="vehicle_trips__trip_date", lookup_expr="gte")
    end_date = DateFilter(field_name="vehicle_trips__trip_date", lookup_expr="lte")

    def vehicle__in(self, queryset, value, *args, **kwargs):
        try:
            if args:
                vehicle_ids = args[0].split(",")
                queryset = queryset.filter(id__in=vehicle_ids)
        except ValueError:
            pass
        return queryset

    def project_id__in(self, queryset, value, *args, **kwargs):
        try:
            if args:
                project_ids = args[0].split(",")
                queryset = queryset.filter(project__project_id__in=project_ids)
        except ValueError:
            pass
        return queryset

    class Meta:
        model = Vehicle
        fields = ()


class DriverReportFilter(filters.FilterSet):

    driver = CharFilter(method="driver__in")
    project_id = CharFilter(method="project_id__in")
    download = BooleanFilter()
    start_date = DateFilter(field_name="driver_trips__trip_date", lookup_expr="gte")
    end_date = DateFilter(field_name="driver_trips__trip_date", lookup_expr="lte")
    expenses = CharFilter(method="expense_category__in")

    def driver__in(self, queryset, value, *args, **kwargs):
        try:
            if args:
                driver_ids = args[0].split(",")
                queryset = queryset.filter(id__in=driver_ids)
        except ValueError:
            pass
        return queryset

    def project_id__in(self, queryset, value, *args, **kwargs):
        try:
            if args:
                project_ids = args[0].split(",")
                queryset = queryset.filter(project__project_id__in=project_ids)
        except ValueError:
            pass
        return queryset

    def expense_category__in(self, queryset, value, *args, **kwargs):
        try:
            if args:
                expense_categories = args[0].split(",")
                queryset = queryset.filter(driver_expense__expense_category__in=expense_categories)
        except ValueError:
            pass
        return queryset

    class Meta:
        model = Driver
        fields = ()


class OrderReportFilter(filters.FilterSet):

    project_id = CharFilter(method="project_id__in")
    download = BooleanFilter()
    start_date = DateFilter(field_name="execution_date", lookup_expr="gte")
    end_date = DateFilter(field_name="execution_date", lookup_expr="lte")
    status = CharFilter(method="status__in")
    payment_type = CharFilter(field_name="payment_type")
    order_type = CharFilter(field_name="order_type")

    def project_id__in(self, queryset, value, *args, **kwargs):
        try:
            if args:
                project_ids = args[0].split(",")
                queryset = queryset.filter(project__project_id__in=project_ids)
        except ValueError:
            pass
        return queryset

    def status__in(self, queryset, value, *args, **kwargs):
        try:
            if args:
                statuses = args[0].split(",")
                queryset = queryset.filter(status__in=statuses)
        except ValueError:
            pass
        return queryset

    class Meta:
        model = Order
        fields = ()


class TripReportFilter(filters.FilterSet):

    driver = CharFilter(method="driver__in")
    vehicle = CharFilter(method="vehicle__in")
    download = BooleanFilter()
    start_date = DateFilter(field_name="trip_date", lookup_expr="gte")
    end_date = DateFilter(field_name="trip_date", lookup_expr="lte")
    status = CharFilter(method="status__in")

    def driver__in(self, queryset, value, *args, **kwargs):
        try:
            if args:
                driver_ids = args[0].split(",")
                queryset = queryset.filter(driver__id__in=driver_ids)
        except ValueError:
            pass
        return queryset

    def vehicle__in(self, queryset, value, *args, **kwargs):
        try:
            if args:
                vehicle_ids = args[0].split(",")
                queryset = queryset.filter(vehicle__id__in=vehicle_ids)
        except ValueError:
            pass
        return queryset

    def status__in(self, queryset, value, *args, **kwargs):
        try:
            if args:
                statuses = args[0].split(",")
                queryset = queryset.filter(status__in=statuses)
        except ValueError:
            pass
        return queryset

    class Meta:
        model = Trip
        fields = ()


class ItemMasterListFilter(filters.FilterSet):
    storage_type = CharFilter(method="storage_type__in", label="Storage Type")
    ordering = OrderingFilter(fields=["storage_type", "item_no", "item_description"])
    unit = CharFilter(method="unit__in", label="Unit")

    def storage_type__in(self, queryset, value, *args, **kwargs):
        STORAGES = {
            "dry": "D",
            "chilled": "C",
            "frozen": "F",
        }
        try:
            if args:
                storage_types = [
                    STORAGES.get(stype.strip().lower(), "") for stype in args[0].split(",")
                ]
                queryset = queryset.filter(storage_type__in=storage_types)
        except ValueError:
            pass
        return queryset

    def unit__in(self, queryset, value, *args, **kwargs):
        UNITS = {
            "kg": "kg",
            "case": "case",
            "each": "each",
        }
        try:
            if args:
                units = [UNITS.get(utype.strip().lower(), "") for utype in args[0].split(",")]
                queryset = queryset.filter(unit__in=units)
        except ValueError:
            pass
        return queryset
