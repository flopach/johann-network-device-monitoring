"""
                       CISCO SAMPLE CODE LICENSE
                              Version 1.1
            Copyright (c) 2021 Cisco and/or its affiliates
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