Value Required INTERFACE (\S+)
Value REMOTE_ID (\d+)
Value CHASSIS_ID_SUBTYPE (\S+)
Value CHASSIS_ID (\S+)
Value PORT_ID_SUBTYPE (\S+)
Value PORT_ID (\S+)
Value HOST_NAME (\S+)
Value PORT_DESC (.*)
Value SYS_CAP_SUP (.*)
Value SYS_CAP_OPER (.*)

Start
  ^LLDP Remote Device Detail
  ^Local Interface\:\s+${INTERFACE}
  ^Remote Identifier\:\s+${REMOTE_ID}
  ^Chassis ID Subtype\:\s+${CHASSIS_ID_SUBTYPE}
  ^Chassis ID\:\s+${CHASSIS_ID}
  ^Port ID Subtype\:\s+${PORT_ID_SUBTYPE}
  ^Port ID\:\s+${PORT_ID}
  ^System Name\:\s+${HOST_NAME}
  ^Port Description:\s+${PORT_DESC}
  ^System Capabilities Supported\:\s+${SYS_CAP_SUP}
  ^System Capabilities Enabled\:\s+${SYS_CAP_OPER} -> Record

EOF
