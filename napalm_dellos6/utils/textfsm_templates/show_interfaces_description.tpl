Value Required INTERFACE (\S+)
Value DESC ((\S.*\S)*)

Start
  ^Port\s+Description -> Port
  
Port
  ^---------\s+--------------------------------------------------------------------------
  ^${INTERFACE}\s+${DESC} -> Record
  ^\s*$$ -> Record Start

EOF
