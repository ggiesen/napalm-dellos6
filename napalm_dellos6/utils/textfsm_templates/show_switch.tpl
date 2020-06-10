Value Required SWITCH (\d+)
Value Required STATUS_MGMT (Stack Mbr|Mgmt Sw)
Value STATUS_STBY (Oper Stby)
Value Required MODEL_ID_ADMIN (\S+)
Value Required MODEL_ID_OPER (\S+)
Value Required STATUS (\S+)
Value VERSION (\S+)

Start
  ^\s+Management\s+Standby\s+Preconfig\s+Plugged-in\s+Switch\s+Code
  ^SW\s+Status\s+Model ID\s+Model ID\s+Status\s+Version
  ^${SWITCH}\s+${STATUS_MGMT}\s+${STATUS_STBY}\s+${MODEL_ID_ADMIN}\s+${MODEL_ID_OPER}\s+${STATUS}\s+${VERSION} -> Record
  ^${SWITCH}\s+${STATUS_MGMT}\s+${MODEL_ID_ADMIN}\s+${MODEL_ID_OPER}\s+${STATUS}\s+${VERSION} -> Record

EOF