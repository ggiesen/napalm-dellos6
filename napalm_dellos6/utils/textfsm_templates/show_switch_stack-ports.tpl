Value Required INTERFACE (\S+)
Value Required ADMIN_STACK_MODE (\S+)
Value Required OPER_STACK_MODE (\S+)
Value Required LINK_STATE (\S.*\S)
Value Required SPEED (Unknown|\d+)
Value Required ADMIN_STATE (\S+)

Start
  ^\s*Configured\s+Running\s+Link\s+Link\s+Admin
  ^Interface\s+Stack Mode\s+Stack Mode\s+Status\s+Speed \(Gb\/s\)\s+Status
  ^---------\s+----------\s+----------\s+------------\s+------------\s+------------
  ^${INTERFACE}\s+${ADMIN_STACK_MODE}\s+${OPER_STACK_MODE}\s+${LINK_STATE}\s+${SPEED}\s+${ADMIN_STATE} -> Continue.Record
  ^\s*$$ -> Record Start

EOF
