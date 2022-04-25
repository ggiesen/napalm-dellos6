
[![Build Status](https://travis-ci.org/ggiesen/napalm-dellos6.svg?branch=master)](https://travis-ci.org/ggiesen/napalm-dellos6)
[![Coverage Status](https://coveralls.io/repos/github/ggiesen/napalm-dellos6/badge.svg?branch=master)](https://coveralls.io/github/ggiesen/napalm-dellos6?branch=master)
# napalm-dellos6

NAPALM driver for Dell EMC Networking OS6 Operating System.

*I no longer have access to this hardware, so as such this repository is now archived. Feel free to ask for a transfer of ownership if you'd like to take it over, or you can simply fork it.*

### Implemented APIs

* get_facts
* get_interfaces
* get_lldp_neighbors
* get_bgp_neighbors  \*needs additional testing, built based on descriptions in manual
* get_environment
* get_interfaces_counters
* get_lldp_neighbors_detail
* get_arp_table
* get_ntp_peers
* get_ntp_servers
* get_ntp_stats
* cli
* get_interfaces_ip
* get_mac_address_table
* get_snmp_information
* ping
* get_users
* get_optics
* get_config
* get_network_instances
* get_ipv6_neighbors_table  \*needs additional testing, built based on descriptions in manual
* get_vlans

### Missing APIs

* load_template
* load_replace_candidate
* load_merge_candidate
* compare_config
* commit_config
* discard_config
* rollback
* get_bgp_config
* get_bgp_neighbors_detail
* get_route_to
* get_probes_config
* get_probes_results
* traceroute
* get_firewall_policies
* compliance_report

This driver is in the early stages, and is a work in progress. Feel free to submit a PR to add additional getters or better implementations of existing getters. Please create an issue (or comment on an existing issue) if you have problems with any of the implemented getters.

