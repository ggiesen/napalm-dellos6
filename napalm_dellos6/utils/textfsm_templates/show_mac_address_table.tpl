Value Required VLAN (\d+)
Value Required MAC (\S+)
Value Required TYPE (Dynamic|Static|Management)
Value Required PORT (\S+)

Start
  ^Vlan\s+Mac Address\s+Type\s+Port -> MacAddressTable

MacAddressTable
  ^--------\s+---------------------\s+-----------\s+---------------------
  ^${VLAN}\s+${MAC}\s+${TYPE}\s+${PORT} -> Record

EOF
