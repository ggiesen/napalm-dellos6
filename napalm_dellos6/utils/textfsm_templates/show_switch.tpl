Value VERSION (\S+)
Value MASTER (\d+)

Start
  ^\s+Management\s+Standby\s+Preconfig\s+Plugged-in\s+Switch\s+Code
  ^SW\s+Status\s+Model ID\s+Model ID\s+Status\s+Version
  ^${MASTER}\s+Mgmt Sw\s+\S+\s+\S+\s+\S+\s+${VERSION}