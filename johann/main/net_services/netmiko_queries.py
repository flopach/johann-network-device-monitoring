"""
Copyright 2022 Cisco Systems

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from netmiko import ConnectHandler
import logging

logger = logging.getLogger("applogger")

def enable_restconf_iosxe(device_ip,device_user,device_pw):
    """
    Try to enably RESTCONF with netmiko library

    :return: Output or Error Message (str)
    """
    try:

        device_credentials = {
            'device_type': 'cisco_ios',
            'host':   device_ip,
            'username': device_user,
            'password': device_pw,
        }

        iosxe_device = ConnectHandler(**device_credentials)

        config_commands = [ 'ip http secure-server',
                            'restconf']

        output = iosxe_device.send_config_set(config_commands)

        return output
    
    except Exception as e:
        logger.exception("Error when trying to enable RESTCONF on {}: {}".format(device_ip,e))
        return "Error when trying to enable RESTCONF. Please check logs."