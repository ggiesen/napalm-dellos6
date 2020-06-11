Value Required IPV6_MODE_ADMIN (\S+)
Value List IPV6_PFX (\S+)
Value DEFAULT_ROUTER (\S+)
Value Required IPV6_PROTOCOL_ADMIN (\S+)
Value Required AUTOCONFIG (\S+)
Value Required MAC_ADDR (\S+)

Start
  ^IPv6 Administrative Mode\.+\s+${IPV6_MODE_ADMIN}
  ^IPv6 Prefix is\.+\s+${IPV6_PFX}
  ^\s+${IPV6_PFX}
  ^IPv6 Default Router\.+\s+${DEFAULT_ROUTER}
  ^Configured IPv6 Protocol\.+\s+${IPV6_PROTOCOL_ADMIN}
  ^IPv6 AutoConfig Mode\.+\s+${AUTOCONFIG}
  ^MAC Address\.+\s+${MAC_ADDR} -> Record

EOF