from django.contrib import admin
from .models import Location, UnitDetails, SiteDetails
# Register your models here.


admin.site.register(Location)
admin.site.register(SiteDetails)
admin.site.register(UnitDetails)