Value Required INTERFACE (\S+)
Value Required DUPLEX (Full|Half|N\/A)
Value Required SPEED (Unknown|\d+)
Value Required NEG (\S+)
Value Required MTU (\d+)
Value Required ADMIN_STATE ([Uu]p|[Dd]own)
Value Required LINK_STATE ([Uu]p|[Dd]own)
Value DESC (.*)

Start
  ^Port\s+Description\s+Duplex\s+Speed\s+Neg\s+MTU\s+Admin\s+Link -> Basic
  ^Port\s+Description -> Description

Basic
  ^\s+State\s+State
  ^---------\s+---------------------------\s+------\s+-------\s+----\s+-----\s+-----\s+-----
  ^${INTERFACE}\s+.*\s+${DUPLEX}\s+${SPEED}\s+${NEG}\s+${MTU}\s+${ADMIN_STATE}\s+${LINK_STATE}
  ^\s*$$ -> Start

Description
  ^---------\s+---------------------------------------------------------------------
  ^\S+\s*${DESC} -> Record
  ^\s*$$ -> Start

EOF