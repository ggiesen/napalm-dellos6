Value UNIT (\d+)
Value DESCRIPTION (\S.*\S)
Value STATUS (\S+)

Start
  ^Fans\: -> Fans

Fans
  ^Unit\s+Description\s+Status
  ^----\s+-----------\s+------
  ^${UNIT}\s+${DESCRIPTION}\s+${STATUS} -> Record
  ^Power Supplies\: -> End
  ^. -> Error

EOF