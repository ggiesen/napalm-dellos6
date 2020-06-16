Value Required COMMUNITY (\S+)
Value Required MODE (\S+.*\S+)
Value Required VIEW (\S+)
Value Required ACL (\S+)

Start
  ^Community-String\s+Community-Access\s+View Name\s+IP Address -> Community

Community
  ^--------------------\s+----------------\s+----------------\s+----------------
  ^Community-String\s+Group Name\s+IP Address -> End
  ^${COMMUNITY}\s+${MODE}\s+${VIEW}\s+${ACL} -> Record
  ^\s*$$ -> End

EOF