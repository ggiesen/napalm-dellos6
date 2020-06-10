Value MACHINE_DESC (.*)
Value MODEL (\S+)
Value MACHINE_TYPE (.*)
Value SERIAL_NUM (\S+)
Value MANUFACTURER (\S+)
Value MAC_ADDR (\S+)
Value SYS_OBJ_ID (\S+)
Value CPU_VER (\S+)
Value SOC_VER (\S+)
Value HW_VER (\d+)
Value CPLD_VER (\d+)

Start
  ^Machine Description\.+ ${MACHINE_DESC}
  ^System Model ID\.+ ${MODEL}
  ^Machine Type\.+ ${MACHINE_TYPE}
  ^Serial Number\.+ ${SERIAL_NUM}
  ^Manufacturer\.+ ${MANUFACTURER}
  ^Burned In MAC Address\.+ ${MAC_ADDR}
  ^System Object ID\.+ ${SYS_OBJ_ID}
  ^CPU Version\.+ ${CPU_VER}
  ^SOC Version\.+ ${SOC_VER}
  ^HW Version\.+ ${HW_VER}
  ^CPLD Version\.+ ${CPLD_VER} -> Record

EOF