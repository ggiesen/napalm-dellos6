Value Required VRF_NAME (\S+)
Value Required INT_NAME (\S+)
Value Required STATE (\S+)
Value Required IP_ADDRESS (\S+)
Value Required SUBNET_MASK (\S+)
Value Required METHOD (\S+)

Start
  ^VRF Name\s+Interface\s+State\s+IP Address\s+IP Mask\s+Method
  ^--------------------\s+----------\s+-----\s+---------------\s+---------------\s+-------
  ^${VRF_NAME}\s+${INT_NAME}\s+${STATE}\s+${IP_ADDRESS}\s+${SUBNET_MASK}\s+${METHOD} -> Record

EOF