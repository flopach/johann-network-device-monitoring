from django.shortcuts import render
from django.core.serializers import serialize
from django.forms.models import model_to_dict
from django.core.files.storage import default_storage
from django.conf import settings
from requests.utils import CaseInsensitiveDict
from .forms import AddSingleDevice,ImportMultipleDevices
from .models import iosxe_device,iosxe_device_interfaces
from .tasks import task_add_devices_single, task_add_devices_multiple, task_tools_raw_json, task_tools_enable_restconf, task_refresh_all
import logging

logger = logging.getLogger("applogger")

def index(response):
    logger.warning("I clicked on index!")
    return render(response, "main/index.html", {})

def add_devices_single(response):
    """
    Add single device
    """
    if response.method == "POST":
        form = AddSingleDevice(response.POST)

        if form.is_valid():
            task = task_add_devices_single.delay(form.cleaned_data["device_ip"],form.cleaned_data["device_username"],form.cleaned_data["device_password"])

        return render(response, "main/add_devices_single.html", { "form" : form, "response_output" : task.id })
    else:
        form = AddSingleDevice()
    return render(response, "main/add_devices_single.html", { "form" : form })

def add_devices_multiple(response):
    """
    Import multiple devices with CSV file
    """
    if response.method == "POST":
        form = ImportMultipleDevices(response.POST,response.FILES)
        
        if form.is_valid():
            uploaded_file = response.FILES['csv_file']
            csv_file_name = default_storage.save(uploaded_file.name, uploaded_file) #save file to default storage
            task = task_add_devices_multiple.delay(csv_file_name)
            print(csv_file_name)

        return render(response, "main/add_devices_multiple.html", { "form" : form, "response_output" : task.id })
    else:
        form = ImportMultipleDevices()
    return render(response, "main/add_devices_multiple.html", { "form" : form })

def refresh_all(response):
    """
    Refresh all device data
    """
    if response.method == "POST":
        task = task_refresh_all.delay()

        return render(response, "main/refresh_all.html", { "response_output" : task.id } )

    return render(response, "main/refresh_all.html")

def show_all_devices(response):
    """
    Show device overview
    """
    device_list = serialize("json", iosxe_device.objects.all(),fields=("hostname","ip","ios_version_brief", "part_number", "serial_number", "uptime","last_update"),)
    return render(response, "main/all_devices.html", { "device_list" : eval(device_list) })

def device_detail(response,id):
    """
    Detailed device page
    Get object from database and display it
    """
    device = model_to_dict(iosxe_device.objects.get(id=id))
    device_interfaces_list = serialize("json", iosxe_device_interfaces.objects.filter(iosxe_device=id))
    return render(response, "main/device_detail.html", { "device" : device, "device_interfaces_list" : eval(device_interfaces_list) })

def reports(response):
    """
    Export collected reports
    """
    return render(response, "main/reports.html", {})

def tools_logs(response):
    """
    Show logs
    """
    try:
        with open("{}/debug.log".format(settings.DATA_DIR),"r") as logfile:
            logs = logfile.read()
    except Exception as e:
        logs = "Error: can't fetch log file. Maybe nothing got logged yet?"
        logger.exception("Error: can't fetch log file.")

    return render(response, "main/tools_logs.html", { "logs" : logs })

def tools_raw_json(response):
    """
    Get raw JSON from the device (before inserting into database)
    """
    if response.method == "POST":
        form = AddSingleDevice(response.POST)

        if form.is_valid():
            task = task_tools_raw_json.delay(form.cleaned_data["device_ip"],form.cleaned_data["device_username"],form.cleaned_data["device_password"])

        return render(response, "main/tools_raw_json.html", { "form" : form, "response_output" : task.id })
    else:
        form = AddSingleDevice()
    return render(response, "main/tools_raw_json.html", { "form" : form })

def tools_enable_restconf(response):
    """
    Try enabling RESTCONF on device
    """
    if response.method == "POST":
        form = AddSingleDevice(response.POST)

        if form.is_valid():
            task = task_tools_enable_restconf.delay(form.cleaned_data["device_ip"],form.cleaned_data["device_username"],form.cleaned_data["device_password"])

        return render(response, "main/tools_enable_restconf.html", { "form" : form, "response_output" : task.id })
    else:
        form = AddSingleDevice()
    return render(response, "main/tools_enable_restconf.html", { "form" : form })
