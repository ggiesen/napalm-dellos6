Value Required INTERFACE (\S+)
Value DESC (.*)

Start
  ^Port\s+Description -> Port
  
Port
  ^---------\s+--------------------------------------------------------------------------
  ^${INTERFACE}\s+${DESC} -> Record.Continue
  ^\s*$$ -> Record Start

EOF
