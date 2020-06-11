Value Required INTERFACE (\S+)
Value Required MODE_OPER (\S+)
Value Required IPV6_ADDRESS (\S+)

Start
  ^\s+Oper.
  ^Interface\s+Mode\s+IPv6 Address/Length
  ^----------\s+--------\s+---------------------------------
  ^${INTERFACE}\s+${MODE_OPER}\s+${IPV6_ADDRESS} -> Record

EOF