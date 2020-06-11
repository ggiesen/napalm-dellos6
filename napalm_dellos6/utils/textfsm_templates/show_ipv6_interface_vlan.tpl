Value List IPV6_PFX (\S+)
Value Required ROUTING_MODE (\S+)
Value Required IPV6_MODE_ENABLE (\S+)
Value Required IPV6_MODE_ADMIN (\S+)
Value Required IPV6_MODE_OPER (\S+)
Value Required MTU (\d+)
Value Required DAD_TX (\d+)
Value Required ADDR_AUTOCONF (\S+)
Value Required ADDR_DHCP (\S+)
Value Required IPV6_HOP_LIMIT_UNSPEC (\S+)
Value Required RA_NS_INTV (\d+)
Value Required RA_RTR_LIFETIME_INTV (\d+)
Value Required RA_REACH_TIME (\d+)
Value Required RA_INTV (\d+)
Value Required RA_M_FLAG (\S+)
Value Required RA_O_FLAG (\S+)
Value Required RA_SUPPRESS (\S+)
Value Required IPV6_DEST_UNREACH (\S+)

Start
  ^IPv6 is enabled
  ^IPv6 Prefix is\s+\.+\s+${IPV6_PFX}
  ^\s+${IPV6_PFX}
  ^Routing Mode\.+\s+${ROUTING_MODE}
  ^IPv6 Enable Mode\.+\s+${IPV6_MODE_ENABLE}
  ^Administrative Mode\.+\s+${IPV6_MODE_ADMIN}
  ^IPv6 Operational Mode\.+\s+${IPV6_MODE_OPER}
  ^Interface Maximum Transmit Unit\.+\s+${MTU}
  ^Router Duplicate Address Detection Transmits\.+\s+${DAD_TX}
  ^Address Autoconfigure Mode\.+\s+${ADDR_AUTOCONF}
  ^Address DHCP Mode\.+\s+${ADDR_DHCP}
  ^IPv6 Hop Limit Unspecified\.+\s+${IPV6_HOP_LIMIT_UNSPEC}
  ^Router Advertisement NS Interval\.+\s+${RA_NS_INTV}
  ^Router Lifetime Interval\.+\s+${RA_RTR_LIFETIME_INTV}
  ^Router Advertisement Reachable Time\.+\s+${RA_REACH_TIME}
  ^Router Advertisement Interval\.+\s+${RA_INTV}
  ^Router Advertisement Managed Config Flag\.+\s+${RA_M_FLAG}
  ^Router Advertisement Other Config Flag\.+\s+${RA_O_FLAG}
  ^Router Advertisement Suppress Flag\.+\s+${RA_SUPPRESS}
  ^IPv6 Destination Unreachables\.+\s+${IPV6_DEST_UNREACH} -> Record

EOF