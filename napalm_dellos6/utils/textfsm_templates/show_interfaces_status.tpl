Value Required INTERFACE (\S+)
Value DESC (.*)
Value DUPLEX (Full|Half|N\/A)
Value SPEED (N\/A|Unknown|\d+)
Value NEG (\S+)
Value Required LINK_STATE (\S+)
Value FLOW_CONTROL (\S+)
Value MODE (\S)
Value VLAN (\S+)
Value TYPE (\S+)

Start
  ^Port\s+Description\s+Duplex\s+Speed\s+Neg\s+Link\s+Flow\s+M\s+VLAN -> Port
  ^Oob\s+Type\s+Link -> Oob
  ^Port\s+Description\s+Link\s+M\s+VLAN -> PortChannel
  
Port
  ^\s+State\s+Ctrl
  ^---------\s+---------------\s+------\s+-------\s+----\s+------\s+-----\s+--\s+-------------------
  ^${INTERFACE}\s+${DESC}\s+${DUPLEX}\s+${SPEED}\s+${NEG}\s+${LINK_STATE}\s+${FLOW_CONTROL}\s*${MODE}\s*${VLAN} -> Continue.Record
  ^\s*$$ -> Record Start

Oob
  ^\s+State
  ^---\s+------------------------------\s+-----
  ^${INTERFACE}\s+${TYPE}\s+${LINK_STATE} -> Continue.Record
  ^\s*$$ -> Record Start

PortChannel
  ^Channel\s+State
  ^-------\s+------------------------------\s+-------\s+--\s+-------------------
  ^${INTERFACE}\s+${DESC}\s+${LINK_STATE}\s+${MODE}\s+${VLAN} -> Continue.Record
  ^\r\n - > Record Start

EOF
