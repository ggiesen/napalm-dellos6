Value Required INTERFACE (\S+)
Value DESC ((\S.*\S)*)
Value DUPLEX (Full|Half|N\/A)
Value SPEED (Unknown|\d+)
Value NEG (\S+)
Value MTU (\d+)
Value Required ADMIN_STATE (\S+)
Value TYPE (\S+)

Start
  ^Port\s+Description\s+Duplex\s+Speed\s+Neg\s+MTU\s+Admin -> Port
  ^Oob\s+Type\s+Link -> Oob
  ^Port\s+Description\s+MTU\s+Admin -> PortChannel
  
Port
  ^\s+State
  ^---------\s+------------------------------\s+------\s+-------\s+----\s+-----\s+-----
  ^${INTERFACE}\s+${DESC}\s+${DUPLEX}\s+${SPEED}\s+${NEG}\s+${MTU}\s+${ADMIN_STATE} -> Continue.Record
  ^\s*$$ -> Record Start

Oob
  ^\s+State
  ^---\s+------------------------------\s+-----
  ^${INTERFACE}\s+${TYPE}\s+${ADMIN_STATE} -> Continue.Record
  ^\s*$$ -> Record Start

PortChannel
  ^Channel\s+State
  ^-------\s+------------------------------\s+-------\s+--\s+-------------------
  ^${INTERFACE}\s+${DESC}\s+${MTU}\s+${ADMIN_STATE} -> Continue.Record
  ^\r\n - > Record Start

EOF
