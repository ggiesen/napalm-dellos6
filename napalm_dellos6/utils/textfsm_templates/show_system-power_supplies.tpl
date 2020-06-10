Value Required UNIT (\d+)
Value Required DESCRIPTION (\S.*\S)
Value Required STATUS (\S+)
Value Required PWR_AVG (\d+\.\d)
Value Required PWR_CUR (\d+\.\d)
Value START_TIME (.*)

Start
  ^Power Supplies\: -> PowerSupplies

PowerSupplies
  ^Unit\s+Description\s+Status\s+Average\s+Current\s+Since
  ^\s+Power\s+Power\s+Date\/Time
  ^\s+\(Watts\)\s+\(Watts\)
  ^----\s+-----------\s+-----------\s+----------\s+--------\s+-------------------
  ^${UNIT}\s+${DESCRIPTION}\s+${STATUS}\s+${PWR_AVG}\s+${PWR_CUR}\s*${START_TIME} -> Record
  ^USB Port Power Status\: -> End
  ^. -> Error

EOF