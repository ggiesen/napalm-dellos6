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
import re
import socket
from ipaddress import IPv4Interface, IPv6Interface
from statistics import stdev

import napalm.base.constants as C
from napalm.base import NetworkDriver
from napalm.base.exceptions import CommandErrorException, ConnectionClosedException
from napalm.base.helpers import (
    canonical_interface_name,
    mac,
    sanitize_configs,
    textfsm_extractor,
)

import napalm_dellos6.dellos6_constants as D6C
from napalm_dellos6.dellos6_canonical_map import dellos6_interfaces

from netmiko import ConnectHandler

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

        self.transport = optional_args.get("transport", "ssh")

        # Netmiko possible arguments
        netmiko_argument_map = {
            "port": None,
            "secret": "",
            "verbose": False,
            "keepalive": 30,
            "global_delay_factor": 3,
            "use_keys": False,
            "key_file": None,
            "ssh_strict": False,
            "system_host_keys": False,
            "alt_host_keys": False,
            "alt_key_file": "",
            "ssh_config_file": None,
            "allow_agent": False,
            "session_timeout": 90,
            "timeout": 120,
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

        default_port = {"ssh": 22}
        self.port = optional_args.get("port", default_port[self.transport])

        self.device = None
        self.config_replace = False

        self.profile = ["dellos6"]

    def open(self):
        """Open a connection to the device."""
        device_type = "dell_os6"
        self.device = ConnectHandler(
            device_type=device_type,
            host=self.hostname,
            username=self.username,
            password=self.password,
            **self.netmiko_optional_args
        )
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
        time_list = re.split(", |:", uptime_str)
        for element in time_list:
            if re.search("days", element):
                days = int(element.strip(" days"))
            elif re.search("h", element):
                hours = int(element.strip("h"))
            elif re.search("m", element):
                minutes = int(element.strip("m"))
            elif re.search("s", element):
                seconds = int(element.strip("s"))

        uptime_sec = (
            (days * DAY_SECONDS) + (hours * HOUR_SECONDS) + (minutes * 60) + seconds
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
        age_list = re.split(" ", arp_age_str)
        for element in age_list:
            if re.search("h", element):
                hours = int(element.strip("h"))
            elif re.search("m", element):
                minutes = int(element.strip("m"))
            elif re.search("s", element):
                seconds = int(element.strip("s"))

        arp_age_sec = (hours * HOUR_SECONDS) + (minutes * 60) + seconds
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
        show_ip_int = textfsm_extractor(self, "show_ip_interface", raw_show_ip_int)

        interface_list = []
        for interface in show_int_status:
            interface_list.append(
                canonical_interface_name(
                    interface["interface"], addl_name_map=dellos6_interfaces
                )
            )
        for interface in show_ip_int:
            interface_list.append(
                canonical_interface_name(
                    interface["interface"], addl_name_map=dellos6_interfaces
                )
            )

        return interface_list

    def _get_interface_dict(self):
        """
        Returns a dict of all interfaces on the device
        """

        raw_show_int_status = self._send_command("show interfaces status")
        raw_show_ip_int = self._send_command("show ip interface")

        show_int_status = textfsm_extractor(
            self, "show_interfaces_status", raw_show_int_status
        )
        show_ip_int = textfsm_extractor(self, "show_ip_interface", raw_show_ip_int)

        interface_dict = {}
        for interface in show_int_status:
            interface_name = canonical_interface_name(
                interface["interface"], addl_name_map=dellos6_interfaces
            )
            interface_dict[interface_name] = {}
        for interface in show_ip_int:
            interface_name = canonical_interface_name(
                interface["interface"], addl_name_map=dellos6_interfaces
            )
            interface_dict[interface_name] = {}

        return interface_dict

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
            'interface_list': [u'Tengigabitethernet1/0/1', u'out-of-band']
            }
        """
        # default values.
        vendor = u"Dell"
        uptime = -1
        model, serial_number, fqdn, os_version, hostname = (self.UNKNOWN,) * 5

        # obtain output from device
        raw_show_ver = self._send_command("show version")
        raw_show_sw = self._send_command("show switch")
        raw_show_sys = self._send_command("show system")
        raw_show_hosts = self._send_command("show hosts")

        show_ver = textfsm_extractor(self, "show_version", raw_show_ver)
        show_sw = textfsm_extractor(self, "show_switch", raw_show_sw)
        show_sys = textfsm_extractor(self, "show_system-basic", raw_show_sys)
        show_hosts = textfsm_extractor(self, "show_hosts", raw_show_hosts)

        interface_list = self._get_interface_list()

        uptime = self.parse_uptime(show_sys[0]["uptime"])
        os_version = ""
        for switch in show_sw:
            if switch["status_mgmt"] == "Mgmt Sw":
                os_version = switch["version"]
        serial_number = show_ver[0]["serial_num"]
        model = show_ver[0]["model"]
        hostname = show_sys[0]["sys_name"]
        domain_name = show_hosts[0]["domain"]

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
        show_ip_int = textfsm_extractor(self, "show_ip_interface", raw_show_ip_int)
        show_switch_stack_ports = textfsm_extractor(
            self, "show_switch_stack-ports", raw_show_switch_stack_ports
        )
        show_int_config = textfsm_extractor(
            self, "show_interfaces_configuration", raw_show_int_config
        )
        show_int = textfsm_extractor(self, "show_interfaces", raw_show_int)
        show_int_desc = textfsm_extractor(
            self, "show_interfaces_description", raw_show_int_desc
        )

        interface_dict = {}
        for interface in show_int_status:
            interface_name = canonical_interface_name(
                interface["interface"], addl_name_map=dellos6_interfaces
            )
            if re.search("down", interface["link_state"], re.IGNORECASE):
                is_up = False
            if re.search("up", interface["link_state"], re.IGNORECASE):
                is_up = True
            interface_dict[interface_name] = {"is_up": is_up}
        for interface in show_ip_int:
            interface_name = canonical_interface_name(
                interface["interface"], addl_name_map=dellos6_interfaces
            )
            if re.search("down", interface["link_state"], re.IGNORECASE):
                is_up = False
            if re.search("up", interface["link_state"], re.IGNORECASE):
                is_up = True
            # SVIs cannot be administratively disabled
            is_enabled = True
            interface_dict[interface_name] = {"is_up": is_up, "is_enabled": is_enabled}
        # Set some defaults
        for interface in interface_dict:
            interface_dict[interface]["description"] = ""
            interface_dict[interface]["last_flapped"] = last_flapped
            interface_dict[interface]["mtu"] = 1500
            interface_dict[interface]["mac_address"] = ""
            interface_dict[interface]["speed"] = -1
        for interface in show_switch_stack_ports:
            interface_name = canonical_interface_name(
                interface["interface"], addl_name_map=dellos6_interfaces
            )
            if re.search("link down", interface["link_state"], re.IGNORECASE):
                is_up = False
            if re.search("link up", interface["link_state"], re.IGNORECASE):
                is_up = True
            speed = -1
            if interface["speed"].isdigit():
                # Speed is reported in Gbps
                speed = int(interface["speed"]) * 1000
            interface_dict[interface_name]["is_up"] = is_up
            interface_dict[interface_name]["speed"] = speed
        for interface in show_int_config:
            interface_name = canonical_interface_name(
                interface["interface"], addl_name_map=dellos6_interfaces
            )
            if interface_name in interface_dict:
                if re.search("down", interface["admin_state"], re.IGNORECASE):
                    is_enabled = False
                if re.search("up", interface["admin_state"], re.IGNORECASE):
                    is_enabled = True
                if interface["speed"].isdigit():
                    interface_dict[interface_name]["speed"] = int(interface["speed"])
                if not interface["mtu"].isdigit():
                    mtu = -1
                else:
                    mtu = int(interface["mtu"])
                interface_dict[interface_name]["is_enabled"] = is_enabled
                interface_dict[interface_name]["mtu"] = mtu
        for interface in show_int_desc:
            interface_name = canonical_interface_name(
                interface["interface"], addl_name_map=dellos6_interfaces
            )
            if interface_name in interface_dict:
                interface_dict[interface_name]["description"] = interface["desc"]
        for interface in show_int:
            interface_name = canonical_interface_name(
                interface["interface"], addl_name_map=dellos6_interfaces
            )
            interface_dict[interface_name]["mac_address"] = mac(
                interface["mac_address"]
            )

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

        raw_show_lldp_remote_device_all = self._send_command(
            "show lldp remote-device all"
        )

        show_lldp_remote_device_all = textfsm_extractor(
            self, "show_lldp_remote-device_all", raw_show_lldp_remote_device_all
        )

        lldp = {}
        for lldp_entry in show_lldp_remote_device_all:
            interface = canonical_interface_name(
                lldp_entry["interface"], addl_name_map=dellos6_interfaces
            )
            lldp[interface] = []
            hostname = lldp_entry["host_name"]
            if not hostname:
                hostname = lldp_entry["chassis_id"]
            else:
                if hostname.rfind("...", (len(hostname) - 2), len(hostname)):
                    raw_show_lldp_remote_device_detail = self._send_command(
                        "show lldp remote-device detail " + lldp_entry["interface"]
                    )
                    show_lldp_remote_device_detail = textfsm_extractor(
                        self,
                        "show_lldp_remote-device_detail",
                        raw_show_lldp_remote_device_detail,
                    )
                    hostname = show_lldp_remote_device_detail[0]["host_name"]
            lldp_dict = {"port": lldp_entry["port_id"], "hostname": hostname}
            lldp[interface].append(lldp_dict)

        return lldp

    def get_bgp_neighbors(self):
        """
        Returns a dictionary of dictionaries. The keys for the first dictionary will be the vrf
        (global if no vrf). The inner dictionary will contain the following data for each vrf:
          * router_id
          * peers - another dictionary of dictionaries. Outer keys are the IPs of the neighbors. \
            The inner keys are:
             * local_as (int)
             * remote_as (int)
             * remote_id - peer router id
             * is_up (True/False)
             * is_enabled (True/False)
             * description (string)
             * uptime (int in seconds)
             * address_family (dictionary) - A dictionary of address families available for the \
               neighbor. So far it can be 'ipv4' or 'ipv6'
                * received_prefixes (int)
                * accepted_prefixes (int)
                * sent_prefixes (int)
            Note, if is_up is False and uptime has a positive value then this indicates the
            uptime of the last active BGP session.
            Example::
                {
                  "global": {
                    "router_id": "10.0.1.1",
                    "peers": {
                      "10.0.0.2": {
                        "local_as": 65000,
                        "remote_as": 65000,
                        "remote_id": "10.0.1.2",
                        "is_up": True,
                        "is_enabled": True,
                        "description": "internal-2",
                        "uptime": 4838400,
                        "address_family": {
                          "ipv4": {
                            "sent_prefixes": 637213,
                            "accepted_prefixes": 3142,
                            "received_prefixes": 3142
                          },
                          "ipv6": {
                            "sent_prefixes": 36714,
                            "accepted_prefixes": 148,
                            "received_prefixes": 148
                          }
                        }
                      }
                    }
                  }
                }
        """

        raw_show_ip_bgp_summary = self._send_command("show ip bgp summary")
        raw_show_ip_bgp_neighbors = self._send_command("show ip bgp neighbors")
        raw_show_bgp_ipv6_neighbors = self._send_command("show bgp ipv6 neighbors")

        show_ip_bgp_summary = textfsm_extractor(
            self, "show_ip_bgp_summary", raw_show_ip_bgp_summary
        )
        show_ip_bgp_neighbors = textfsm_extractor(
            self, "show_ip_bgp_neighbors", raw_show_ip_bgp_neighbors
        )
        show_bgp_ipv6_neighbors = textfsm_extractor(
            self, "show_bgp_ipv6_neighbors", raw_show_bgp_ipv6_neighbors
        )

        router_id = show_ip_bgp_summary[0]["bgp_router_id"]
        local_as = int(show_ip_bgp_summary[0]["local_as"])
        bgp_neighbors = {"global": {"router_id": router_id, "peers": {}}}
        for neighbor in show_ip_bgp_neighbors:
            peer_addr = neighbor["peer_addr"]
            bgp_neighbors["global"]["peers"][peer_addr] = {
                "local_as": local_as,
                "remote_as": int(neighbor["peer_as"]),
                "remote_id": neighbor["peer_id"],
                "is_up": (neighbor["peer_state"] == "ESTABLISHED"),
                "is_enabled": (neighbor["peer_status_admin"] == "START"),
                "description": "",
                "uptime": -1,
                "address_family": {},
            }
            if neighbor["ipv4_ucast"] != "None":
                bgp_neighbors["global"]["peers"][peer_addr]["address_family"][
                    "ipv4"
                ] = {
                    "sent_prefixes": int(neighbor["ipv4_pfx_adv_tx"]),
                    "accepted_prefixes": int(neighbor["ipv4_pfx_current_rx"]),
                    "received_prefixes": int(neighbor["ipv4_pfx_adv_rx"]),
                }
            if neighbor["ipv6_ucast"] != "None":
                bgp_neighbors["global"]["peers"][peer_addr]["address_family"][
                    "ipv6"
                ] = {
                    "sent_prefixes": int(neighbor["ipv6_pfx_adv_tx"]),
                    "accepted_prefixes": int(neighbor["ipv6_pfx_current_rx"]),
                    "received_prefixes": int(neighbor["ipv6_pfx_adv_rx"]),
                }
        for neighbor in show_bgp_ipv6_neighbors:
            peer_addr = neighbor["peer_addr"]
            bgp_neighbors["global"]["peers"][peer_addr] = {
                "local_as": local_as,
                "remote_as": int(neighbor["peer_as"]),
                "remote_id": neighbor["peer_id"],
                "is_up": (neighbor["peer_state"] == "ESTABLISHED"),
                "is_enabled": (neighbor["peer_status_admin"] == "START"),
                "description": neighbor["desc"],
                "uptime": -1,
                "address_family": {},
            }
            if neighbor["ipv4_ucast"] != "None":
                bgp_neighbors["global"]["peers"][peer_addr]["address_family"][
                    "ipv4"
                ] = {
                    "sent_prefixes": int(neighbor["ipv4_pfx_adv_tx"]),
                    "accepted_prefixes": int(neighbor["ipv4_pfx_current_rx"]),
                    "received_prefixes": int(neighbor["ipv4_pfx_adv_rx"]),
                }
            if neighbor["ipv6_ucast"] != "None":
                bgp_neighbors["global"]["peers"][peer_addr]["address_family"][
                    "ipv6"
                ] = {
                    "sent_prefixes": int(neighbor["ipv6_pfx_adv_tx"]),
                    "accepted_prefixes": int(neighbor["ipv6_pfx_current_rx"]),
                    "received_prefixes": int(neighbor["ipv6_pfx_adv_rx"]),
                }

        return bgp_neighbors

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

        show_sys_fans = textfsm_extractor(self, "show_system-fans", raw_show_sys)
        show_sys_temps = textfsm_extractor(self, "show_system-temps", raw_show_sys)
        show_sys_power = textfsm_extractor(
            self, "show_system-power_supplies", raw_show_sys
        )
        show_proc_cpu = textfsm_extractor(self, "show_process_cpu", raw_show_proc_cpu)

        environment = {}
        environment.setdefault("fans", {})
        environment.setdefault("temperature", {})
        environment.setdefault("power", {})
        environment.setdefault("cpu", {})
        environment.setdefault("memory", {})

        for fan in show_sys_fans:
            environment["fans"].setdefault(
                "unit " + fan["unit"] + " " + fan["description"], {}
            )
            if fan["status"] == "OK":
                environment["fans"]["unit " + fan["unit"] + " " + fan["description"]][
                    "status"
                ] = True
            else:
                environment["fans"]["unit " + fan["unit"] + " " + fan["description"]][
                    "status"
                ] = False
        for temp in show_sys_temps:
            environment["temperature"].setdefault(
                "unit " + temp["unit"] + " " + temp["description"], {}
            )
            environment["temperature"][
                "unit " + temp["unit"] + " " + temp["description"]
            ] = {
                "temperature": float(temp["temp"]),
                "is_alert": False,
                "is_critical": False,
            }
        for power in show_sys_power:
            environment["power"].setdefault(
                "unit " + power["unit"] + " " + power["description"], {}
            )
            environment["power"][
                "unit " + power["unit"] + " " + power["description"]
            ] = {"status": False, "capacity": -1.0, "output": float(power["pwr_cur"])}
            if power["status"] == "OK":
                environment["power"][
                    "unit " + power["unit"] + " " + power["description"]
                ]["status"] = True
        environment["cpu"][0] = {}
        environment["cpu"][0]["%usage"] = 0.0
        environment["cpu"][0]["%usage"] = float(show_proc_cpu[0]["cpu_60"])
        environment["memory"] = {
            "available_ram": int(show_proc_cpu[0]["mem_free"]) * 1024,
            "used_ram": int(show_proc_cpu[0]["mem_alloc"]) * 1024,
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
                "tx_errors": -1,
                "rx_errors": -1,
                "tx_discards": -1,
                "rx_discards": -1,
                "tx_octets": -1,
                "rx_octets": -1,
                "tx_unicast_packets": -1,
                "rx_unicast_packets": -1,
                "tx_multicast_packets": -1,
                "rx_multicast_packets": -1,
                "tx_broadcast_packets": -1,
                "rx_broadcast_packets": -1,
            }

            for int_count_err in show_int_count_err:
                interface_name = canonical_interface_name(
                    int_count_err["interface"], addl_name_map=dellos6_interfaces
                )
                if interface_name == int_list:
                    if (
                        int_count_err["out_total"].isdigit()
                        and int(int_count_err["out_total"]) >= 0
                    ):
                        int_counters[int_list]["tx_errors"] = int(
                            int_count_err["out_total"]
                        )
                    if (
                        int_count_err["in_total"].isdigit()
                        and int(int_count_err["in_total"]) >= 0
                    ):
                        int_counters[int_list]["rx_errors"] = int(
                            int_count_err["in_total"]
                        )
                    if (
                        int_count_err["out_discard"].isdigit()
                        and int(int_count_err["out_discard"]) >= 0
                    ):
                        int_counters[int_list]["tx_discards"] = int(
                            int_count_err["out_discard"]
                        )

            for int_count in show_int_count:
                interface_name = canonical_interface_name(
                    int_count["interface"], addl_name_map=dellos6_interfaces
                )
                if interface_name == int_list:
                    if (
                        int_count["out_total_octs"].isdigit()
                        and int(int_count["out_total_octs"]) >= 0
                    ):
                        int_counters[int_list]["tx_octets"] = int(
                            int_count["out_total_octs"]
                        )
                    if (
                        int_count["in_total_octs"].isdigit()
                        and int(int_count["in_total_octs"]) >= 0
                    ):
                        int_counters[int_list]["rx_octets"] = int(
                            int_count["in_total_octs"]
                        )
                    if (
                        int_count["out_ucast_pkts"].isdigit()
                        and int(int_count["out_ucast_pkts"]) >= 0
                    ):
                        int_counters[int_list]["tx_unicast_packets"] = int(
                            int_count["out_ucast_pkts"]
                        )
                    if (
                        int_count["in_ucast_pkts"].isdigit()
                        and int(int_count["in_ucast_pkts"]) >= 0
                    ):
                        int_counters[int_list]["rx_unicast_packets"] = int(
                            int_count["in_ucast_pkts"]
                        )
                    if (
                        int_count["out_mcast_pkts"].isdigit()
                        and int(int_count["out_mcast_pkts"]) >= 0
                    ):
                        int_counters[int_list]["tx_multicast_packets"] = int(
                            int_count["out_mcast_pkts"]
                        )
                    if (
                        int_count["in_mcast_pkts"].isdigit()
                        and int(int_count["in_mcast_pkts"]) >= 0
                    ):
                        int_counters[int_list]["rx_multicast_packets"] = int(
                            int_count["in_mcast_pkts"]
                        )
                    if (
                        int_count["out_bcast_pkts"].isdigit()
                        and int(int_count["out_bcast_pkts"]) >= 0
                    ):
                        int_counters[int_list]["tx_broadcast_packets"] = int(
                            int_count["out_bcast_pkts"]
                        )
                    if (
                        int_count["in_bcast_pkts"].isdigit()
                        and int(int_count["in_bcast_pkts"]) >= 0
                    ):
                        int_counters[int_list]["rx_broadcast_packets"] = int(
                            int_count["in_bcast_pkts"]
                        )

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
        raw_show_lldp_remote_device_all = self._send_command(
            "show lldp remote-device all"
        )

        show_lldp_remote_device_all = textfsm_extractor(
            self, "show_lldp_remote-device_all", raw_show_lldp_remote_device_all
        )

        lldp = {}
        for lldp_entry in show_lldp_remote_device_all:
            interface = canonical_interface_name(
                lldp_entry["interface"], addl_name_map=dellos6_interfaces
            )
            lldp[interface] = {}
            raw_show_lldp_remote_device_detail = self._send_command(
                "show lldp remote-device detail " + lldp_entry["interface"]
            )
            show_lldp_remote_device_detail = textfsm_extractor(
                self,
                "show_lldp_remote-device_detail",
                raw_show_lldp_remote_device_detail,
            )
            # We don't yet support reporting the parent interface
            parent_interface = ""
            remote_chassis_id = lldp_entry["chassis_id"]
            remote_system_name = show_lldp_remote_device_detail[0]["host_name"]
            remote_port = show_lldp_remote_device_detail[0]["port_id"]
            remote_port_description = show_lldp_remote_device_detail[0]["port_desc"]
            remote_system_description = show_lldp_remote_device_detail[0]["sys_desc"]
            if show_lldp_remote_device_detail[0]["sys_cap_sup"]:
                remote_system_capab = (
                    show_lldp_remote_device_detail[0]["sys_cap_sup"]
                    .replace(" ", "")
                    .split(",")
                )
            else:
                remote_system_capab = []
            if show_lldp_remote_device_detail[0]["sys_cap_oper"]:
                remote_system_enable_capab = (
                    show_lldp_remote_device_detail[0]["sys_cap_oper"]
                    .replace(" ", "")
                    .split(",")
                )
            else:
                remote_system_enable_capab = []

            entry_list = []
            entry = {
                "parent_interface": parent_interface,
                "remote_chassis_id": remote_chassis_id,
                "remote_system_name": remote_system_name,
                "remote_port": remote_port,
                "remote_port_description": remote_port_description,
                "remote_system_description": remote_system_description,
                "remote_system_capab": remote_system_capab,
                "remote_system_enable_capab": remote_system_enable_capab,
            }
            entry_list.append(entry)
            lldp[interface] = entry_list

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

        show_arp = textfsm_extractor(self, "show_arp", raw_show_arp)

        arp_table = []
        for entry in show_arp:
            arp_table.append(
                {
                    "interface": canonical_interface_name(
                        entry["interface"], addl_name_map=dellos6_interfaces
                    ),
                    "mac": mac(entry["mac_address"]),
                    "ip": entry["ip_address"],
                    "age": float(self.parse_arp_age(entry["age"])),
                }
            )

        return arp_table

    def get_ntp_peers(self):

        """
        Returns the NTP peers configuration as dictionary.
        The keys of the dictionary represent the IP Addresses of the peers.
        Inner dictionaries do not have yet any available keys.
        Example::
            {
                '192.168.0.1': {},
                '17.72.148.53': {},
                '37.187.56.220': {},
                '162.158.20.18': {}
            }
        """

        raw_show_sntp_status = self._send_command("show sntp status")

        show_sntp_status = textfsm_extractor(
            self, "show_sntp_status", raw_show_sntp_status
        )

        ntp_peers = {}
        for peer in show_sntp_status:
            ntp_peers[peer["server_ip"]] = {}

        return ntp_peers

    def get_ntp_servers(self):

        """
        Returns the NTP servers configuration as dictionary.
        The keys of the dictionary represent the IP Addresses of the servers.
        Inner dictionaries do not have yet any available keys.
        Example::
            {
                '192.168.0.1': {},
                '17.72.148.53': {},
                '37.187.56.220': {},
                '162.158.20.18': {}
            }
        """

        raw_show_sntp_server = self._send_command("show sntp server")

        show_sntp_server = textfsm_extractor(
            self, "show_sntp_server", raw_show_sntp_server
        )

        ntp_servers = {}
        for server in show_sntp_server:
            ntp_servers[server["server_ip"]] = {}

        return ntp_servers

    def get_ntp_stats(self):

        """
        Returns a list of NTP synchronization statistics.
            * remote (string)
            * referenceid (string)
            * synchronized (True/False)
            * stratum (int)
            * type (string)
            * when (string)
            * hostpoll (int)
            * reachability (int)
            * delay (float)
            * offset (float)
            * jitter (float)
        Example::
            [
                {
                    'remote'        : u'188.114.101.4',
                    'referenceid'   : u'188.114.100.1',
                    'synchronized'  : True,
                    'stratum'       : 4,
                    'type'          : u'-',
                    'when'          : u'107',
                    'hostpoll'      : 256,
                    'reachability'  : 377,
                    'delay'         : 164.228,
                    'offset'        : -13.866,
                    'jitter'        : 2.695
                }
            ]
        """

        raw_show_sntp_stats = self._send_command("show sntp server")

        show_sntp_stats = textfsm_extractor(
            self, "show_sntp_server", raw_show_sntp_stats
        )

        ntp_stats = []
        for server in show_sntp_stats:
            if server["status"] == "Success":
                synchronized = True
            else:
                synchronized = False
            ntp_stats.append(
                {
                    "remote": server["server_ip"],
                    # Not supported
                    "referenceid": "",
                    "synchronized": synchronized,
                    # Not supported
                    "stratum": -1,
                    # We only support parsing unicast servers right now
                    "type": "u",
                    # We don't support parsing this right now
                    "when": "",
                    # Not supported
                    "hostpoll": -1,
                    # Not supported
                    "reachability": -1,
                    # Not supported
                    "delay": -0.0,
                    # Not supported
                    "offset": -0.0,
                    # Not supported
                    "jitter": -0.0,
                }
            )

        return ntp_stats

    def get_interfaces_ip(self):

        """
        Returns all configured IP addresses on all interfaces as a dictionary of dictionaries.
        Keys of the main dictionary represent the name of the interface.
        Values of the main dictionary represent are dictionaries that may consist of two keys
        'ipv4' and 'ipv6' (one, both or none) which are themselves dictionaries with the IP
        addresses as keys.
        Each IP Address dictionary has the following keys:
            * prefix_length (int)
        Example::
            {
                u'FastEthernet8': {
                    u'ipv4': {
                        u'10.66.43.169': {
                            'prefix_length': 22
                        }
                    }
                },
                u'Loopback555': {
                    u'ipv4': {
                        u'192.168.1.1': {
                            'prefix_length': 24
                        }
                    },
                    u'ipv6': {
                        u'1::1': {
                            'prefix_length': 64
                        },
                        u'2001:DB8:1::1': {
                            'prefix_length': 64
                        },
                        u'2::': {
                            'prefix_length': 64
                        },
                        u'FE80::3': {
                            'prefix_length': u'N/A'
                        }
                    }
                },
                u'Tunnel0': {
                    u'ipv4': {
                        u'10.63.100.9': {
                            'prefix_length': 24
                        }
                    }
                }
            }
        """

        raw_show_ip_int = self._send_command("show ip interface")
        raw_show_ip_int_oob = self._send_command("show ip interface out-of-band")
        raw_show_ipv6_int = self._send_command("show ipv6 interface")
        raw_show_ipv6_int_oob = self._send_command("show ipv6 interface out-of-band")

        show_ip_int = textfsm_extractor(self, "show_ip_interface", raw_show_ip_int)
        show_ip_int_oob = textfsm_extractor(
            self, "show_ip_interface_out-of-band", raw_show_ip_int_oob
        )
        show_ipv6_int = textfsm_extractor(
            self, "show_ipv6_interface", raw_show_ipv6_int
        )
        show_ipv6_int_oob = textfsm_extractor(
            self, "show_ipv6_interface_out-of-band", raw_show_ipv6_int_oob
        )

        interfaces_ip = {}
        for int in show_ip_int:
            interface = canonical_interface_name(
                int["interface"], addl_name_map=dellos6_interfaces
            )
            raw_show_ip_int_vlan = self._send_command("show ip interface " + interface)
            show_ip_int_vlan = textfsm_extractor(
                self, "show_ip_interface_vlan", raw_show_ip_int_vlan
            )
            for vlan_int in show_ip_int_vlan:
                if vlan_int["ip_addr_pri"]:
                    interfaces_ip.setdefault(interface, {})
                    interfaces_ip[interface].setdefault("ipv4", {})
                    ip_address = str(IPv4Interface(vlan_int["ip_addr_pri"]).ip)
                    prefix_len = IPv4Interface(
                        vlan_int["ip_addr_pri"]
                    ).network.prefixlen
                    interfaces_ip[interface]["ipv4"][ip_address] = {
                        "prefix_length": prefix_len
                    }
                if vlan_int["ip_addr_sec"]:
                    for ip in vlan_int["ip_addr_sec"]:
                        ip_address = str(IPv4Interface(ip).ip)
                        prefix_len = IPv4Interface(ip).network.prefixlen
                        interfaces_ip[interface]["ipv4"][ip_address] = {
                            "prefix_length": prefix_len
                        }

        for int in show_ipv6_int:
            interface = canonical_interface_name(
                int["interface"], addl_name_map=dellos6_interfaces
            )
            raw_show_ipv6_int_vlan = self._send_command(
                "show ipv6 interface " + interface
            )
            show_ipv6_int_vlan = textfsm_extractor(
                self, "show_ipv6_interface_vlan", raw_show_ipv6_int_vlan
            )
            for vlan_int in show_ipv6_int_vlan:
                if vlan_int["ipv6_pfx"]:
                    interfaces_ip.setdefault(interface, {})
                    interfaces_ip[interface].setdefault("ipv6", {})
                    for ipv6 in vlan_int["ipv6_pfx"]:
                        ipv6_address = str(IPv6Interface(ipv6).ip)
                        prefix_len = IPv6Interface(ipv6).network.prefixlen
                        interfaces_ip[interface]["ipv6"][ipv6_address] = {
                            "prefix_length": prefix_len
                        }

        if show_ip_int_oob[0]["ip_addr"]:
            interfaces_ip.setdefault("out-of-band", {})
            interfaces_ip["out-of-band"].setdefault("ipv4", {})
            ip_address = show_ip_int_oob[0]["ip_addr"]
            prefix_len = IPv4Interface(
                show_ip_int_oob[0]["ip_addr"] + "/" + show_ip_int_oob[0]["subnet_mask"]
            ).network.prefixlen
            interfaces_ip["out-of-band"]["ipv4"][ip_address] = {
                "prefix_length": prefix_len
            }
            raw_show_ipv6_int_vlan = self._send_command(
                "show ipv6 interface " + interface
            )
            show_ipv6_int_vlan = textfsm_extractor(
                self, "show_ipv6_interface_vlan", raw_show_ipv6_int_vlan
            )

        if show_ipv6_int_oob[0]["ipv6_pfx"]:
            interfaces_ip.setdefault("out-of-band", {})
            interfaces_ip["out-of-band"].setdefault("ipv6", {})
            for ipv6 in show_ipv6_int_oob[0]["ipv6_pfx"]:
                ipv6_address = str(IPv6Interface(ipv6).ip)
                prefix_len = IPv6Interface(ipv6).network.prefixlen
                interfaces_ip["out-of-band"]["ipv6"][ipv6_address] = {
                    "prefix_length": prefix_len
                }

        return interfaces_ip

    def get_ipv6_neighbors_table(self):
        """
        Get IPv6 neighbors table information.
        Return a list of dictionaries having the following set of keys:
            * interface (string)
            * mac (string)
            * ip (string)
            * age (float) in seconds
            * state (string)
        For example::
            [
                {
                    'interface' : 'MgmtEth0/RSP0/CPU0/0',
                    'mac'       : '5c:5e:ab:da:3c:f0',
                    'ip'        : '2001:db8:1:1::1',
                    'age'       : 1454496274.84,
                    'state'     : 'REACH'
                },
                {
                    'interface': 'MgmtEth0/RSP0/CPU0/0',
                    'mac'       : '66:0e:94:96:e0:ff',
                    'ip'        : '2001:db8:1:1::2',
                    'age'       : 1435641582.49,
                    'state'     : 'STALE'
                }
            ]
        """

        raw_show_ipv6_neighbors = self._send_command("show ipv6 neighbors")
        show_ipv6_neighbors = textfsm_extractor(
            self, "show_ipv6_neighbors", raw_show_ipv6_neighbors
        )

        ipv6_neighbors = []
        for neighbor in show_ipv6_neighbors:
            interface_name = canonical_interface_name(
                neighbor["int_name"], addl_name_map=dellos6_interfaces
            )
            mac_addr = mac(neighbor["mac_addr"])
            ipv6_addr = neighbor["ipv6_addr"]
            # Dell OS6 doesn't support age
            age = -0.0
            state = neighbor["state"].upper()
            ipv6_neighbors.append(
                {
                    "interface": interface_name,
                    "mac": mac_addr,
                    "ip": ipv6_addr,
                    "age": age,
                    "state": state,
                }
            )

        return ipv6_neighbors

    def _expand_ranges(self, iflist):
        """
        In: ["Gi1/0/42-43"]
        Out: ["Gi1/0/42", "Gi1/0/43"]
        """
        expanded_interfaces = []
        for interface in iflist:
            m = re.match(r"(\S\S|.+/)((\d+)-(\d+))", interface)
            if m is None:
                expanded_interfaces.append(interface)
            else:
                interfaces = []
                for i in range(int(m.group(3)), int(m.group(4)) + 1):
                    interfaces.append("%s%d" % (m.group(1), i))
                expanded_interfaces = expanded_interfaces + interfaces
        return expanded_interfaces

    def _ensure_ports_split(self, ports):
        "textFSM cannot split repeated values in the same line. Do it here."
        result = []
        for port in ports:
            result = result + port.split(",")
        return result

    def get_vlans(self):
        """
        turn structure being spit balled is as follows.
        vlan_id (int)
                name (text_type)
                interfaces (list)
        Example:
        {
            1: {
                "name": "default",
                "interfaces": ["GigabitEthernet0/0/1", "GigabitEthernet0/0/2"]
            },
            2: {
                "name": "vlan2",
                "interfaces": []
            }
        }
        """
        raw_show_vlan = self._send_command("show vlan")
        show_vlan = textfsm_extractor(self, "show_vlan", raw_show_vlan)
        interface_dict = self._get_interface_dict()

        vlans = {}
        for vlan_entry in show_vlan:
            canonical_interfaces = []
            ports = self._ensure_ports_split(vlan_entry["ports"])
            for interface in self._expand_ranges(ports):
                interface_name = canonical_interface_name(
                    interface, addl_name_map=dellos6_interfaces
                )
                if interface_name in interface_dict.keys():
                    canonical_interfaces.append(interface_name)
            vlans[int(vlan_entry["vlan_id"])] = {
                "name": vlan_entry["vlan_name"],
                "interfaces": canonical_interfaces,
            }
        return vlans

    def get_mac_address_table(self):
        """
        Returns a lists of dictionaries. Each dictionary represents an entry in the MAC Address
        Table, having the following keys:
            * mac (string)
            * interface (string)
            * vlan (int)
            * active (boolean)
            * static (boolean)
            * moves (int)
            * last_move (float)
        However, please note that not all vendors provide all these details.
        E.g.: field last_move is not available on JUNOS devices etc.
        Example::
            [
                {
                    'mac'       : '00:1C:58:29:4A:71',
                    'interface' : 'Ethernet47',
                    'vlan'      : 100,
                    'static'    : False,
                    'active'    : True,
                    'moves'     : 1,
                    'last_move' : 1454417742.58
                },
                {
                    'mac'       : '00:1C:58:29:4A:C1',
                    'interface' : 'xe-1/0/1',
                    'vlan'       : 100,
                    'static'    : False,
                    'active'    : True,
                    'moves'     : 2,
                    'last_move' : 1453191948.11
                },
                {
                    'mac'       : '00:1C:58:29:4A:C2',
                    'interface' : 'ae7.900',
                    'vlan'      : 900,
                    'static'    : False,
                    'active'    : True,
                    'moves'     : None,
                    'last_move' : None
                }
            ]
        """
        raw_get_mac_address_table = self._send_command("show mac address-table")
        get_mac_address_table = textfsm_extractor(
            self, "show_mac_address_table", raw_get_mac_address_table
        )
        table = []
        for entry in get_mac_address_table:
            table.append(
                {
                    "mac": mac(entry["mac"]),
                    "interface": canonical_interface_name(
                        entry["port"], addl_name_map=dellos6_interfaces
                    ),
                    "vlan": int(entry["vlan"]),
                    "static": entry["type"] == "Static"
                    or entry["type"] == "Management",
                    "active": True,
                    "moves": -1,
                    "last_move": -1.0,
                }
            )
        return table

    def get_snmp_information(self):

        """
        Returns a dict of dicts containing SNMP configuration.
        Each inner dictionary contains these fields
            * chassis_id (string)
            * community (dictionary)
            * contact (string)
            * location (string)
        'community' is a dictionary with community string specific information, as follows:
            * acl (string) # acl number or name
            * mode (string) # read-write (rw), read-only (ro)
        Example::
            {
                'chassis_id': u'Asset Tag 54670',
                'community': {
                    u'private': {
                        'acl': u'12',
                        'mode': u'rw'
                    },
                    u'public': {
                        'acl': u'11',
                        'mode': u'ro'
                    },
                    u'public_named_acl': {
                        'acl': u'ALLOW-SNMP-ACL',
                        'mode': u'ro'
                    },
                    u'public_no_acl': {
                        'acl': u'N/A',
                        'mode': u'ro'
                    }
                },
                'contact' : u'Joe Smith',
                'location': u'123 Anytown USA Rack 404'
            }
        """

        raw_show_sys = self._send_command("show system")
        raw_show_snmp = self._send_command("show snmp")

        show_sys = textfsm_extractor(self, "show_system-basic", raw_show_sys)
        show_snmp_basic = textfsm_extractor(self, "show_snmp-basic", raw_show_snmp)
        show_snmp_communities = textfsm_extractor(
            self, "show_snmp-communities", raw_show_snmp
        )
        snmp_info = {
            # Dell OS6 doesn't support setting the chassis ID, it's derived from the hostname
            "chassis_id": show_sys[0]["sys_name"],
            "community": {},
            "contact": show_snmp_basic[0]["contact"],
            "location": show_snmp_basic[0]["location"],
        }

        for entry in show_snmp_communities:
            community = entry["community"]
            if entry["acl"] == "All":
                acl = u"N/A"
            else:
                # Dell OS6 only supports direct host entries, no ACLs
                acl = entry["acl"] + "/32"
            if entry["mode"] == "Read Only":
                mode = u"ro"
            if entry["mode"] == "Read/Write":
                mode = u"rw"
            snmp_info["community"][community] = {"acl": acl, "mode": mode}

        return snmp_info

    def ping(
        self,
        destination,
        source=C.PING_SOURCE,
        ttl=C.PING_TTL,
        timeout=C.PING_TIMEOUT,
        size=C.PING_SIZE,
        count=C.PING_COUNT,
        vrf=C.PING_VRF,
    ):
        """
        Executes ping on the device and returns a dictionary with the result
        :param destination: Host or IP Address of the destination
        :param source (optional): Source address of echo request
        :param ttl (optional): Maximum number of hops
        :param timeout (optional): Maximum seconds to wait after sending final packet
        :param size (optional): Size of request (bytes)
        :param count (optional): Number of ping request to send
        Output dictionary has one of following keys:
            * success
            * error
        In case of success, inner dictionary will have the followin keys:
            * probes_sent (int)
            * packet_loss (int)
            * rtt_min (float)
            * rtt_max (float)
            * rtt_avg (float)
            * rtt_stddev (float)
            * results (list)
        'results' is a list of dictionaries with the following keys:
            * ip_address (str)
            * rtt (float)
        Example::
            {
                'success': {
                    'probes_sent': 5,
                    'packet_loss': 0,
                    'rtt_min': 72.158,
                    'rtt_max': 72.433,
                    'rtt_avg': 72.268,
                    'rtt_stddev': 0.094,
                    'results': [
                        {
                            'ip_address': u'1.1.1.1',
                            'rtt': 72.248
                        },
                        {
                            'ip_address': '2.2.2.2',
                            'rtt': 72.299
                        }
                    ]
                }
            }
            OR
            {
                'error': 'unknown host 8.8.8.8.8'
            }
        """

        vrf_name = ""
        if vrf:
            vrf_name = " vrf " + str(vrf)

        params = ""
        if source:
            params = params + " source "
        if timeout:
            params = params + " timeout " + str(timeout)
        if size:
            params = params + " size " + str(size)
        if count:
            params = params + " repeat " + str(count)

        cmd = "ping{} {}{}".format(vrf_name, destination, params)
        ping_dict = {}

        send_received_regexp = (
            r"(\d+)\s+packets transmitted\S+\s+(\d+)\s+"
            r"packets received\S+\s+\S+\s+packet loss"
        )
        icmp_result_regexp = (
            r"Reply From\s+(\S+)\:\s+icmp_seq\s+=\s+(\d+)\.\s+"
            r"time=\s+(\d+)\s+usec\."
        )
        min_avg_max_reg_exp = (
            r"round-trip \(msec\)\s+min\/avg\/max\s+=\s+(\S+)\/" r"(\S+)\/(\S+)"
        )

        output = self._send_command(cmd)

        if "% Error" in output:
            status = "error"
            ping_dict = {"results": ("command :: " + cmd + " :: " + output)}
        elif "packets transmitted" in output:
            ping_dict = {
                "probes_sent": 0,
                "packet_loss": 0,
                "rtt_min": 0.0,
                "rtt_max": 0.0,
                "rtt_avg": 0.0,
                "rtt_stddev": 0.0,
                "results": [],
            }

            results_array = []
            std_dev_list = []
            for line in output.splitlines():
                status = "success"
                if "packets transmitted" in line:
                    sent_and_received = re.search(send_received_regexp, line)
                    probes_sent = int(sent_and_received.groups()[0])
                    probes_received = int(sent_and_received.groups()[1])
                    if probes_received == 0:
                        status = "error"
                    ping_dict["probes_sent"] = probes_sent
                    ping_dict["packet_loss"] = probes_sent - probes_received
                elif "icmp_seq" in line:
                    icmp_result = re.search(icmp_result_regexp, line)
                    results_array.append(
                        {
                            "ip_address": icmp_result.groups()[0],
                            "rtt": float(icmp_result.groups()[2]) / 1000,
                        }
                    )
                    ping_dict.update({"results": results_array})
                    std_dev_list.append(float(icmp_result.groups()[2]) / 1000)
                elif "round-trip (msec)" in line:
                    min_avg = re.search(min_avg_max_reg_exp, line)
                    if std_dev_list:
                        rtt_stddev = stdev(std_dev_list)
                    else:
                        rtt_stddev = 0.0
                    if min_avg.groups()[0] == "<10":
                        rtt_min = 0.0
                    else:
                        rtt_min = float(min_avg.groups()[0])
                    if min_avg.groups()[1] == "<10":
                        rtt_avg = 0.0
                    else:
                        rtt_avg = float(min_avg.groups()[1])
                    if min_avg.groups()[2] == "<10":
                        rtt_max = 0.0
                    else:
                        rtt_max = float(min_avg.groups()[2])
                    ping_dict.update(
                        {
                            "rtt_min": rtt_min,
                            "rtt_avg": rtt_avg,
                            "rtt_max": rtt_max,
                            "rtt_stddev": rtt_stddev,
                        }
                    )

        return {status: ping_dict}

    def get_users(self):
        """
        Returns a dictionary with the configured users.
        The keys of the main dictionary represents the username. The values represent the details
        of the user, represented by the following keys:
            * level (int)
            * password (str)
            * sshkeys (list)
        The level is an integer between 0 and 15, where 0 is the lowest access and 15 represents
        full access to the device.
        Example::
            {
                'mircea': {
                    'level': 15,
                    'password': '$1$0P70xKPa$z46fewjo/10cBTckk6I/w/',
                    'sshkeys': [
                        'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC4pFn+shPwTb2yELO4L7NtQrKOJXNeCl1je\
                         l9STXVaGnRAnuc2PXl35vnWmcUq6YbUEcgUTRzzXfmelJKuVJTJIlMXii7h2xkbQp0YZIEs4P\
                         8ipwnRBAxFfk/ZcDsN3mjep4/yjN56eorF5xs7zP9HbqbJ1dsqk1p3A/9LIL7l6YewLBCwJj6\
                         D+fWSJ0/YW+7oH17Fk2HH+tw0L5PcWLHkwA4t60iXn16qDbIk/ze6jv2hDGdCdz7oYQeCE55C\
                         CHOHMJWYfN3jcL4s0qv8/u6Ka1FVkV7iMmro7ChThoV/5snI4Ljf2wKqgHH7TfNaCfpU0WvHA\
                         nTs8zhOrGScSrtb mircea@master-roshi'
                    ]
                }
            }
        """

        username_regex = (
            r"^username\s+\"(?P<username>\S+)\"\s+password\s+(?P<pwd_hash>[0-9a-f]+).*"
        )

        raw_show_users_accounts = self._send_command("show users accounts")
        show_users_accounts = textfsm_extractor(
            self, "show_users_accounts", raw_show_users_accounts
        )
        users = {}
        for user in show_users_accounts:
            users[user["username"]] = {
                "level": int(user["priv"]),
                "password": "",
                "sshkeys": [],
            }

        command = "show running-config | section username"
        output = self._send_command(command)

        for match in re.finditer(username_regex, output, re.M):
            username = match.groupdict()["username"]
            pwd_hash = match.groupdict()["pwd_hash"]
            users[username]["password"] = pwd_hash

        return users

    def get_optics(self):
        """Fetches the power usage on the various transceivers installed
        on the switch (in dbm), and returns a view that conforms with the
        openconfig model openconfig-platform-transceiver.yang
        Returns a dictionary where the keys are as listed below:
            * intf_name (unicode)
                * physical_channels
                    * channels (list of dicts)
                        * index (int)
                        * state
                            * input_power
                                * instant (float)
                                * avg (float)
                                * min (float)
                                * max (float)
                            * output_power
                                * instant (float)
                                * avg (float)
                                * min (float)
                                * max (float)
                            * laser_bias_current
                                * instant (float)
                                * avg (float)
                                * min (float)
                                * max (float)
        Example::
            {
                'et1': {
                    'physical_channels': {
                        'channel': [
                            {
                                'index': 0,
                                'state': {
                                    'input_power': {
                                        'instant': 0.0,
                                        'avg': 0.0,
                                        'min': 0.0,
                                        'max': 0.0,
                                    },
                                    'output_power': {
                                        'instant': 0.0,
                                        'avg': 0.0,
                                        'min': 0.0,
                                        'max': 0.0,
                                    },
                                    'laser_bias_current': {
                                        'instant': 0.0,
                                        'avg': 0.0,
                                        'min': 0.0,
                                        'max': 0.0,
                                    },
                                }
                            }
                        ]
                    }
                }
            }
        """

        raw_show_fiber_ports_optical_transceiver = self._send_command(
            "show fiber-ports optical transceiver"
        )
        show_fiber_ports_optical_transceiver = textfsm_extractor(
            self,
            "show_fiber-ports_optical-transceiver",
            raw_show_fiber_ports_optical_transceiver,
        )

        optics = {}
        for interface in show_fiber_ports_optical_transceiver:
            interface_name = canonical_interface_name(
                interface["int_name"], addl_name_map=dellos6_interfaces
            )
            pwr_rx = float(interface["pwr_rx"])
            pwr_tx = float(interface["pwr_tx"])
            current = float(interface["current"])

            optics[interface_name] = {
                "physical_channels": {
                    "channel": [
                        {
                            # We do not yet support multiple channels
                            "index": 0,
                            "state": {
                                "input_power": {
                                    "instant": pwr_rx,
                                    "avg": -0.0,
                                    "min": -0.0,
                                    "max": -0.0,
                                },
                                "output_power": {
                                    "instant": pwr_tx,
                                    "avg": -0.0,
                                    "min": -0.0,
                                    "max": -0.0,
                                },
                                "laser_bias_current": {
                                    "instant": current,
                                    "avg": -0.0,
                                    "min": -0.0,
                                    "max": -0.0,
                                },
                            },
                        }
                    ]
                }
            }

        return optics

    def get_config(self, retrieve="all", full=False, sanitized=False):
        """
        Return the configuration of a device.

        Args:
            retrieve(string): Which configuration type you want to populate, default is all of them.
                              The rest will be set to "".
            full(bool): Retrieve all the configuration. For instance, on ios, "sh run all".
            sanitized(bool): Remove secret data. Default: ``False``.

        Returns:
          The object returned is a dictionary with a key for each configuration store:

            - running(string) - Representation of the native running configuration
            - candidate(string) - Representation of the native candidate configuration. If the
              device doesnt differentiate between running and startup configuration this will an
              empty string
            - startup(string) - Representation of the native startup configuration. If the
              device doesnt differentiate between running and startup configuration this will an
              empty string
        """
        running_config = ""
        startup_config = ""

        if retrieve in ["all", "running"]:
            running_config = self._send_command("show running-config")
        if retrieve in ["all", "startup"]:
            startup_config = self._send_command("show startup-config")

        configs = {
            "running": running_config,
            "startup": startup_config,
            "candidate": "",
        }

        if sanitized:
            return sanitize_configs(configs, D6C.DELLOS6_SANITIZE_FILTERS)

        return configs

    def get_network_instances(self, name=""):
        """
        Return a dictionary of network instances (VRFs) configured, including default/global
        Args:
            name(string) - Name of the network instance to return, default is all.
        Returns:
            A dictionary of network instances in OC format:
            * name (dict)
                * name (unicode)
                * type (unicode)
                * state (dict)
                    * route_distinguisher (unicode)
                * interfaces (dict)
                    * interface (dict)
                        * interface name: (dict)
        Example::
            {
                u'MGMT': {
                    u'name': u'MGMT',
                    u'type': u'L3VRF',
                    u'state': {
                        u'route_distinguisher': u'123:456',
                    },
                    u'interfaces': {
                        u'interface': {
                            u'Management1': {}
                        }
                    }
                },
                u'default': {
                    u'name': u'default',
                    u'type': u'DEFAULT_INSTANCE',
                    u'state': {
                        u'route_distinguisher': None,
                    },
                    u'interfaces: {
                        u'interface': {
                            u'Ethernet1': {}
                            u'Ethernet2': {}
                            u'Ethernet3': {}
                            u'Ethernet4': {}
                        }
                    }
                }
            }
        """

        raw_show_ip_vrf = self._send_command("show ip vrf")
        raw_show_ip_vrf_interface = self._send_command("show ip vrf interface")
        show_ip_vrf = textfsm_extractor(self, "show_ip_vrf", raw_show_ip_vrf)
        show_ip_vrf_interface = textfsm_extractor(
            self, "show_ip_vrf_interface", raw_show_ip_vrf_interface
        )

        default_ip_interfaces = self.get_interfaces_ip()

        network_instances = {}
        network_instances[u"default"] = {
            u"name": u"default",
            u"type": u"DEFAULT_INSTANCE",
            u"state": {u"route_distinguisher": ""},
            u"interfaces": {u"interface": {}},
        }

        for interface in default_ip_interfaces.keys():
            network_instances["default"]["interfaces"]["interface"][interface] = {}

        for vrf in show_ip_vrf:
            network_instances[vrf["vrf_name"]] = {
                u"name": vrf["vrf_name"],
                u"type": u"L3VRF",
                u"state": {
                    # Dell OS6 doesn't support RDs
                    u"route_distinguisher": ""
                },
                u"interfaces": {u"interface": {}},
            }

        for interface in show_ip_vrf_interface:
            vrf_name = interface["vrf_name"]
            interface_name = canonical_interface_name(
                interface["int_name"], addl_name_map=dellos6_interfaces
            )
            network_instances[vrf_name]["interfaces"]["interface"][interface_name] = {}

        return network_instances
