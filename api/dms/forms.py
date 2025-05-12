from datetime import timezone

from django import forms
from django.contrib.gis.geos import Point

from dms.models import Order, CustomerAddress, Driver


class OrderForm(forms.ModelForm):
    pickup_latitude = forms.DecimalField(
        min_value=-90,
        max_value=90,
        required=True,
    )
    pickup_longitude = forms.DecimalField(
        min_value=-180,
        max_value=180,
        required=True,
    )
    drop_latitude = forms.DecimalField(
        min_value=-90,
        max_value=90,
        required=True,
    )
    drop_longitude = forms.DecimalField(
        min_value=-180,
        max_value=180,
        required=True,
    )

    class Meta:
        model = Order
        fields = [
            "reference_number",
            "execution_date",
            "order_type",
            "order_remarks",
            "pickup_address",
            "pickup_latitude",
            "pickup_longitude",
            "drop_address",
            "drop_latitude",
            "drop_longitude",
            "customer_address",
            "customer_name",
            "contact_person",
            "contact_email",
            "contact_number",
            "payment_type",
            "order_value",
            "require_barcode_scanning",
            "require_proof_of_delivery",
            "customer_notifications",
            "status",
            "customer_detail_link",
            "cancellation_remarks",
            "cancelled_on",
        ]
        widgets = {"pickup_point": forms.HiddenInput(), "drop_point": forms.HiddenInput()}

    def clean(self):
        super().clean()
        if any(
            x
            for x in ["drop_latitude", "drop_longitude", "pickup_latitude", "pickup_longitude"]
            if x in self.changed_data
        ):
            drop_latitude = float(self.cleaned_data["drop_latitude"])
            drop_longitude = float(self.cleaned_data["drop_longitude"])
            pickup_latitude = float(self.cleaned_data["pickup_latitude"])
            pickup_longitude = float(self.cleaned_data["pickup_longitude"])
            self.cleaned_data["pickup_point"] = Point(pickup_longitude, pickup_latitude)
            self.cleaned_data["drop_point"] = Point(drop_longitude, drop_latitude)

    def __init__(self, *args, **kwargs):
        try:
            drop_coordinates = kwargs["instance"].drop_point.tuple  # If PointField exists
            pickup_coordinates = kwargs["instance"].pickup_point.tuple
            initial = kwargs.get("initial", {})
            initial["drop_longitude"] = drop_coordinates[0]  # Set longitude from coordinates
            initial["drop_latitude"] = drop_coordinates[1]  # Set Latitude from coordinates
            initial["pickup_longitude"] = pickup_coordinates[0]  # Set longitude from coordinates
            initial["pickup_latitude"] = pickup_coordinates[1]  # Set Latitude from coordinates
            kwargs["initial"] = initial
        except (KeyError, AttributeError):
            pass
        super().__init__(*args, **kwargs)


class CustomerAddressForm(forms.ModelForm):
    latitude = forms.DecimalField(
        min_value=-90,
        max_value=90,
        required=True,
    )
    longitude = forms.DecimalField(
        min_value=-180,
        max_value=180,
        required=True,
    )

    class Meta:
        model = CustomerAddress
        exclude = []
        fields = [
            "customer_code",
            "customer_name",
            "customer_type",
            "contact_person",
            "contact_number",
            "contact_email",
            "processing_time",
            "remarks",
            "project",
            "latitude",
            "longitude",
        ]
        # widgets = {'coordinates': forms.HiddenInput()}

    def clean(self):
        super().clean()
        if any(x for x in ["latitude", "longitude"] if x in self.changed_data):
            latitude = float(self.cleaned_data["latitude"])
            longitude = float(self.cleaned_data["longitude"])
            self.cleaned_data["coordinates"] = Point(longitude, latitude)

    def __init__(self, *args, **kwargs):
        try:
            coordinates = kwargs["instance"].coordinates.tuple  # If PointField exists
            initial = kwargs.get("initial", {})
            initial["longitude"] = coordinates[0]  # Set longitude from coordinates
            initial["latitude"] = coordinates[1]  # Set Latitude from coordinates
            kwargs["initial"] = initial
        except (KeyError, AttributeError):
            pass
        super().__init__(*args, **kwargs)


class DriverLoginForm(forms.ModelForm):

    class Meta:
        model = Driver
        fields = ("user",)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", "")
        super(DriverLoginForm, self).__init__(*args, **kwargs)
        self.fields["username"] = forms.ModelChoiceField(
            queryset=Driver.objects.filter(user__username=user.username)
        )
        self.fields["password"] = forms.ModelChoiceField(
            queryset=Driver.objects.filter(user__password=user.password)
        )


class DeliveryDetailsForm(forms.Form):

    address = forms.CharField(max_length=255, required=True)
    remarks = forms.CharField(max_length=255, required=False)
    lat = forms.DecimalField(max_digits=80, decimal_places=10, required=True)
    long = forms.DecimalField(max_digits=80, decimal_places=10, required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["address"].widget.attrs.update(
            {"class": "form-control DMS-Form-Input", "type": "text", "required": "true"}
        )
        self.fields["remarks"].widget.attrs.update(
            {"class": "form-control DMS-Form-Input", "type": "text"}
        )
        self.fields["lat"].widget.attrs.update({"class": "form-control DMS-Form-Input"})
        self.fields["long"].widget.attrs.update({"class": "form-control DMS-Form-Input"})

    def clean_lat(self):
        return (
            round(float(self.cleaned_data.get("lat")), 8) if self.cleaned_data.get("lat") else None
        )

    def clean_long(self):
        return (
            round(float(self.cleaned_data.get("long")), 8)
            if self.cleaned_data.get("long")
            else None
        )
