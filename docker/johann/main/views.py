from django.db.models.fields import json
from django.shortcuts import render
from django.core.serializers import serialize
from django.forms.models import model_to_dict
from django.core.files.storage import default_storage
from django.http import FileResponse
from django.conf import settings
from .forms import AddSingleDevice,ImportMultipleDevices
from .models import iosxe_device,iosxe_device_interfaces
from .tasks import task_add_devices_single, task_add_devices_multiple, task_tools_raw_json, task_tools_enable_restconf, task_refresh_all
import logging
import json
import pandas as pd
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import io


logger = logging.getLogger("applogger")

def index(response):
    return render(response, "main/index.html", {})

def add_devices_single(response):
    """
    Add single device:

    When form content is valid, start celery task and return celery task-id.
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
    Import multiple devices with CSV file.

    When form content is valid, start celery task and return celery task-id.
    """
    if response.method == "POST":
        form = ImportMultipleDevices(response.POST,response.FILES)
        
        if form.is_valid():
            uploaded_file = response.FILES['csv_file']
            csv_file_name = default_storage.save(uploaded_file.name, uploaded_file) #save file to default storage
            task = task_add_devices_multiple.delay(csv_file_name)

        return render(response, "main/add_devices_multiple.html", { "form" : form, "response_output" : task.id })
    else:
        form = ImportMultipleDevices()
    return render(response, "main/add_devices_multiple.html", { "form" : form })

def refresh_all(response):
    """
    Refresh all device data

    When form content is valid, start celery task and return celery task-id.
    """
    if response.method == "POST":
        task = task_refresh_all.delay()

        return render(response, "main/refresh_all.html", { "response_output" : task.id } )

    return render(response, "main/refresh_all.html")

def show_all_devices(response):
    """
    Show device overview

    Get listed fields from the iosxe_device table and serialize the output for displaying the data.
    """
    device_list = serialize("json", iosxe_device.objects.all(),fields=("hostname","ip","ios_version_brief", "part_number", "serial_number", "uptime","last_update"),)
    return render(response, "main/all_devices.html", { "response_output" : eval(device_list) })

def device_detail(response,id):
    """
    Detailed device page
    Get fields from the SQLite database based on the id in the URL!
    """
    device = model_to_dict(iosxe_device.objects.get(id=id))
    device_interfaces_list = serialize("json", iosxe_device_interfaces.objects.filter(iosxe_device=id))
    return render(response, "main/device_detail.html", { "device" : device, "device_interfaces_list" : eval(device_interfaces_list) })

