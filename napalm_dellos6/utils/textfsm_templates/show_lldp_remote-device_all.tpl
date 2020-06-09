Value Required INTERFACE (\S+)
Value Required REMOTE_ID (\d+)
Value Required CHASSIS_ID (\S+)
Value Required PORT_ID (\S+)
Value HOST_NAME (\S+)

Start
  ^LLDP Remote Device Summary
  ^Local
  ^Interface\s+RemID\s+Chassis ID\s+Port ID\s+System Name
  ^---------\s+-------\s+-------------------\s+-----------------\s+-----------------
  ^${INTERFACE}\s+${REMOTE_ID}\s+${CHASSIS_ID}\s+${PORT_ID}\s+${HOST_NAME} -> Record
  ^${INTERFACE}\s+${REMOTE_ID}\s+${CHASSIS_ID}\s+${PORT_ID} -> Record
  ^\s*$$ -> Start

EOF
