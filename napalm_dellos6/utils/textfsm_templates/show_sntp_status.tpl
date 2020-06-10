Value Required SERVER_IP (\S+)
Value Required STATUS (\S.*\S)
Value Required LAST_RESPONSE (\d+\:\d+:\d+ \S+ \d+ \d+)

Start
  ^Unicast servers\: -> Unicast

Unicast
  ^Server\s+Status\s+Last response
  ^---------------\s+----------------------\s+--------------------------
  ^${SERVER_IP}\s+${STATUS}\s+${LAST_RESPONSE} -> Record

EOF