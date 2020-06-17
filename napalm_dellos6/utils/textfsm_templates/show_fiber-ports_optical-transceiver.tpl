Value Required INT_NAME (\S+)
Value TEMP (\S+)
Value VOLTAGE (\S+)
Value CURRENT (\S+)
Value PWR_TX (\S+)
Value PWR_RX (\S+)
Value FAULT_TX (\S+)
Value LOS (\S+)

Start
  ^\s+Output\s+Input
  ^Port\s+Temp\s+Voltage\s+Current\s+Power\s+Power\s+TX\s+LOS
  ^\s+\[C\]\s+\[Volt\]\s+\[mA\]\s+\[dBm\]\s+\[dBm\]\s+Fault
  ^---------\s+----\s+-------\s+-------\s+-------\s+-------\s+-----\s+---
  ^${INT_NAME}\s+${TEMP}\s+${VOLTAGE}\s+${CURRENT}\s+${PWR_TX}\s+${PWR_RX}\s+${FAULT_TX}\s+${LOS} -> Record
  ^. -> Error

EOF