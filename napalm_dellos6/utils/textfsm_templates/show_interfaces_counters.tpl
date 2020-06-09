Value Key,Required INTERFACE (\S+)
Value IN_TOTAL_PKTS (\d+)
Value IN_TOTAL_OCTS (\d+)
Value IN_UCAST_PKTS (\d+)
Value IN_MCAST_PKTS (\d+)
Value IN_BCAST_PKTS (\d+)
Value OUT_TOTAL_PKTS (\d+)
Value OUT_TOTAL_OCTS (\d+)
Value OUT_UCAST_PKTS (\d+)
Value OUT_MCAST_PKTS (\d+)
Value OUT_BCAST_PKTS (\d+)

Start
  ^\s*Port\s+InTotalPkts\s+InUcastPkts\s+InMcastPkts\s+InBcastPkts -> PortInbound
  ^\s*Port\s+OutTotalPkts\s+OutUcastPkts\s+OutMcastPkts\s+OutBcastPkts -> PortOutbound
  ^\s*Ch\s+InOctets\s+InUcastPkts\s+InMcastPkts\s+InBcastPkts -> ChInbound
  ^\s*Ch\s+OutOctets\s+OutUcastPkts\s+OutMcastPkts\s+OutBcastPkts -> ChOutbound

PortInbound
  ^---------\s+----------------\s+----------------\s+----------------\s+----------------
  ^${INTERFACE}\s+${IN_TOTAL_PKTS}\s+${IN_UCAST_PKTS}\s+${IN_MCAST_PKTS}\s+${IN_BCAST_PKTS} -> Record
  ^\s*$$ -> Start
  ^. -> Error

PortOutbound
  ^---------\s+----------------\s+----------------\s+----------------\s+----------------
  ^${INTERFACE}\s+${OUT_TOTAL_PKTS}\s+${OUT_UCAST_PKTS}\s+${OUT_MCAST_PKTS}\s+${OUT_BCAST_PKTS} -> Record
  ^\s*$$ -> Start
  ^. -> Error

ChInbound
  ^---------\s+----------------\s+----------------\s+----------------\s+----------------
  ^${INTERFACE}\s+${IN_TOTAL_OCTS}\s+${IN_UCAST_PKTS}\s+${IN_MCAST_PKTS}\s+${IN_BCAST_PKTS} -> Record
  ^\s*$$ -> Start
  ^. -> Error

ChOutbound
  ^---------\s+----------------\s+----------------\s+----------------\s+----------------
  ^${INTERFACE}\s+${OUT_TOTAL_OCTS}\s+${OUT_UCAST_PKTS}\s+${OUT_MCAST_PKTS}\s+${OUT_BCAST_PKTS} -> Record
  ^\s*$$ -> Start
  ^. -> Error

EOF