def reports_device_stats(response):
    """
    Show valuable information out of the database with graphs
    Get the data, put them into pandas dataframes, plot figures and save them as PNG files
    """
    response_output = {}
    df_devices = pd.DataFrame.from_records(iosxe_device.objects.values("ios_version_brief","memory_status","iox")) #put data in pandas dataframe
    df_interfaces = pd.DataFrame.from_records(iosxe_device_interfaces.objects.values("oper_status")) #put data in pandas dataframe

    if df_devices.empty:
        response_output["status"] = "empty"
        return render(response, "main/reports_device_stats.html", { "response_output" : response_output })

    try:
        # Get total number of devices in the database
        response_output["total_devices"] = len(df_devices.index)

        # plot IOS XE versions
        ios_version_count = df_devices['ios_version_brief'].value_counts() 
        ios_version_plot = plt.figure(0)
        ios_version_plot = ios_version_count.plot.pie(colors=["#64bbe3", "#6abf4b", "#fbab18", "#0175a2","#e2231a"],ylabel='',shadow=True,autopct='%.2f%%',wedgeprops={"edgecolor":"k",'linewidth': 1, 'linestyle': 'solid', 'antialiased': True},title="Used IOS XE Versions")
        plt.tight_layout()
        ios_version_plot.figure.savefig("{}ios_version_count.png".format(settings.IMG_FOLDER_PATH))
        plt.close(0)

        # plot memory status health
        ios_memory_status = df_devices['memory_status'].value_counts()
        ios_memory_status_plot = plt.figure(1)
        ios_memory_status_plot = ios_memory_status.plot.bar(color=["#6abf4b", "#fbab18", "#00bceb", "#0175a2"],title="Memory Status Health")
        plt.ylabel("no of devices")
        plt.xticks(rotation=0)
        plt.tight_layout()
        ios_memory_status_plot.figure.savefig("{}ios_memory_status.png".format(settings.IMG_FOLDER_PATH))
        plt.close(1)

        # plot interfaces oper status
        interfaces_oper_status = df_interfaces["oper_status"].value_counts()
        interfaces_oper_status_plot = plt.figure(2)
        interfaces_oper_status_plot = interfaces_oper_status.plot.bar(color=["#fbab18","#6abf4b", "#00bceb", "#0175a2"],title="Operational Status of all interfaces")
        plt.xticks(rotation=45)
        plt.ylabel("no of interfaces")
        plt.tight_layout()
        interfaces_oper_status_plot.figure.savefig("{}interfaces_oper_status.png".format(settings.IMG_FOLDER_PATH))
        plt.close(2)

        #IOX enabled
        iox_status = df_devices['iox'].value_counts() 
        iox_status_plot = plt.figure(3)
        iox_status_plot = iox_status.plot.pie(colors=["#6abf4b", "#e2231a"],ylabel='',shadow=True,autopct='%.2f%%',wedgeprops={"edgecolor":"k",'linewidth': 1, 'linestyle': 'solid', 'antialiased': True},title="IOx enabled (all devices)")
        plt.tight_layout()
        iox_status_plot.figure.savefig("{}iox_status.png".format(settings.IMG_FOLDER_PATH))
        plt.close(3)

        response_output["status"] = "success"
    except Exception as e:
        response_output["status"] = "error"
        logger.exception(f"Error! Could not create report graphs: {e}")

    return render(response, "main/reports_device_stats.html", { "response_output" : response_output })

def reports_oneview(response):
    """
    Return all device information in one view
    """
    df_devices = pd.DataFrame.from_records(iosxe_device.objects.values())
    return render(response, "main/reports_oneview.html", { "response_output" : df_devices.to_html(classes="table table--lined", index=False) })

def reports_licensing(response):
    """
    Show licensing overview

    Get listed fields from the iosxe_device table and serialize the output for displaying the data.
    """
    device_list = serialize("json", iosxe_device.objects.all(),fields=("hostname","ip","lic_config_transport_type","lic_config_cslu_url","lic_udi","lic_used_licenses_list","lic_rum_ack_last","lic_rum_ack_next","lic_policy_name","lic_policy_ack_req"))
    return render(response, "main/reports_licensing.html", { "response_output" : json.loads(device_list) })

def oneview_export_xls(response):
    """
    Export iosxe_device table into XLSX
    """
    file = io.BytesIO() #create file in memory
    df_devices = pd.DataFrame.from_records(iosxe_device.objects.values()) # put database in pandas dataframe
    writer = pd.ExcelWriter(file, engine='xlsxwriter') # create Excel-file
    df_devices.to_excel(writer,sheet_name='Devices', index=False) # Put pandas dataframe into Excel-file
    writer.save()
    file.seek(0)
    return FileResponse(file,as_attachment=True,content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',filename='johann_devices.xlsx')

def tools_logs(response):
    """
    Show logs

    Simply return the logfile.
    """
    try:
        with open(f"{settings.MEDIA_ROOT}/debug.log", "r") as logfile:
            logs = logfile.read()
    except Exception:
        logs = "Error: can't fetch log file. Maybe nothing got logged yet?"
        logger.exception("Error: can't fetch log file.")

    return render(response, "main/tools_logs.html", { "logs" : logs })

def tools_raw_json(response):
    """
    Get show run command in JSON format.

    When form content is valid, start celery task and return celery task-id.
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
    Try enabling RESTCONF on device.

    When form content is valid, start celery task and return celery task-id.
    """
    if response.method == "POST":
        form = AddSingleDevice(response.POST)

        if form.is_valid():
            task = task_tools_enable_restconf.delay(form.cleaned_data["device_ip"],form.cleaned_data["device_username"],form.cleaned_data["device_password"])

        return render(response, "main/tools_enable_restconf.html", { "form" : form, "response_output" : task.id })
    else:
        form = AddSingleDevice()
    return render(response, "main/tools_enable_restconf.html", { "form" : form })
