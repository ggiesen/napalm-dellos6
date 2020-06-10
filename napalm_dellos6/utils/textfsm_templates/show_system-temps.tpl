Value UNIT (\d+)
Value DESCRIPTION (\S.*\S)
Value TEMP (\d+)

Start
  ^Temperature Sensors\: -> TempSensors

TempSensors
  ^Unit\s+Description\s+Temperature
  ^\s+\(Celsius\)
  ^----\s+------------------\s+-----------
  ^${UNIT}\s+${DESCRIPTION}\s+${TEMP} -> Record
  ^Fans\: -> End
  ^. -> Error

EOF