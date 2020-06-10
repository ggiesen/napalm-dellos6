Value Required IP_ADDRESS (\S+)
Value Required MAC_ADDRESS (\S+)
Value Required INTERFACE (\S+)
Value Required TYPE (\S+)
Value Required AGE (\S.*\S)

Start
  ^IP Address\s+MAC Address\s+Interface\s+Type\s+Age -> ARPTable

ARPTable
  ^---------------\s+-----------------\s+--------------\s+--------\s+-----------
  ^${IP_ADDRESS}\s+${MAC_ADDRESS}\s+${INTERFACE}\s+${TYPE}\s+${AGE} -> Record
  ^. -> Error

EOF