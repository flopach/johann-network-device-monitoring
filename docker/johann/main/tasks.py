# CISCO SAMPLE CODE LICENSE
# Version 1.1
# Copyright (c) 2021 Cisco and/or its affiliates

# Celery tasks for johann

import logging
from csv import DictReader
from io import StringIO
from celery import shared_task
from .models import iosxe_device,iosxe_device_interfaces, iosxe_device_cred
from django.core.files.storage import default_storage
from .net_services.restconf_queries import new_iosxe_device
from .net_services.netmiko_queries import enable_restconf_iosxe

logger = logging.getLogger("applogger")

@shared_task(bind=True,track_started=True)
def task_add_devices_single(self,device_ip,device_username,device_password):
    self.update_state(state='Querying RESTCONF and adding <b>{}</b> to database.'.format(device_ip))
    new_device = new_iosxe_device(device_ip,device_username,device_password)
    r_status, r_content = new_device.add_to_database()
    self.update_state(state='COMPLETE')
    return r_status, r_content

@shared_task(bind=True,track_started=True)
def task_add_devices_multiple(self,csv_file_name):
    """
    Import more than one IOSXE device

    :return: String if operation was successful or not
    """
    try:
        self.update_state(state='Reading CSV file')

        if csv_file_name.lower().endswith((".csv")) != True:
            return 0,"Wrong Filetype! Please upload only CSV files."
        
        csv_reader = DictReader(default_storage.open(csv_file_name,mode="r")) #read to get total number of devices
        total_devices = len(list(csv_reader))

        csv_reader = DictReader(default_storage.open(csv_file_name,mode="r")) #read again to pointer 0        
        imported_devices = 0
        current_device = 1
        task_response = ""

        logger.info("CSV-File Import | Started for {}".format(csv_file_name))
        
        for device in csv_reader:
            self.update_state(state='Adding <b>{}</b> to database ({} out of {}).'.format(device["ip"],current_device,total_devices))
            new_device = new_iosxe_device(device["ip"],device["username"],device["password"])
            device_response = new_device.add_to_database()
            
            if device_response[0] == 200:
                imported_devices += 1
                task_response += "SUCCESS! {}: {}\n".format(device["ip"],device_response[1])
            else:
                task_response += "ERROR! {}: {}\n".format(device["ip"],device_response[1])

            current_device += 1
            
        logger.info("CSV-File Import | successfully imported {} device(s).".format(imported_devices))
        logger.info("CSV-File Import | Ended for {}".format(csv_file_name))

        self.update_state(state='COMPLETE')
        task_response += "\nImport Done: successfully imported {} device(s).\n".format(imported_devices)

        return 200,task_response

    except Exception as e:
        logger.exception("CSV-File Import | Error when inserting: {}".format(e))
        return 0,"Error when inserting. Please check log and your CSV format!"

    finally:
        default_storage.delete(csv_file_name) #delete the CSV file

@shared_task(bind=True,track_started=True)
def task_refresh_all(self):
    """
    Refresh all device data from the database

    :return: String if operation was successful or not
    """
    try:
        self.update_state(state='Reading CSV file')
        logger.info("Database Refresh | Started")

        all_devices = iosxe_device_cred.objects.all().values("iosxe_device__ip","device_user","device_pw","iosxe_device__id")
        current_device = 1
        updated_devices = 0
        total_devices = iosxe_device.objects.count()
        task_response = ""

        for device in all_devices:
            self.update_state(state='Updating <b>{}</b> ({} out of {}).'.format(device["iosxe_device__ip"],current_device,total_devices))
            update_device = new_iosxe_device(device["iosxe_device__ip"],device["device_user"],device["device_pw"])
            device_response = update_device.refresh_to_database(device["iosxe_device__id"])

            if device_response[0] == 200:
                updated_devices += 1
                task_response += "SUCCESS! {}: {}\n".format(device["iosxe_device__ip"],device_response[1])
            else:
                task_response += "ERROR! {}: {}\n".format(device["iosxe_device__ip"],device_response[1])

            current_device += 1
            
        logger.info("Database Refresh |  successfully refreshed {} device(s).".format(updated_devices))
        logger.info("Database Refresh | Ended")

        self.update_state(state='COMPLETE')
        task_response += "\nImport Done: successfully refreshed {} device(s).\n".format(updated_devices)

        return 200,task_response

    except Exception as e:
        logger.exception("Database Refresh | Error when refreshing: {}".format(e))
        return 0,"Error when refreshing. Please check the log!"

@shared_task(bind=True,track_started=True)
def task_tools_raw_json(self,device_ip,device_username,device_password):
    self.update_state(state='Getting configuration data')
    new_device = new_iosxe_device(device_ip,device_username,device_password)
    r_status, r_content = new_device.get_running_config_json()
    self.update_state(state='COMPLETE')
    return r_status, r_content

@shared_task(bind=True,track_started=True)
def task_tools_enable_restconf(self,device_ip,device_username,device_password):
    self.update_state(state='Trying to enable RESTCONF')
    r_content = enable_restconf_iosxe(device_ip,device_username,device_password)
    self.update_state(state='COMPLETE')
    return 200, r_content