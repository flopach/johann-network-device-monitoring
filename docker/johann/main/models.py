from django.db import models

# Create your models here.

class iosxe_device(models.Model):

    # provided by the user
    ip = models.CharField(max_length=50)
    last_update = models.CharField(max_length=30)

    # YANG model: Cisco-IOS-XE-native:native
    hostname = models.CharField(max_length=50)
    ios_version_brief = models.CharField(max_length=6)
    ios_users_list = models.JSONField(blank=True,null=True)
    domain_name = models.CharField(max_length=50,blank=True,null=True)
    ios_boot_files_list = models.JSONField(blank=True,null=True)

    default_gateway = models.GenericIPAddressField(blank=True,null=True)
    name_server_list = models.JSONField(blank=True,null=True)
    ntp_server_list = models.JSONField(blank=True,null=True)

    snmp_server_community_list = models.JSONField(blank=True,null=True)
    snmp_server_group_list = models.JSONField(blank=True,null=True)
    snmp_server_user_list = models.JSONField(blank=True,null=True)

    spanning_tree_mode = models.CharField(max_length=50,blank=True,null=True)

    iox = models.BooleanField(blank=True)

    # YANG model: Cisco-IOS-XE-platform-software-oper:cisco-platform-software
    memory_status = models.CharField(max_length=15,blank=True)
    memory_total_mb = models.IntegerField(blank=True,null=True)
    memory_used_percentage = models.IntegerField(blank=True,null=True)
    memory_available_percentage = models.IntegerField(blank=True,null=True)

    cpu_totalavg_user_percentage = models.FloatField(blank=True,null=True)
    cpu_totalavg_system_percentage = models.FloatField(blank=True,null=True)
    cpu_totalavg_idle_percentage = models.FloatField(blank=True,null=True)

    partitions_list = models.JSONField(blank=True,null=True)
    images_files_list = models.JSONField(blank=True,null=True)

    # YANG model: Cisco-IOS-XE-device-hardware-oper:device-hardware-data
    part_number = models.CharField(max_length=20,blank=True)
    serial_number = models.CharField(max_length=20,blank=True)
    current_time = models.CharField(max_length=30,blank=True)
    uptime = models.CharField(max_length=20,blank=True)
    rommon_version = models.CharField(max_length=20,blank=True)
    last_reboot_reason = models.CharField(max_length=20,blank=True)
    ios_version_long = models.CharField(max_length=200,blank=True)

    # YANG model: Cisco-IOS-XE-arp-oper:arp-data
    arp_data_list = models.JSONField(blank=True,null=True)

    # YANG model: Cisco-IOS-XE-cdp-oper:cdp-neighbor-details
    cdp_neighbors_list = models.JSONField(blank=True,null=True)

    # YANG model: cisco-smart-license:licensing
    lic_config_transport_type = models.CharField(max_length=20,blank=True)
    lic_config_cslu_url = models.CharField(max_length=50,blank=True)
    lic_udi = models.CharField(max_length=40,blank=True)
    lic_used_licenses_list = models.JSONField(blank=True,null=True)
    lic_rum_ack_last = models.CharField(max_length=30,blank=True)
    lic_rum_ack_next = models.CharField(max_length=30,blank=True)
    lic_policy_name = models.CharField(max_length=30,blank=True)
    lic_policy_ack_req = models.CharField(max_length=10,blank=True)

    # latest added devices on top of the table when viewing for the user
    class Meta:
        ordering = ['-id']

class iosxe_device_cred(models.Model):
    iosxe_device = models.ForeignKey(iosxe_device,on_delete=models.CASCADE)

    device_user = models.CharField(max_length=50)
    device_pw = models.CharField(max_length=50)


class iosxe_device_interfaces(models.Model):
    iosxe_device = models.ForeignKey(iosxe_device,on_delete=models.CASCADE)

    # YANG model: Cisco-IOS-XE-interfaces-oper:interfaces
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=100,blank=True)
    admin_status = models.CharField(max_length=20,null=True)
    oper_status = models.CharField(max_length=20,null=True)
    last_change = models.CharField(max_length=20,null=True)
    phys_address = models.CharField(max_length=30,blank=True)
    duplex_mode = models.CharField(max_length=20,blank=True)
    port_speed = models.CharField(max_length=20,blank=True)
    ipv4 = models.CharField(max_length=40,blank=True)


"""
maybe in the future

class iosxe_device_arp(models.Model):
    iosxe_device = models.ForeignKey(iosxe_device,on_delete=models.CASCADE)

    arp_ip = models.GenericIPAddressField()
    arp_mac = models.CharField(max_length=20)
    arp_int = models.CharField(max_length=30)
    arp_vrf = models.CharField(max_length=20)

    def __str__(self):
        return self.iosxe_device.ip
"""