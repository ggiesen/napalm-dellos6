Value Required IP_ADDR (\S+)
Value Required SUBNET_MASK (\S+)
Value Required DEFAULT_GATEWAY (\S+)
Value Required IPV4_PROTOCOL_ADMIN (\S+)
Value Required MAC_ADDR (\S+)

Start
  ^IP Address\.+\s+${IP_ADDR}
  ^Subnet Mask\.+\s+${SUBNET_MASK}
  ^Default Gateway\.+\s+${DEFAULT_GATEWAY}
  ^Configured IPv4 Protocol\.+\s+${IPV4_PROTOCOL_ADMIN}
  ^MAC Address\.+\s+${MAC_ADDR} -> Record

EOF