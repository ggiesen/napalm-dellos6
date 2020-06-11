Value Required STATUS_OPER (\S+)
Value IP_ADDR_PRI (\S+)
Value List IP_ADDR_SEC (\S+)
Value Required METHOD (\S+)
Value Required ROUTING_MODE (\S+)
Value Required ADMIN_MODE (\S+)
Value Required FWD_DIRECTED_BCAST (\S+)
Value Required PROXY_ARP (\S+)
Value Required LOCAL_PROXY_ARP (\S+)
Value Required ACTIVE_STATE (\S+)
Value Required MAC_ADDR (\S+)
Value Required ENCAP (\S+)
Value Required MTU (\S+)
Value Required BW (\d+)
Value Required DEST_UNREACHABLE (\S+)
Value Required ICMP_REDIRECT (\S+)

Start
  ^Routing interface status\.+\s+${STATUS_OPER}
  ^Primary IP Address\.+\s+${IP_ADDR_PRI}
  ^Secondary IP Address\(es\)\.+\s+${IP_ADDR_SEC}
  ^\.+\s+${IP_ADDR_SEC}
  ^Method\.+\s+${METHOD}
  ^Routing Mode\.+\s+${ROUTING_MODE}
  ^Administrative Mode\.+\s+${ADMIN_MODE}
  ^Forward Net Directed Broadcasts\.+\s+${FWD_DIRECTED_BCAST}
  ^Proxy ARP\.+\s+${PROXY_ARP}
  ^Local Proxy ARP\.+\s+${LOCAL_PROXY_ARP}
  ^Active State\.+\s+${ACTIVE_STATE}
  ^MAC Address\.+\s+${MAC_ADDR}
  ^Encapsulation Type\.+\s+${ENCAP}
  ^IP MTU\.+\s+${MTU}
  ^Bandwidth\.+\s+${BW}\s+kbps
  ^Destination Unreachables\.+\s+${DEST_UNREACHABLE}
  ^ICMP Redirects\.+\s+${ICMP_REDIRECT} -> Record

EOF