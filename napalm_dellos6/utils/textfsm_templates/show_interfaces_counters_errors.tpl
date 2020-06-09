Value Required INTERFACE (\S+)
Value IN_ALIGN (\d+)
Value IN_FCS (\d+)
Value OUT_TOTAL (\d+)
Value IN_TOTAL (\d+)
Value IN_UNDERSIZE (\d+)
Value OUT_DISCARD (\d+)

Start
  ^Port\s+Align-Err\s+FCS-Err\s+Xmit-Err\s+Rcv-Err\s+UnderSize\s+OutDiscard -> Port
  ^Channel\s+Align-Err\s+FCS-Err\s+Xmit-Err\s+Rcv-Err\s+UnderSize\s+OutDiscard -> Port

Port
  ^Port
  ^---------\s+----------\s+----------\s+----------\s+----------\s+----------\s+----------
  ^${INTERFACE}\s+${IN_ALIGN}\s+${IN_FCS}\s+${OUT_TOTAL}\s+${IN_TOTAL}\s+${IN_UNDERSIZE}\s+${OUT_DISCARD} -> Record
  ^\s*$$ -> Start

EOF