from django.contrib import admin
from .models import iosxe_device,iosxe_device_cred,iosxe_device_interfaces

# Register your models here.
admin.site.register(iosxe_device)
admin.site.register(iosxe_device_cred)
admin.site.register(iosxe_device_interfaces)