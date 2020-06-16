Value CONTACT (\S+.*\S+)
Value LOCATION (\S+.*\S+)

Start
  ^System Contact\:\s*${CONTACT} -> Record
  ^System Location\:\s*${LOCATION} -> Record

EOF