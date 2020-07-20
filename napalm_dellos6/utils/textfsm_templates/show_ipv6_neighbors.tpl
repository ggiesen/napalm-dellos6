Value Required IPV6_ADDR (\S+)
Value Required MAC_ADDR (\S+)
Value Required IS_RTR (\S+)
Value Required STATE (\S+)
Value Required INT_NAME (\S+)

Start
  ^Neighbor Last
  ^IPv6 Address\s+MAC Address\s+isRtr\s+State\s+Updated
  ^\s+Interface
  ^----------------------\s+-----------------\s+-----\s+-------\s+---------
  ^${IPV6_ADDR}\s+${MAC_ADDR}\s+${IS_RTR}\s+${STATE}\s+${INT_NAME} -> Record
  ^. -> Error

EOF