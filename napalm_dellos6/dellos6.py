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
        Extract the uptime string from the given Cisco IOS Device.
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
                minutes = int(element.strip('s'))

        uptime_sec = (
            (days * DAY_SECONDS)
            + (hours * HOUR_SECONDS)
            + (minutes * 60)
            + seconds
        )
        return uptime_sec

    def get_facts(self):
        """Return a set of facts from the devices."""
        # default values.
        vendor = u'Dell'
        uptime = -1
        model, serial_number, fqdn, os_version, hostname = (self.UNKNOWN,) * 5

        # obtain output from device
        raw_show_ver = self._send_command("show version")
        raw_show_sw = self._send_command("show switch")
        raw_show_sys = self._send_command("show system")
        raw_show_hosts = self._send_command("show hosts")
        raw_show_int_status = self._send_command("show interfaces status")
        raw_show_ip_int = self._send_command("show ip interface")

        show_ver = textfsm_extractor(
            self, "show_version", raw_show_ver
        )
        show_sw = textfsm_extractor(
            self, "show_switch", raw_show_sw
        )
        show_sys = textfsm_extractor(
            self, "show_system", raw_show_sys
        )
        show_hosts = textfsm_extractor(
            self, "show_hosts", raw_show_hosts
        )
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

        uptime = self.parse_uptime(show_sys[0]['uptime'])
        os_version = show_sw[0]['version']
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