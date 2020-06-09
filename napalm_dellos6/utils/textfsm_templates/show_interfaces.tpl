Value Required INTERFACE (\S+)
Value Required SOC (\S+)
Value Required LINK_STATE (Up|Down)
Value Required MODE (\S+)
Value Required VLAN (\S+)
Value Required MTU (\d+)
Value Required DUPLEX (Full|Half|N\/A)
Value Required SPEED (Unknown|\d+)
Value Required NEG (\S+)
Value Required MAC_ADDRESS (\S+)

Start
  ^Interface Name\s*\:\s*\.* ${INTERFACE}
  ^SOC Hardware Info\s*\:\s*\.* ${SOC}
  ^Link Status\s*\:\s*\.* ${LINK_STATE}
  ^VLAN Membership Mode\s*\:\s*\.* ${MODE}
  ^VLAN Membership\s*\:\s*\.* ${VLAN}
  ^MTU Size\s*\:\s*\.* ${MTU}
  ^Port Mode \[Duplex\]\s*\:\s*\.* ${DUPLEX}
  ^Port Speed\s*\:\s*\.* ${SPEED}
  ^Auto-Negotation Status\s*:\s*\.* ${NEG}
  ^Burned MAC Address\s*\:\s*\.* ${MAC_ADDRESS}
  ^\s*$$ -> Record Start

EOF