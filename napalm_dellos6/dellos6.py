# -*- coding: utf-8 -*-
# Copyright 2016 Dravetech AB. All rights reserved.
#
# The contents of this file are licensed under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with the
# License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

"""
Napalm driver for DellOS6.

Read https://napalm.readthedocs.io for more information.
"""
from napalm_dellos6.dellos6_canonical_map import dellos6_interfaces

from napalm.base import NetworkDriver
from napalm.base.exceptions import (
    ConnectionException,
    SessionLockedException,
    MergeConfigException,
    ReplaceConfigException,
    CommandErrorException,
)
from napalm.base.helpers import (
    canonical_interface_name,
    textfsm_extractor,
    mac,
)

from netmiko import ConnectHandler, FileTransfer

import re

# Easier to store these as constants
HOUR_SECONDS = 3600
DAY_SECONDS = 24 * HOUR_SECONDS
WEEK_SECONDS = 7 * DAY_SECONDS
YEAR_SECONDS = 365 * DAY_SECONDS

class DellOS6Driver(NetworkDriver):
    """Napalm driver for DellOS6."""

    UNKNOWN = u"N/A"

    def __init__(self, hostname, username, password, timeout=60, optional_args=None):
        """Constructor."""
        if optional_args is None:
            optional_args = {}
        self.device = None
        self.hostname = hostname
        self.username = username
        self.password = password
        self.timeout = timeout

        self.transport = optional_args.get('transport', 'ssh')

        # Netmiko possible arguments
        netmiko_argument_map = {
            'port': None,
            'secret': '',
            'verbose': False,
            'keepalive': 30,
            'global_delay_factor': 3,
            'use_keys': False,
            'key_file': None,
            'ssh_strict': False,
            'system_host_keys': False,
            'alt_host_keys': False,
            'alt_key_file': '',
            'ssh_config_file': None,
            'allow_agent': False,
            'session_timeout': 90,
            'timeout': 120
        }

        # Build dict of any optional Netmiko args
        self.netmiko_optional_args = {}
        for key in netmiko_argument_map:
            try:
                value = optional_args.get(key)
                if value:
                    self.netmiko_optional_args[key] = value
            except KeyError:
                pass

        default_port = {
            'ssh': 22
        }
        self.port = optional_args.get('port', default_port[self.transport])

        self.device = None
        self.config_replace = False

        self.profile = ["dellos10"]

    def open(self):
        """Open a connection to the device."""
        device_type = 'dell_os6'
        self.device = ConnectHandler(device_type=device_type,
                                     host=self.hostname,
                                     username=self.username,
                                     password=self.password,
                                     **self.netmiko_optional_args)
        # ensure in enable mode
        self.device.enable()


    def close(self):
        """To close the connection."""
        self.device.disconnect()

    def _send_command(self, command):
        """Error handling for self.device.send.command()."""
        try:
            error_msg = "Error while executing the command : {} output :: {}"
            self.device.set_base_prompt()
            output = self.device.send_command(command)
            if "% Invalid" in output:
                raise CommandErrorException(error_msg.format(command, output))

            return output
        except (socket.error, EOFError) as exp:
            raise ConnectionClosedException(str(exp))

    @staticmethod
    def parse_uptime(uptime_str):
        """
        Extract the uptime string from the given Dell OS6 Device.
        Return the uptime in seconds as an integer
        """
        # Initialize to zero
        (days, hours, minutes, seconds) = (0, 0, 0, 0)

        uptime_str = uptime_str.strip()
        time_list = re.split(', |:', uptime_str)
        for element in time_list:
            if re.search("days", element):
                days = int(element.strip(' days'))
            elif re.search("h", element):
                hours = int(element.strip('h'))
            elif re.search("m", element):
                minutes = int(element.strip('m'))
            elif re.search("s", element):
                seconds = int(element.strip('s'))

        uptime_sec = (
            (days * DAY_SECONDS)
            + (hours * HOUR_SECONDS)
            + (minutes * 60)
            + seconds
        )
        return uptime_sec

    @staticmethod
    def parse_arp_age(arp_age_str):
        """
        Extract the ARP time string from the given Dell OS6 Device.
        Return the ARP time in seconds as an integer
        """
        # Initialize to zero
        (hours, minutes, seconds) = (0, 0, 0)

        arp_age_str = arp_age_str.strip()
        age_list = re.split(' ', arp_age_str)
        for element in age_list:
            if re.search("h", element):
                hours = int(element.strip('h'))
            elif re.search("m", element):
                minutes = int(element.strip('m'))
            elif re.search("s", element):
                seconds = int(element.strip('s'))

        arp_age_sec = (
            (hours * HOUR_SECONDS)
            + (minutes * 60)
            + seconds
        )
        return arp_age_sec

    def _get_interface_list(self):
        """
        Returns a list of all interfaces on the device
        """

        raw_show_int_status = self._send_command("show interfaces status")
        raw_show_ip_int = self._send_command("show ip interface")

        show_int_status = textfsm_extractor(
            self, "show_interfaces_status", raw_show_int_status
        )
        show_ip_int = textfsm_extractor(
            self, "show_ip_interface", raw_show_ip_int
        )

        interface_list = []
        for interface in show_int_status:
            interface_list.append(canonical_interface_name(interface['interface'], addl_name_map=dellos6_interfaces))
        for interface in show_ip_int:
            interface_list.append(canonical_interface_name(interface['interface'], addl_name_map=dellos6_interfaces))

        return interface_list

    def get_facts(self):
        """
        Returns a dictionary containing the following information:
         * uptime - Uptime of the device in seconds.
         * vendor - Manufacturer of the device.
         * model - Device model.
         * hostname - Hostname of the device
         * fqdn - Fqdn of the device
         * os_version - String with the OS version running on the device.
         * serial_number - Serial number of the device
         * interface_list - List of the interfaces of the device
        Example::
            {
            'uptime': 102383940,
            'vendor': u'Dell',
            'os_version': u'6.2.0.5',
            'serial_number': u'CN04G4FP2829859O0195A99',
            'model': u'N4032',
            'hostname': u'dellos6-switch',
            'fqdn': u'dellos6-switch',
            'interface_list': [u'Tengigabitethernet1/0/1', u'Tengigabitethernet1/0/1', u'out-of-band']
            }
        """
        # default values.
        vendor = u'Dell'
        uptime = -1
        model, serial_number, fqdn, os_version, hostname = (self.UNKNOWN,) * 5

        # obtain output from device
        raw_show_ver = self._send_command("show version")
        raw_show_sw = self._send_command("show switch")
        raw_show_sys = self._send_command("show system")
        raw_show_hosts = self._send_command("show hosts")

        show_ver = textfsm_extractor(
            self, "show_version", raw_show_ver
        )
        show_sw = textfsm_extractor(
            self, "show_switch", raw_show_sw
        )
        show_sys = textfsm_extractor(
            self, "show_system-basic", raw_show_sys
        )
        show_hosts = textfsm_extractor(
            self, "show_hosts", raw_show_hosts
        )

        interface_list = self._get_interface_list()

        uptime = self.parse_uptime(show_sys[0]['uptime'])
        os_version = ''
        for switch in show_sw:
            if switch['status_mgmt'] == 'Mgmt Sw':
                os_version = switch['version']
        serial_number = show_ver[0]['serial_num']
        model = show_ver[0]['model']
        hostname = show_sys[0]['sys_name']
        domain_name = show_hosts[0]['domain']

        if domain_name != "Unknown" and hostname != "Unknown":
            fqdn = "{}.{}".format(hostname, domain_name)

        return {
            "uptime": uptime,
            "vendor": vendor,
            "os_version": str(os_version),
            "serial_number": str(serial_number),
            "model": str(model),
            "hostname": str(hostname),
            "fqdn": fqdn,
            "interface_list": interface_list,
        }

    def get_interfaces(self):
        """
        Returns a dictionary of dictionaries. The keys for the first dictionary will be the \
        interfaces in the devices. The inner dictionary will containing the following data for \
        each interface:
         * is_up (True/False)
         * is_enabled (True/False)
         * description (string)
         * last_flapped (float in seconds) (NOT IMPLEMENTED)
         * speed (int in Mbit)
         * MTU (in Bytes)
         * mac_address (string)
        Example::
            {
            u'Management1':
                {
                'is_up': False,
                'is_enabled': False,
                'description': '',
                'last_flapped': -1.0,
                'speed': 1000,
                'mtu': 1500,
                'mac_address': 'FA:16:3E:57:33:61',
                },
            u'Ethernet1':
                {
                'is_up': True,
                'is_enabled': True,
                'description': 'foo',
                'last_flapped': 1429978575.1554043,
                'speed': 1000,
                'mtu': 1500,
                'mac_address': 'FA:16:3E:57:33:62',
                },
            u'Ethernet2':
                {
                'is_up': True,
                'is_enabled': True,
                'description': 'bla',
                'last_flapped': 1429978575.1555667,
                'speed': 1000,
                'mtu': 1500,
                'mac_address': 'FA:16:3E:57:33:63',
                },
            u'Ethernet3':
                {
                'is_up': False,
                'is_enabled': True,
                'description': 'bar',
                'last_flapped': -1.0,
                'speed': 1000,
                'mtu': 1500,
                'mac_address': 'FA:16:3E:57:33:64',
                }
            }
        """

        # default values.
        last_flapped = -1.0

        raw_show_int_status = self._send_command("show interfaces status")
        raw_show_ip_int = self._send_command("show ip interface")
        raw_show_switch_stack_ports = self._send_command("show switch stack-ports")
        raw_show_int_config = self._send_command("show interfaces configuration")
        raw_show_int = self._send_command("show interfaces")
        raw_show_int_desc = self._send_command("show interfaces description")

        show_int_status = textfsm_extractor(
            self, "show_interfaces_status", raw_show_int_status
        )
        show_ip_int = textfsm_extractor(
            self, "show_ip_interface", raw_show_ip_int
        )
        show_switch_stack_ports = textfsm_extractor(
            self, "show_switch_stack-ports", raw_show_switch_stack_ports
        )
        show_int_config = textfsm_extractor(
            self, "show_interfaces_configuration", raw_show_int_config
        )
        show_int = textfsm_extractor(
            self, "show_interfaces", raw_show_int
        )
        show_int_desc = textfsm_extractor(
            self, "show_interfaces_description", raw_show_int_desc
        )


        interface_dict = {}
        for interface in show_int_status:
            interface_name = canonical_interface_name(interface['interface'], addl_name_map=dellos6_interfaces)
            if re.search('down', interface['link_state'], re.IGNORECASE):
                is_up = False
            if re.search('up', interface['link_state'], re.IGNORECASE):
                is_up = True
            interface_dict[interface_name] = {
                "is_up": is_up,
            }
        for interface in show_ip_int:
            interface_name = canonical_interface_name(interface['interface'], addl_name_map=dellos6_interfaces)
            if re.search('down', interface['link_state'], re.IGNORECASE):
                is_up = False
            if re.search('up', interface['link_state'], re.IGNORECASE):
                is_up = True
            # SVIs cannot be administratively disabled
            is_enabled = True
            interface_dict[interface_name] = {
                "is_up": is_up,
                "is_enabled": is_enabled,
            }
        # Set some defaults
        for interface in interface_dict:
            interface_dict[interface]['description'] = ''
            interface_dict[interface]['last_flapped'] = last_flapped
            interface_dict[interface]['mtu'] = 1500
            interface_dict[interface]['mac_address'] = ''
        for interface in show_switch_stack_ports:
            interface_name = canonical_interface_name(interface['interface'], addl_name_map=dellos6_interfaces)
            if re.search('link down', interface['link_state'], re.IGNORECASE):
                is_up = False
            if re.search('link up', interface['link_state'], re.IGNORECASE):
                is_up = True
            if not interface['speed'].isdigit():
                speed = -1
            else:
                # Speed is reported in Gbps
                speed = int(interface['speed']) * 1000
            interface_dict[interface_name]['is_up'] = is_up
            interface_dict[interface_name]['speed'] = speed
        for interface in show_int_config:
            interface_name = canonical_interface_name(interface['interface'], addl_name_map=dellos6_interfaces)
            if interface_name in interface_dict:
                if re.search('down', interface['admin_state'], re.IGNORECASE):
                    is_enabled = False
                if re.search('up', interface['admin_state'], re.IGNORECASE):
                    is_enabled = True
                if not interface['speed'].isdigit():
                    speed = -1
                else:
                    speed = int(interface['speed'])
                if not interface['mtu'].isdigit():
                    mtu= -1
                else:
                    mtu = int(interface['mtu'])
                interface_dict[interface_name]['is_enabled'] = is_enabled
                interface_dict[interface_name]['mtu'] = mtu
        for interface in show_int_desc:
            interface_name = canonical_interface_name(interface['interface'], addl_name_map=dellos6_interfaces)
            if interface_name in interface_dict:
                interface_dict[interface_name]['description'] = interface['desc']
        for interface in show_int:
            interface_name = canonical_interface_name(interface['interface'], addl_name_map=dellos6_interfaces)
            interface_dict[interface_name]['mac_address'] = mac(interface['mac_address'])

        return interface_dict

    def get_lldp_neighbors(self):
        """
        Returns a dictionary where the keys are local ports and the value is a list of \
        dictionaries with the following information:
            * hostname
            * port
        Example::
            {
            u'Ethernet2':
                [
                    {
                    'hostname': u'junos-unittest',
                    'port': u'520',
                    }
                ],
            u'Ethernet3':
                [
                    {
                    'hostname': u'junos-unittest',
                    'port': u'522',
                    }
                ],
            u'Ethernet1':
                [
                    {
                    'hostname': u'junos-unittest',
                    'port': u'519',
                    },
                    {
                    'hostname': u'ios-xrv-unittest',
                    'port': u'Gi0/0/0/0',
                    }
                ],
            u'Management1':
                [
                    {
                    'hostname': u'junos-unittest',
                    'port': u'508',
                    }
                ]
            }
        """

        raw_show_lldp_remote_device_all = self._send_command("show lldp remote-device all")

        show_lldp_remote_device_all = textfsm_extractor(
            self, "show_lldp_remote-device_all", raw_show_lldp_remote_device_all
        )

        lldp = {}
        for lldp_entry in show_lldp_remote_device_all:
            lldp[lldp_entry['interface']] = []
            hostname = lldp_entry['host_name']
            if not hostname:
                hostname = lldp_entry['chassis_id']
            else:
                if hostname.rfind('...', (len(hostname) - 2), len(hostname)):
                    raw_show_lldp_remote_device_detail = self._send_command("show lldp remote-device detail " + lldp_entry['interface'])
                    show_lldp_remote_device_detail = textfsm_extractor(
                        self, "show_lldp_remote-device_detail", raw_show_lldp_remote_device_detail
                    )
                    hostname = show_lldp_remote_device_detail[0]['host_name']
            lldp_dict = {"port": lldp_entry['port_id'], 'hostname': hostname}
            lldp[lldp_entry['interface']].append(lldp_dict)

        return lldp

    def get_environment(self):
        """
        Returns a dictionary where:
            * fans is a dictionary of dictionaries where the key is the location and the values:
                 * status (True/False) - True if it's ok, false if it's broken
            * temperature is a dict of dictionaries where the key is the location and the values:
                 * temperature (float) - Temperature in celsius the sensor is reporting.
                 * is_alert (True/False) - True if the temperature is above the alert threshold
                 * is_critical (True/False) - True if the temp is above the critical threshold
            * power is a dictionary of dictionaries where the key is the PSU id and the values:
                 * status (True/False) - True if it's ok, false if it's broken
                 * capacity (float) - Capacity in W that the power supply can support
                 * output (float) - Watts drawn by the system
            * cpu is a dictionary of dictionaries where the key is the ID and the values
                 * %usage
            * memory is a dictionary with:
                 * available_ram (int) - Total amount of RAM installed in the device
                 * used_ram (int) - RAM in use in the device

            * cpu is using 1-minute average
            * cpu hard-coded to cpu0 (i.e. only a single CPU)
        """

        raw_show_sys = self._send_command("show system")
        raw_show_proc_cpu = self._send_command("show process cpu")

        show_sys_fans = textfsm_extractor(
            self, "show_system-fans", raw_show_sys
        )
        show_sys_temps = textfsm_extractor(
            self, "show_system-temps", raw_show_sys
        )
        show_sys_power = textfsm_extractor(
            self, "show_system-power_supplies", raw_show_sys
        )
        show_proc_cpu = textfsm_extractor(
            self, "show_process_cpu", raw_show_proc_cpu
        )

        environment = {}
        environment.setdefault("fans", {})
        environment.setdefault("temperature", {})
        environment.setdefault("power", {})
        environment.setdefault("cpu", {})
        environment.setdefault("memory", {})

        for fan in show_sys_fans:
            environment["fans"].setdefault("unit " + fan["unit"], {})
            environment["fans"]["unit " + fan["unit"]].setdefault(fan["description"], {})
            if fan["status"] == "OK":
                environment["fans"]["unit " + fan["unit"]][fan["description"]]["status"] = True
            else:
                environment["fans"]["unit " + fan["unit"]][fan["description"]]["status"] = False
        for temp in show_sys_temps:
            environment["temperature"].setdefault("unit " + temp["unit"], {})
            environment["temperature"]["unit " + temp["unit"]].setdefault(temp["description"], {})
            environment["temperature"]["unit " + temp["unit"]][temp["description"]] = {
                "temperature": float(temp["temp"]),
                "is_alert": False,
                "is_critical": False,
            }
        for power in show_sys_power:
            environment["power"].setdefault("unit " + power["unit"], {})
            environment["power"]["unit " + power["unit"]].setdefault(power["description"], {})
            environment["power"]["unit " + power["unit"]][power["description"]] = {
                "status": False,
                "capacity": -1.0,
                "output": float(power["pwr_cur"]),
            }
            if power["status"] == "OK":
                environment["power"]["unit " + power["unit"]][power["description"]]["status"] = True
        environment["cpu"][0] = {}
        environment["cpu"][0]["%usage"] = 0.0
        environment["cpu"][0]["%usage"] = show_proc_cpu[0]['cpu_60']
        environment["memory"] = {
            "available_ram": int(show_proc_cpu[0]['mem_free']) * 1024,
            "used_ram": int(show_proc_cpu[0]['mem_alloc']) * 1024,
        }

        return environment

    def get_interfaces_counters(self):
        """
        Returns a dictionary of dictionaries where the first key is an interface name and the
        inner dictionary contains the following keys:
            * tx_errors (int)
            * rx_errors (int)
            * tx_discards (int)
            * rx_discards (int)
            * tx_octets (int)
            * rx_octets (int)
            * tx_unicast_packets (int)
            * rx_unicast_packets (int)
            * tx_multicast_packets (int)
            * rx_multicast_packets (int)
            * tx_broadcast_packets (int)
            * rx_broadcast_packets (int)
        Example::
            {
                u'Ethernet2': {
                    'tx_multicast_packets': 699,
                    'tx_discards': 0,
                    'tx_octets': 88577,
                    'tx_errors': 0,
                    'rx_octets': 0,
                    'tx_unicast_packets': 0,
                    'rx_errors': 0,
                    'tx_broadcast_packets': 0,
                    'rx_multicast_packets': 0,
                    'rx_broadcast_packets': 0,
                    'rx_discards': 0,
                    'rx_unicast_packets': 0
                },
                u'Management1': {
                     'tx_multicast_packets': 0,
                     'tx_discards': 0,
                     'tx_octets': 159159,
                     'tx_errors': 0,
                     'rx_octets': 167644,
                     'tx_unicast_packets': 1241,
                     'rx_errors': 0,
                     'tx_broadcast_packets': 0,
                     'rx_multicast_packets': 0,
                     'rx_broadcast_packets': 80,
                     'rx_discards': 0,
                     'rx_unicast_packets': 0
                },
                u'Ethernet1': {
                     'tx_multicast_packets': 293,
                     'tx_discards': 0,
                     'tx_octets': 38639,
                     'tx_errors': 0,
                     'rx_octets': 0,
                     'tx_unicast_packets': 0,
                     'rx_errors': 0,
                     'tx_broadcast_packets': 0,
                     'rx_multicast_packets': 0,
                     'rx_broadcast_packets': 0,
                     'rx_discards': 0,
                     'rx_unicast_packets': 0
                }
            }
        """

        interface_list = self._get_interface_list()

        raw_show_int_count = self._send_command("show interfaces counters")
        raw_show_int_count_err = self._send_command("show interfaces counters errors")

        show_int_count = textfsm_extractor(
            self, "show_interfaces_counters", raw_show_int_count
        )
        show_int_count_err = textfsm_extractor(
            self, "show_interfaces_counters_errors", raw_show_int_count_err
        )

        int_counters = {}
        for int_list in interface_list:

            int_counters[int_list] = {
                'tx_errors': -1,
                'rx_errors': -1,
                'tx_discards': -1,
                'rx_discards': -1,
                'tx_octets': -1,
                'rx_octets': -1,
                'tx_unicast_packets': -1,
                'rx_unicast_packets': -1,
                'tx_multicast_packets': -1,
                'rx_multicast_packets': -1,
                'tx_broadcast_packets': -1,
                'rx_broadcast_packets': -1,
            }

            for int_count_err in show_int_count_err:
                interface_name = canonical_interface_name(int_count_err['interface'], addl_name_map=dellos6_interfaces)
                if interface_name == int_list:
                    if int_count_err['out_total'].isdigit() and int(int_count_err['out_total']) >= 0:
                        int_counters[int_list]['tx_errors'] = int(int_count_err['out_total'])
                    if int_count_err['in_total'].isdigit() and int(int_count_err['in_total']) >= 0:
                        int_counters[int_list]['rx_errors'] = int(int_count_err['in_total'])
                    if int_count_err['out_discard'].isdigit() and int(int_count_err['out_discard']) >= 0:
                        int_counters[int_list]['tx_discards'] = int(int_count_err['out_discard'])

            for int_count in show_int_count:
                interface_name = canonical_interface_name(int_count['interface'], addl_name_map=dellos6_interfaces)
                if interface_name == int_list:
                    if int_count['out_total_octs'].isdigit() and int(int_count['out_total_octs']) >= 0:
                        int_counters[int_list]['tx_octets'] = int(int_count['out_total_octs'])
                    if int_count['in_total_octs'].isdigit() and int(int_count['in_total_octs']) >= 0:
                        int_counters[int_list]['rx_octets'] = int(int_count['in_total_octs'])
                    if int_count['out_ucast_pkts'].isdigit() and int(int_count['out_ucast_pkts']) >= 0:
                        int_counters[int_list]['tx_unicast_packets'] = int(int_count['out_ucast_pkts'])
                    if int_count['in_ucast_pkts'].isdigit() and int(int_count['in_ucast_pkts']) >= 0:
                        int_counters[int_list]['rx_unicast_packets'] = int(int_count['in_ucast_pkts'])
                    if int_count['out_mcast_pkts'].isdigit() and int(int_count['out_mcast_pkts']) >= 0:
                        int_counters[int_list]['tx_multicast_packets'] = int(int_count['out_mcast_pkts'])
                    if int_count['in_mcast_pkts'].isdigit() and int(int_count['in_mcast_pkts']) >= 0:
                        int_counters[int_list]['rx_multicast_packets'] = int(int_count['in_mcast_pkts'])
                    if int_count['out_bcast_pkts'].isdigit() and int(int_count['out_bcast_pkts']) >= 0:
                        int_counters[int_list]['tx_broadcast_packets'] = int(int_count['out_bcast_pkts'])
                    if int_count['in_bcast_pkts'].isdigit() and int(int_count['in_bcast_pkts']) >= 0:
                        int_counters[int_list]['rx_broadcast_packets'] = int(int_count['in_bcast_pkts'])

        return int_counters


    def get_lldp_neighbors_detail(self, interface=""):
        """
        Returns a detailed view of the LLDP neighbors as a dictionary
        containing lists of dictionaries for each interface.
        Empty entries are returned as an empty string (e.g. '') or list where applicable.
        Inner dictionaries contain fields:
            * parent_interface (string)
            * remote_port (string)
            * remote_port_description (string)
            * remote_chassis_id (string)
            * remote_system_name (string)
            * remote_system_description (string)
            * remote_system_capab (list) with any of these values
                * other
                * repeater
                * bridge
                * wlan-access-point
                * router
                * telephone
                * docsis-cable-device
                * station
            * remote_system_enabled_capab (list)
        Example::
            {
                'TenGigE0/0/0/8': [
                    {
                        'parent_interface': u'Bundle-Ether8',
                        'remote_chassis_id': u'8c60.4f69.e96c',
                        'remote_system_name': u'switch',
                        'remote_port': u'Eth2/2/1',
                        'remote_port_description': u'Ethernet2/2/1',
                        'remote_system_description': u'''Cisco Nexus Operating System (NX-OS)
                              Software 7.1(0)N1(1a)
                              TAC support: http://www.cisco.com/tac
                              Copyright (c) 2002-2015, Cisco Systems, Inc. All rights reserved.''',
                        'remote_system_capab': ['bridge', 'repeater'],
                        'remote_system_enable_capab': ['bridge']
                    }
                ]
            }
        """
        raw_show_lldp_remote_device_all = self._send_command("show lldp remote-device all")

        show_lldp_remote_device_all = textfsm_extractor(
            self, "show_lldp_remote-device_all", raw_show_lldp_remote_device_all
        )

        lldp = {}
        for lldp_entry in show_lldp_remote_device_all:
            lldp[lldp_entry['interface']] = {}
            raw_show_lldp_remote_device_detail = self._send_command("show lldp remote-device detail " + lldp_entry['interface'])
            show_lldp_remote_device_detail = textfsm_extractor(
                self, "show_lldp_remote-device_detail", raw_show_lldp_remote_device_detail
            )
            print(raw_show_lldp_remote_device_detail)
            print(show_lldp_remote_device_detail)
            parent_interface = ''
            remote_chassis_id = lldp_entry['chassis_id']
            remote_system_name = show_lldp_remote_device_detail[0]['host_name']
            remote_port = show_lldp_remote_device_detail[0]['port_id']
            remote_port_description = show_lldp_remote_device_detail[0]['port_desc']
            remote_system_description = show_lldp_remote_device_detail[0]['sys_desc']
            if show_lldp_remote_device_detail[0]['sys_cap_sup']:
                remote_system_capab = show_lldp_remote_device_detail[0]['sys_cap_sup'].replace(" ", "").split(",")
            else:
                remote_system_capab = []
            if show_lldp_remote_device_detail[0]['sys_cap_oper']:
                remote_system_enable_capab = show_lldp_remote_device_detail[0]['sys_cap_oper'].replace(" ", "").split(",")
            else:
                remote_system_enable_capab = []

            lldp[lldp_entry['interface']] = {
                "parent_interface": parent_interface,
                "remote_chassis_id": remote_chassis_id,
                "remote_system_name": remote_system_name,
                "remote_port": remote_port,
                "remote_port_description": remote_port_description,
                "remote_system_description": remote_system_description,
                "remote_system_capab": remote_system_capab,
                "remote_system_enable_capab": remote_system_enable_capab,
            }

        return lldp

    def cli(self, commands):

        """
        Will execute a list of commands and return the output in a dictionary format.
        Example::
            {
                u'show version and haiku':  u'''Hostname: re0.edge01.arn01
                                                Model: mx480
                                                Junos: 13.3R6.5
                                                        Help me, Obi-Wan
                                                        I just saw Episode Two
                                                        You're my only hope
                                            ''',
                u'show chassis fan'     :   u'''
                    Item               Status  RPM     Measurement
                    Top Rear Fan       OK      3840    Spinning at intermediate-speed
                    Bottom Rear Fan    OK      3840    Spinning at intermediate-speed
                    Top Middle Fan     OK      3900    Spinning at intermediate-speed
                    Bottom Middle Fan  OK      3840    Spinning at intermediate-speed
                    Top Front Fan      OK      3810    Spinning at intermediate-speed
                    Bottom Front Fan   OK      3840    Spinning at intermediate-speed'''
            }
        """

        cli_output = dict()
        if type(commands) is not list:
            raise TypeError("Please enter a valid list of commands!")

        for command in commands:
            output = self._send_command(command)
            cli_output.setdefault(command, {})
            cli_output[command] = output

        return cli_output

    def get_arp_table(self, vrf=""):

        """
        Returns a list of dictionaries having the following set of keys:
            * interface (string)
            * mac (string)
            * ip (string)
            * age (float)
        'vrf' of null-string will default to all VRFs. Specific 'vrf' will return the ARP table
        entries for that VRFs (including potentially 'default' or 'global').
        In all cases the same data structure is returned and no reference to the VRF that was used
        is included in the output.
        Example::
            [
                {
                    'interface' : 'MgmtEth0/RSP0/CPU0/0',
                    'mac'       : '5C:5E:AB:DA:3C:F0',
                    'ip'        : '172.17.17.1',
                    'age'       : 1454496274.84
                },
                {
                    'interface' : 'MgmtEth0/RSP0/CPU0/0',
                    'mac'       : '5C:5E:AB:DA:3C:FF',
                    'ip'        : '172.17.17.2',
                    'age'       : 1435641582.49
                }
            ]
        """
        if vrf:
            command = "show arp vrf {}".format(vrf)
        else:
            command = "show arp"

        raw_show_arp = self._send_command(command)

        show_arp = textfsm_extractor(
            self, "show_arp", raw_show_arp
        )

        arp_table = []
        for entry in show_arp:
            arp_table.append(
                {
                    'interface': canonical_interface_name(entry['interface'], addl_name_map=dellos6_interfaces),
                    'mac': mac(entry['mac_address']),
                    'ip': entry['ip_address'],
                    'age': float(self.parse_arp_age(entry['age'])),
                }
            )

        return arp_table
