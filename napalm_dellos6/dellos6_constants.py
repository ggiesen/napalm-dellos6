"""Constants to be used with Dell OS6 driver."""

DELLOS6_SANITIZE_FILTERS = {
    r"^(username\s+\S+\s+password)\s+(\S+)(\s+privilege\s+\d+(\s+encrypted)?)?$": r"\1 <removed>\3",
    r"^(key)\s+\S+$": r"\1 <removed>",
    r"^(snmp-server engineid local).*$": r"\1 <removed>",
    r"^(snmp-server community)\s+\S+(\s*(ro|rw))?$": r"\1 <removed>\2",
    r"^(snmp-server host \S+ traps version (1|2)) \S+(\s+(filter \S+)"
    r"?(udp-port \d+)?)?$": r"\1 <removed>\3",
    r"^(snmp-server host \S+ informs\s*(timeout \d+)?\s*(retries \d+)?)\s*\S+$": r"\1 <removed>",
    r"^(enable\s+password)\s+(\S+)(\s+encrypted)?$": r"\1 <removed>\3",
}
