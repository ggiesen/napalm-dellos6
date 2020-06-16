Value Required VRF_NAME (\S+)
Value Required VRF_ID (\d+)

Start
  ^Name\s+Identifier
  ^--------------------\s+---------------
  ^${VRF_NAME}\s+${VRF_ID} -> Record

EOF