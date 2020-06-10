Value Required SERVER_IP (\S+)
Value Required ADDR_TYPE (\S+)
Value Required PRIORITY (\d+)
Value Required VERSION (\d+)
Value Required PORT (\d+)
Value TIME_LAST_UPD (\S.*\S)
Value TIME_LAST_ATT (\S.*\S)
Value STATUS (\S.*\S)
Value Required UCAST_REQ_TOTAL (\d+)
Value Required UCAST_REQ_FAILED (\d+)

Start
  ^SNTP Servers -> Servers

Servers
  ^Host Address\:\s+${SERVER_IP}
  ^Address Type\:\s+${ADDR_TYPE}
  ^Priority\:\s+${PRIORITY}
  ^Version\:\s+${VERSION}
  ^Port\:\s+${PORT}
  ^Last Update Time\:\s+${TIME_LAST_UPD}
  ^Last Attempt Time\:\s+${TIME_LAST_ATT}
  ^Last Update Status\:\s+${STATUS}
  ^Total Unicast Requests\:\s+${UCAST_REQ_TOTAL}
  ^Failed Unicast Requests\:\s+${UCAST_REQ_FAILED} -> Record

EOF