from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.VMclass)
# admin.site.register(models.VMInstance)
admin.site.register(models.LinodeSetting)
