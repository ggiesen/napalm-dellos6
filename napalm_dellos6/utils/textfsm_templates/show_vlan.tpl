Value Required VLAN_ID (\d+)
Value VLAN_NAME ((\S+(\s*\S))+)
Value List PORTS (\S+)
Value VLAN_TYPE (\S+)

Start
  ^VLAN\s+Name\s+Ports\s+Type -> VLans

VLans
  ^-----\s+---------------\s+-------------\s+--------------
  ^${VLAN_ID}\s+${VLAN_NAME}\s+${PORTS}\,\s+${VLAN_TYPE} -> ExtraPorts
  ^${VLAN_ID}\s+${VLAN_NAME}\s+${PORTS}\s+${VLAN_TYPE} -> Record
  ^. -> Error

ExtraPorts
  ^\s+${PORTS}\, -> ExtraPorts
  ^\s+${PORTS} -> Record VLans

EOF
