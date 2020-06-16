Value Required USERNAME (\S+)
Value Required PRIV (\d+)
Value Required PWD_AGING (\S+)
Value Required PWD_EXPIRY (\S+)
Value Required LOCKOUT (True|False)
Value List ADMIN_PROFILES (\S+\s*\S+)

Start
  ^\s*UserName\s+Privilege\s+Password\s+Password\s+Lockout
  ^\s*Aging\s+Expiry date
  ^------------------------\s+---------\s+--------\s+--------------------\s+--------
  ^${USERNAME}\s+${PRIV}\s+${PWD_AGING}\s+${PWD_EXPIRY}\s+${LOCKOUT}
  ^\s*Administrative Profile\(s\)\:\s*${ADMIN_PROFILES} -> Record
  ^\s*Administrative Profile\(s\)\: -> Record
  ^. -> Error

EOF