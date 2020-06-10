# napalm-dellos10

NAPALM driver for Dell EMC Networking OS6 Operating System.

### Implemented APIs

* get_facts
* get_interfaces
* get_lldp_neighbors
* get_environment
* get_interfaces_counters
* get_lldp_neighbors_detail
* get_arp_table
* get_ntp_peers
* get_ntp_servers
* get_ntp_stats

### Missing APIs.

* configuration management
* most L3

This driver is in the early stages, and is a work in progres. There are no unit tests at the moment either. Feel free to submit a PR to add additional getters.

