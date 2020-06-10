Value MEM_ALLOC (\d+)
Value MEM_FREE (\d+)
Value CPU_5 ([\d\.]+)
Value CPU_60 (\d+\.\d\d)
Value CPU_300 (\d+\.\d\d)

Start
  ^Memory Utilization Report -> Memory
  ^CPU Utilization\: -> CPU

Memory
  ^status\s+KBytes
  ^------\s+----------
  ^free\s+${MEM_FREE}
  ^alloc\s+${MEM_ALLOC} -> Start

CPU
  ^Total CPU Utilization\s+${CPU_5}%\s+${CPU_60}%\s+${CPU_300}% -> Record

EOF