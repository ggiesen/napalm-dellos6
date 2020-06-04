Value Required INTERFACE (\S+)
Value Required STATE (\S+)
Value Required IP_ADDRESS (\S+)
Value Required SUBNET_MASK (\S+)
Value Required METHOD (\S+)

Start
  ^Routing Interfaces\: -> RoutingInterfaces

RoutingInterfaces
  ^Interface\s+State\s+IP Address\s+IP Mask\s+Method
  ^----------\s+-----\s+---------------\s+---------------\s+-------
  ^${INTERFACE}\s+${STATE}\s+${IP_ADDRESS}\s+${SUBNET_MASK}\s+${METHOD} -> Continue.Record

EOF