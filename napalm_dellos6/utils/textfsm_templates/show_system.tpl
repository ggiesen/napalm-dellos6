Value SYS_DESC (.*)
Value UPTIME (.*)
Value SYS_CONTACT (.*)
Value SYS_NAME (\S+)
Value SYS_LOC (.*)
Value MAC_ADDR (\S+)
Value SYS_OBJ_ID (\S+)
Value MODEL (\S+)
Value MACHINE_TYPE (.*)

Start
  ^System Description\: ${SYS_DESC}
  ^System Up Time\: ${UPTIME}
  ^System Contact\: ${SYS_CONTACT}
  ^System Name\: ${SYS_NAME}
  ^System Location\: ${SYS_LOC}
  ^Burned In MAC Address\: ${MAC_ADDR}
  ^System Object ID\: ${SYS_OBJ_ID}
  ^System Model ID\: ${MODEL}
  ^Machine Type\: ${MACHINE_TYPE}