Value Required IPV4_ROUTING (\S+)
Value Required BGP_STATE_OPER (\S+)
Value Required BGP_ROUTER_ID (\S+)
Value Required LOCAL_AS (\d+)
Value Required TRAPS (\S+)
Value Required PATHS_MAX (\d+)
Value Required PATHS_IBGP_MAX (\d+)
Value Required KEEPALIVE_ADMIN (\d+)
Value Required HOLD_TIME_ADMIN (\d+)
Value Required NETWORK_ENTRIES (\d+)
Value Required AS_PATHS (\d+)
Value Required DYN_NEIGH_CUR (\d+)
Value Required DYN_NEIGH_MAX (\d+)
Value Required DYN_NEIGH_LIMIT (\d+)
Value Required METRIC_DEFAULT (\S+)
Value Required ORIG_DEFAULT (\S+)

Start
  ^IPv4 Routing\s*\.+\s*${IPV4_ROUTING}
  ^BGP Admin Mode\s*\.+\s*${BGP_STATE_OPER}
  ^BGP Router ID\s*\.+\s*${BGP_ROUTER_ID}
  ^Local AS Number\s*\.+\s*${LOCAL_AS}
  ^Traps\s*\.+\s*${TRAPS}
  ^Maximum Paths\s*\.+\s*${PATHS_MAX}
  ^Maximum Paths iBGP\s*\.+\s*${PATHS_IBGP_MAX}
  ^Default Keep Alive Time\s*\.+\s*${KEEPALIVE_ADMIN}
  ^Default Hold Time\s*\.+\s*${HOLD_TIME_ADMIN}
  ^Number of Network Entries\s*\.+\s*${NETWORK_ENTRIES}
  ^Number of AS Paths\s*\.+\s*${AS_PATHS}
  ^Dynamic Neighbors Current/High/Limit\s*\.+\s*${DYN_NEIGH_CUR}\/${DYN_NEIGH_MAX}\/${DYN_NEIGH_LIMIT}
  ^Default Metric\s*\.+\s*${METRIC_DEFAULT}
  ^Default Route Advertise\s*\.+\s*${ORIG_DEFAULT} -> Record

EOF