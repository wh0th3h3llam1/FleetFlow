from django.contrib import admin
from django.contrib.auth.models import Group

# Register your models here.


admin.site.index_title = "FleetFlow API"
admin.site.site_header = "FleetFlow Admin"
admin.site.site_title = "FleetFlow Administration"

admin.site.unregister(Group)
