from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("index/", views.index, name="index"),
    path("add/", views.add_devices_single, name="add single device"),
    path("import/", views.add_devices_multiple, name="import devices"),
    path("devices/", views.show_all_devices, name="show all devices"),
    path("devices/<int:id>", views.device_detail, name="show device detail"),
    path("reports/", views.reports, name="reports"),
    path("logs/", views.tools_logs, name="logs"),
    path("raw_json/", views.tools_raw_json, name="raw json"),
    path("enable_restconf/", views.tools_enable_restconf, name="enable restconf"),
    path("refresh_all/", views.refresh_all, name="refresh all")
]