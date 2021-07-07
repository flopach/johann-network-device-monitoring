"""
                       CISCO SAMPLE CODE LICENSE
                              Version 1.1
            Copyright (c) 2021 Cisco and/or its affiliates
"""

import requests
import json
import logging
import datetime
from requests.models import stream_decode_response_unicode
import urllib3
from main.models import iosxe_device, iosxe_device_interfaces, iosxe_device_cred
import time

restconf_port = 443
restconf_base_url = "restconf/data"
timeout_connect = 5
timeout_read = 20
request_verify = False

logger = logging.getLogger("applogger")
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class new_iosxe_device:

    def __init__(self,device_ip,device_user,device_pw):
        self.device_ip = device_ip
        self.device_user = device_user
        self.device_pw = device_pw

    def _restconf_get_request(self, yang_loc, inner_function):
        """
        Request data via RESTCONF based on the YANG location
        Pass along an inner function which will be executed if the content was successfully received (200)
        Log if anything goes wrong.

        :self use: class variables for connection parameters
        :yang_loc: defined YANG location
        :inner_function: function which will be executed if 200

        :return success: status code , inner function response
        :return error: status code , error information
        """
        try:
            headers = { "Accept": "application/yang-data+json" }
            r_get = requests.request('GET',
                f"https://{self.device_ip}:{restconf_port}/{restconf_base_url}/{yang_loc}",
                headers=headers,
                auth=(self.device_user, self.device_pw),
                verify=request_verify,
                timeout=(timeout_connect,timeout_read))
            r_get.raise_for_status()

            if r_get.status_code == 200:
                logger.debug(self.device_ip+" | 200 Response: Successfully received data from {}".format(yang_loc))
                try:
                    i = inner_function(r_get.json()[yang_loc])
                    return 200, i
                except Exception as e:
                    logger.error(self.device_ip+" | Error! Received JSON, but there is something wrong. YANG: {} | Error: {}".format(yang_loc,e))
                    return 0, "Error! Received JSON, but there is something wrong."

            elif r_get.status_code == 204:
                logger.warning(self.device_ip+" | 204 Response: Received no content from {}".format(yang_loc))
                return 204, "No content."

        except requests.exceptions.HTTPError as errh:
            logger.exception(self.device_ip+" | HTTP Error: "+str(errh))
            err_code = int(r_get.status_code)
            if err_code == 401:
                return 401, "Unauthorized! Please check username or password!"
            elif err_code == 400:
                return 400, "Bad Request! Could connect to the device, but bad request. Is RESTCONF and secure webserver enabled?"
            elif err_code == 404:
                return 404, "Bad Request! Could connect to the device, but bad request. Is RESTCONF and secure webserver enabled?"
            else:
                return 0, "Error {}: Could not receive device data. Please check logs.".format(err_code)
        except requests.exceptions.ConnectionError as errc:
            logger.exception(self.device_ip+" | Connection Error: "+str(errc))
            return 0, "Can't connect to the device! Please check IP address and logs."
        except requests.exceptions.Timeout as errt:
            logger.exception(self.device_ip+" | Timeout Error: "+str(errt))
            return 0, "Can't connect to the device! Please check IP address and logs."
        except Exception as e:
            logger.exception(self.device_ip+" | Error: "+str(e))
            return 0, "Can't connect to the device! Please check IP address and logs."
        
    def _restconf_iosxe_native(self, r_content):
        """
        Get data from Cisco-IOS-XE-native:native
        Add to pre-defined Django database model, best effort

        :return success: added
        :return error: None
        """

        try:
            self.new_device.hostname = r_content["hostname"]
            self.new_device.ios_version_brief = r_content["version"]
        except:
            pass

        try:
            ios_users = []
            for user in r_content["username"]:
                try:
                    user_priv = user["privilege"]
                except:
                    user_priv = "1"
                ios_users.append("{} ({})".format(user["name"],user_priv))
            self.new_device.ios_users_list = ios_users
        except:
            pass

        try:
            self.new_device.domain_name = r_content["ip"]["domain"]["name"]
        except:
            pass

        try:
            ios_boot_files = []
            for filename in r_content["boot"]["system"]["bootfile"]["filename-list"]:
                ios_boot_files.append(filename["filename"])
            self.new_device.ios_boot_files_list = ios_boot_files
        except:
            pass
        
        try:
            self.new_device.default_gateway = r_content["ip"]["default-gateway"]
        except:
            pass

        try:
            self.new_device.name_server_list = r_content["ip"]["name-server"]["no-vrf"]
        except:
            pass

        try:
            ntp_server_list = []
            for ntp_server in r_content["ntp"]["Cisco-IOS-XE-ntp:server"]["server-list"]:
                ntp_server_list.append(ntp_server["ip-address"])
            self.new_device.ntp_server_list = ntp_server_list
        except:
            pass
        
        #SNMP server configs
        try:
            snmp_server_community_list = []
            for entry in r_content["snmp-server"]["Cisco-IOS-XE-snmp:community-config"]:
                snmp_server_community_list.append("{} ({})".format(entry["name"],entry["permission"]))
            self.new_device.snmp_server_community_list = snmp_server_community_list
        except:
            pass

        try:
            snmp_server_group_list = []
            for entry in r_content["snmp-server"]["Cisco-IOS-XE-snmp:group"]:
                snmp_server_group_list.append(entry["id"])
            self.new_device.snmp_server_group_list = snmp_server_group_list
        except:
            pass

        try:
            snmp_server_user_list = []
            for entry in r_content["snmp-server"]["Cisco-IOS-XE-snmp:user"]["names"]:
                snmp_server_user_list.append("{} ({})".format(entry["username"],entry["grpname"]))
            self.new_device.snmp_server_user_list = snmp_server_user_list
        except:
            pass

        try:
            self.new_device.spanning_tree_mode = r_content["spanning-tree"]["Cisco-IOS-XE-spanning-tree:mode"]
        except:
            pass

        try:
            if "iox" in r_content:
                self.new_device.iox = True
            else:
                self.new_device.iox = False
        except:
            pass

        return "added"

    def _restconf_iosxe_platform_software_oper(self, r_content):
        """
        Get data from Cisco-IOS-XE-platform-software-oper:cisco-platform-software
        Add to pre-defined Django database model, best effort

        :return success: added
        :return error: None
        """

        # memory information - getting data only from first control process in the list 
        try:
            self.new_device.memory_status = r_content["control-processes"]["control-process"][0]["memory-stats"]["memory-status"]
            memory_mb = round(int(r_content["control-processes"]["control-process"][0]["memory-stats"]["total"]) / 1000)
            self.new_device.memory_total_mb = memory_mb
            self.new_device.memory_used_percentage = r_content["control-processes"]["control-process"][0]["memory-stats"]["used-percent"]
            self.new_device.memory_available_percentage = r_content["control-processes"]["control-process"][0]["memory-stats"]["free-percent"]
        except:
            pass

        # CPU utilization
        # Get utilization from each core and get average in percentage
        try:
            cpu_user = 0.00
            cpu_system = 0.00
            cpu_idle = 0.00
            cores = 0
            for core in r_content["control-processes"]["control-process"][0]["per-core-stats"]["per-core-stat"]:
                cores += 100
                cpu_user += float(core["user"])
                cpu_system += float(core["system"])
                cpu_idle += float(core["idle"])

            self.new_device.cpu_totalavg_user_percentage = round( cpu_user / cores * 100 , 2)
            self.new_device.cpu_totalavg_system_percentage = round( cpu_system / cores * 100 , 2)
            self.new_device.cpu_totalavg_idle_percentage = round( cpu_idle / cores * 100 , 2)
        except:
            pass

        # partitions and filesystems
        try:
            partitions = []
            for p in r_content["q-filesystem"][0]["partitions"]:
                p_total_mb = round(int(p["total-size"]) / 1000)
                p_used_mb = round(int(p["used-size"]) / 1000)
                p_free_mb = p_total_mb - p_used_mb
                p_free_percent = 100 - int(p["used-percent"])
                partitions.append({ "p_name" : p["name"], "p_status": p["disk-status"], "p_total_mb" : p_total_mb, "p_used_mb": p_used_mb, "p_free_mb": p_free_mb, "p_used_percent" : p["used-percent"], "p_free_percent" : p_free_percent })
            self.new_device.partitions_list = partitions
        except:
            pass

        # get images from first filesystem only
        try:
            image_files = []
            for i in r_content["q-filesystem"][0]["image-files"]:
                image_files.append(i["full-path"])
            self.new_device.images_files_list = image_files
        except:
            pass

        return "added"

    def _restconf_iosxe_device_hardware_oper(self, r_content):
        """
        Get data from Cisco-IOS-XE-device-hardware-oper:device-hardware-data
        Add to pre-defined Django database model, best effort

        :return success: added
        :return error: None
        """

        # system time & boot time
        try:
            # different ms/s format for some devices
            try:
                device_current_time = datetime.datetime.strptime(r_content["device-hardware"]["device-system-data"]["current-time"], '%Y-%m-%dT%H:%M:%S.%f+00:00')
                device_current_time = device_current_time.replace(microsecond=0) # remove microseconds
            except:
                device_current_time = datetime.datetime.strptime(r_content["device-hardware"]["device-system-data"]["current-time"], '%Y-%m-%dT%H:%M:%S+00:00')
            device_boot_time = datetime.datetime.strptime(r_content["device-hardware"]["device-system-data"]["boot-time"], '%Y-%m-%dT%H:%M:%S+00:00')
            device_uptime = device_current_time - device_boot_time

            self.new_device.current_time = device_current_time.strftime("%d.%m.%Y %H:%M:%S")
            self.new_device.uptime = str(device_uptime)

            self.new_device.rommon_version = r_content["device-hardware"]["device-system-data"]["rommon-version"]
            self.new_device.last_reboot_reason = r_content["device-hardware"]["device-system-data"]["last-reboot-reason"]
        
            # get only the first line
            sw_version = r_content["device-hardware"]["device-system-data"]["software-version"].split("\n", 1)
            self.new_device.ios_version_long = sw_version[0]
        except:
            pass

        # get only the chassis information and iterative through the list, break early
        try:
            for hw in r_content["device-hardware"]["device-inventory"]:
                if hw["hw-type"] == "hw-type-chassis":
                    self.new_device.part_number = hw["part-number"]
                    self.new_device.serial_number = hw["serial-number"]
                    break
        except:
            pass

        return "added"

    def _restconf_iosxe_platform_oper(self, r_content):
        """
        Get data from Cisco-IOS-XE-platform-oper:components
        Add to pre-defined Django database model, best effort

        :return success: added
        :return error: None
        """

        # add this information if not yet defined
        if self.new_device.part_number == "":
            try:
                # get only the chassis information and iterative through the list, break early
                for component in r_content["component"]:
                    if component["state"]["type"] == "comp-chassis":
                        self.new_device.part_number = component["state"]["part-no"]
                        self.new_device.serial_number = component["state"]["serial-no"]
                        break
            except:
                pass

        return "added"

    def _restconf_iosxe_arp_oper(self, r_content):
        """
        Get data from Cisco-IOS-XE-arp-oper:arp-data
        Add to pre-defined Django database model, best effort

        :return success: added
        :return error: None
        """
            
        try:
            arp_data = []
            for vrf in r_content["arp-vrf"]:

                try:
                    for arp_oper in vrf["arp-oper"]:
                        arp_data.append(f'{arp_oper["hardware"]} (IP: {arp_oper["address"]}, Interface: {arp_oper["interface"]}, Vrf: {vrf["vrf"]})')
                except:
                    logger.info(self.device_ip+" | Could not insert all ARP data")

            self.new_device.arp_data_list = arp_data
            return "added"

        except:
            pass

    def _restconf_iosxe_cdp_oper(self, r_content):
        """
        Get data from Cisco-IOS-XE-cdp-oper:cdp-neighbor-details
        Add to pre-defined Django database model, best effort

        :return success: added
        :return error: None
        """

        try:
            cdp_neighbors = []
            for cdp_n in r_content["cdp-neighbor-detail"]:
                cdp_neighbors.append(f'{cdp_n["ip-address"]} (platform: {cdp_n["platform-name"]}, Local Interface: {cdp_n["local-intf-name"]})')
            
            self.new_device.cdp_neighbors_list = cdp_neighbors
            return "added"
        except:
            pass      

    def _restconf_iosxe_interfaces_oper(self, r_content):
        """
        Get data from Cisco-IOS-XE-interfaces-oper:interfaces
        In this case, data is saved to current class

        :return success: added
        :return error: None
        """

        try:
            # put all interface information in a list
            interfaces = []
            for interface in r_content["interface"]:

                try:

                    append_interface = {}
                    append_interface["name"] = interface["name"]
                    append_interface["description"] = interface["description"]

                    # convert admin status to read-friendly
                    if interface["admin-status"] == "if-state-up":
                        admin_status = "UP"
                    elif interface["admin-status"] == "if-state-down":
                        admin_status = "DOWN"
                    elif interface["admin-status"] == "if-state-test":
                        admin_status = "TEST"
                    else:
                        admin_status = "unknown"
                    append_interface["admin-status"] = admin_status

                    # convert oper status to read-friendly
                    if interface["oper-status"] == "if-oper-state-ready":
                        oper_status = "UP and CONNECTED"
                    elif interface["oper-status"] == "if-oper-state-no-pass":
                        oper_status = "administratively DOWN"
                    elif interface["oper-status"] == "if-oper-state-test":
                        oper_status = "test"
                    elif interface["oper-status"] == "if-oper-state-lower-layer-down":
                        oper_status = "DOWN, ready to connect"
                    elif interface["oper-status"] == "if-oper-state-invalid":
                        oper_status = "invalid"
                    elif interface["oper-status"] == "if-oper-state-dormant":
                        oper_status = "dormant"
                    elif interface["oper-status"] == "if-oper-state-not-present":
                        oper_status = "not present"
                    else:
                        oper_status = "unknown"
                    append_interface["oper-status"] = oper_status

                    last_change = datetime.datetime.strptime(interface["last-change"], '%Y-%m-%dT%H:%M:%S.%f+00:00')
                    append_interface["last-change"] = last_change.strftime("%d.%m.%Y %H:%M:%S")

                    append_interface["phys-address"] = interface["phys-address"]

                    if "ether-state" in interface:
                        append_interface["negotiated-duplex-mode"] = interface["ether-state"]["negotiated-duplex-mode"]
                        append_interface["negotiated-port-speed"] = interface["ether-state"]["negotiated-port-speed"]
                    
                    if "ipv4" in interface:
                        append_interface["ipv4"] = f'{interface["ipv4"]} ({interface["ipv4-subnet-mask"]})'

                    interfaces.append(append_interface)

                except:
                    pass
            
            #save temporarily to new_iosxe_device class
            self.interfaces = interfaces
            return "added"

        except:
            pass

    def _restconf_cisco_smart_license(self, r_content):
        """
        Get data from cisco-smart-license:licensing
        Add to pre-defined Django database model, best effort

        :return success: added
        :return error: None
        """

        # if transport-type is not set, exception will call no config set
        try:
            if r_content["config"]["transport"]["transport-type"] == "transport-type-off":
                transport_type = "disabled"
            elif r_content["config"]["transport"]["transport-type"] == "transport-type-smart":
                transport_type = "smart"
            elif r_content["config"]["transport"]["transport-type"] == "transport-type-callhome":
                transport_type = "callhome"
            elif r_content["config"]["transport"]["transport-type"] == "transport-type-cslu":
                transport_type = "CSLU URL"
            elif r_content["config"]["transport"]["transport-type"] == "transport-type-automatic":
                transport_type = "automatic"
        except:
            transport_type = "No config set"
        finally:
            self.new_device.lic_config_transport_type = transport_type

        try:
            self.new_device.lic_config_cslu_url = r_content["config"]["transport"]["transport-cslu"]["url-cslu"]
        except:
            pass

        try:
            udi_pid = r_content["state"]["state-info"]["udi"]["pid"]
            udi_sn = r_content["state"]["state-info"]["udi"]["sn"]
            self.new_device.lic_udi = "PID:{},SN:{}".format(udi_pid,udi_sn)
        except:
            pass

        try:
            used_licenses = []
            for license in r_content["state"]["state-info"]["usage"]:
                used_licenses.append("{} (name: {}, count: {})".format(license["license-name"],license["short-name"],license["count"]))
            self.new_device.lic_used_licenses_list = used_licenses
        except:
            pass

        try:
            rum_ack_last = datetime.datetime.strptime(r_content["state"]["state-info"]["rum-ack"]["last-received-time"], '%Y-%m-%dT%H:%M:%S+00:00')
            rum_ack_next = datetime.datetime.strptime(r_content["state"]["state-info"]["rum-ack"]["next-report-deadline"], '%Y-%m-%dT%H:%M:%S+00:00')
            self.new_device.lic_rum_ack_last = rum_ack_last.strftime("%d.%m.%Y %H:%M:%S")
            self.new_device.lic_rum_ack_next = rum_ack_next.strftime("%d.%m.%Y %H:%M:%S")
        except:
            pass

        try:
            self.new_device.lic_policy_name = r_content["state"]["state-info"]["policy"]["policy-name"]
            self.new_device.lic_policy_ack_req = r_content["state"]["state-info"]["policy"]["ack-required"]
        except:
            pass

        return "added"

    @staticmethod
    def _convert_to_nice_json(r_content):
        """
        Convert received content to nice JSON 
        """
        return json.dumps(r_content, indent=4)

    def _collect_restconf_data(self):
        """
        Run all RESTCONF calls to collect data from device

        :return success: status code , "collected"
        :return error: status code , error information
        """
        
        try:
            # if string "added" is not received, something must be wrong. Return error from request function.
            r_status, r_content = self._restconf_get_request("Cisco-IOS-XE-native:native",self._restconf_iosxe_native)
            if r_content != "added":
                return r_status, r_content

            # for now, no further error handling here for the others
            self._restconf_get_request("Cisco-IOS-XE-platform-software-oper:cisco-platform-software",self._restconf_iosxe_platform_software_oper)
            self._restconf_get_request("Cisco-IOS-XE-device-hardware-oper:device-hardware-data",self._restconf_iosxe_device_hardware_oper)
            self._restconf_get_request("Cisco-IOS-XE-platform-oper:components",self._restconf_iosxe_platform_oper)
            self._restconf_get_request("Cisco-IOS-XE-arp-oper:arp-data",self._restconf_iosxe_arp_oper)
            self._restconf_get_request("Cisco-IOS-XE-cdp-oper:cdp-neighbor-details",self._restconf_iosxe_cdp_oper)
            self._restconf_get_request("Cisco-IOS-XE-interfaces-oper:interfaces",self._restconf_iosxe_interfaces_oper)
            self._restconf_get_request("cisco-smart-license:licensing",self._restconf_cisco_smart_license)

            return r_status, "collected"

        except Exception as e:
            logger.exception(self.device_ip+" | Error when collecting data from the device: {}".format(e))
            return 0, "Error! Can't collect data from the device. Please check logs."

    def _write_to_database(self,write_mode="update"):
        """
        Write all gathered data to Django database model iosxe_device + iosxe_device_cred
        Get the gathered interface data (list) from the current class and save each interface as a new row in iosxe_device_interfaces

        Parameter used if updating the database entry
        :param: write_mode = update

        :return success: status code , success information
        :return error: status code , error information
        """
        try:
            # Save SQLite table iosxe_device 
            self.new_device.ip = self.device_ip
            self.new_device.last_update = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            self.new_device.save()

            # if the data will be refreshed, delete the interfaces and credentials at first to make the update easier
            if write_mode == "update":
                iosxe_device_cred.objects.filter(iosxe_device=self.new_device).delete()
                iosxe_device_interfaces.objects.filter(iosxe_device=self.new_device).delete()

            # Save SQLite table iosxe_device_cred
            # will be encrpyted soon
            self.new_device_cred = iosxe_device_cred()
            self.new_device_cred.iosxe_device = self.new_device
            self.new_device_cred.device_user = self.device_user
            self.new_device_cred.device_pw = self.device_pw
            self.new_device_cred.save()

            # Save SQLite table iosxe_device_interfaces
            # create for each interface a new entry in the interfaces table

            for interface in self.interfaces:
                # create for each interface a new entry in the database
                self.new_device_interface = iosxe_device_interfaces()
                # foreign key link
                self.new_device_interface.iosxe_device = self.new_device

                self.new_device_interface.name = interface["name"]
                self.new_device_interface.description = interface["description"]
                self.new_device_interface.admin_status = interface["admin-status"]
                self.new_device_interface.oper_status = interface["oper-status"]
                self.new_device_interface.last_change = interface["last-change"]
                self.new_device_interface.phys_address = interface["phys-address"]

                if "negotiated-duplex-mode" in interface:
                    self.new_device_interface.duplex_mode = interface["negotiated-duplex-mode"]
                
                if "negotiated-port-speed" in interface:
                    self.new_device_interface.port_speed = interface["negotiated-port-speed"]

                if "ipv4" in interface:
                    self.new_device_interface.ipv4 = interface["ipv4"]
                
                # save interface to database
                self.new_device_interface.save()
            
            logger.info("{} | Successfully inserted into database.".format(self.device_ip))
            return 200,f"Successfully inserted {self.device_ip} into database."
        
        except Exception as e:
            logger.exception("{} | Error when saving to database: {}".format(self.device_ip,e))
            return 0,"Error! Can't insert into database. Please check logs."

    def get_running_config_json(self):
        """
        Return running configuration in JSON
        """
        r_status, r_content = self._restconf_get_request("Cisco-IOS-XE-native:native",self._convert_to_nice_json)
        return r_status, r_content

    def add_to_database(self):
        """
        Top level function to be executed for adding the device to the database

        :return success: status code , success information
        :return error: status code , error information
        """

        # create new instance of database model class 
        self.new_device = iosxe_device()

        # get data via RESTCONF and add to class instance object
        # if there was an error, return it immediately
        r_status, r_content = self._collect_restconf_data()

        if r_content != "collected":
            return r_status, r_content

        status,content = self._write_to_database()
        return status,content

    def refresh_to_database(self,pk):
        """
        Top level function to be executed for refreshing the data in the database

        :param: pk: primary key in the database to know where to refresh the information

        :return success: status code , success information
        :return error: status code , error information
        """

        # create new instance of database model class 
        self.new_device = iosxe_device(id=pk)

        # get data via RESTCONF and add to class instance object
        # if there was an error, return it immediately
        r_status, r_content = self._collect_restconf_data()

        if r_content != "collected":
            return r_status, r_content

        status,content = self._write_to_database("update") #update parameters in the database
        return status,content