Value Required PEER_ADDR (\S+)
Value Required PEER_AS (\d+)
Value Required PEER_ID (\S+)
Value Required PEER_STATUS_ADMIN (\S+)
Value Required PEER_STATE (\S+)
Value Required LOCAL_ADDR (\S+)
Value Required LOCAL_PORT (\d+)
Value Required PEER_PORT (\d+)
Value Required RETRY_INT (\d+)
Value Required PEER_CAPAB (\S+.*\S+)
Value Required NHS (\S+)
Value Required IPV4_UCAST (\S+.*\S+)
Value Required IPV6_UCAST (\S+.*\S+)
Value Required TEMPLATE (\S+)
Value UPD_SRC (\S+)
Value Required HOLD_TIME_ADMIN (\S+)
Value Required KEEPALIVE_ADMIN (\S+)
Value HOLD_TIME_OPER (\S+)
Value KEEPALIVE_OPER (\S+)
Value Required PFX_LIMIT (None|\d+)
Value Required PFX_WARNING (\d+)
Value Required PFX_WARN_ONLY (\S+)
Value Required MD5 (\S+)
Value Required ORIG_DEFAULT (\S+)
Value Required ERROR_LAST (\S+)
Value Required SUBERROR_LAST (\S+)
Value Required TIME_SINCE_ERROR (\S+)
Value Required ESTAB_TRANS (\d+)
Value Required ESTAB_TIME (\S+)
Value Required UPD_TIME (\S+)
Value Required UPD_GROUP (None|\d+)
Value Required MSG_TX_OPEN (\d+)
Value Required MSG_TX_UPD (\d+)
Value Required MSG_TX_KEEPALIVE (\d+)
Value Required MSG_TX_NOTIF (\d+)
Value Required MSG_TX_REFRESH (\d+)
Value Required MSG_TX_TOTAL (\d+)
Value Required MSG_RX_OPEN (\d+)
Value Required MSG_RX_UPD (\d+)
Value Required MSG_RX_KEEPALIVE (\d+)
Value Required MSG_RX_NOTIF (\d+)
Value Required MSG_RX_REFRESH (\d+)
Value Required MSG_RX_TOTAL (\d+)
Value Required QUEUE_SIZE (\d+)
Value Required QUEUE_MAX (\d+)
Value Required QUEUE_LIMIT (\d+)
Value Required QUEUE_DROPS (\d+)
Value IPV4_PFX_ADV_RX (\d+)
Value IPV4_PFX_ADV_TX (\d+)
Value IPV4_PFX_WITHDRAWN_RX (\d+)
Value IPV4_PFX_WITHDRAWN_TX (\d+)
Value IPV4_PFX_CURRENT_RX (\d+)
Value IPV4_PFX_CURRENT_TX (\d+)
Value IPV4_PFX_ACCEPT_RX (\d+)
Value IPV4_PFX_REJECT_RX (\d+)
Value IPV4_NLRI_MAX_RX (\d+)
Value IPV4_NLRI_MAX_TX (\d+)
Value IPV4_NLRI_MIN_RX (\d+)
Value IPV4_NLRI_MIN_TX (\d+)
Value IPV6_PFX_ADV_RX (\d+)
Value IPV6_PFX_ADV_TX (\d+)
Value IPV6_PFX_WITHDRAWN_RX (\d+)
Value IPV6_PFX_WITHDRAWN_TX (\d+)
Value IPV6_PFX_CURRENT_RX (\d+)
Value IPV6_PFX_CURRENT_TX (\d+)
Value IPV6_PFX_ACCEPT_RX (\d+)
Value IPV6_PFX_REJECT_RX (\d+)
Value IPV6_NLRI_MAX_RX (\d+)
Value IPV6_NLRI_MAX_TX (\d+)
Value IPV6_NLRI_MIN_RX (\d+)
Value IPV6_NLRI_MIN_TX (\d+)

Start
  ^Remote Address\s*\.+\s -> Continue.Record
  ^Remote Address\s*\.+\s*${PEER_ADDR}
  ^Remote AS\s*\.+\s*${PEER_AS}
  ^Peer ID\s*\.+\s*${PEER_ID}
  ^Peer Admin Status\s*\.+\s*${PEER_STATUS_ADMIN}
  ^Peer State\s*\.+\s*${PEER_STATE}
  ^Local Interface Address\s*\.+\s*${LOCAL_ADDR}
  ^Local Port\s*\.+\s*${LOCAL_PORT}
  ^Remote Port\s*\.+\s*${PEER_PORT}
  ^Connection Retry Interval\s*\.+\s*${RETRY_INT}\s+sec
  ^Neighbor Capabilities\s*\.+\s*${PEER_CAPAB}
  ^Next Hop Self\s*\.+\s*${NHS}
  ^IPv4 Unicast Support\s*\.+\s*${IPV4_UCAST}
  ^IPv6 Unicast Support\s*\.+\s*${IPV6_UCAST}
  ^Template Name\s*\.+\s*${TEMPLATE}
  ^Update Source\s*\.+\s*${UPD_SRC}
  ^Configured Hold Time\s*\.+\s*${HOLD_TIME_ADMIN}
  ^Configured Keep Alive Time\s*\.+\s*${KEEPALIVE_ADMIN}
  ^Negotiated Hold Time\s*\.+\s*${HOLD_TIME_OPER}
  ^Keep Alive Time\s*\.+\s*${KEEPALIVE_OPER}
  ^Prefix Limit\s*\.+\s*${PFX_LIMIT}
  ^Prefix Warning Threshold\s*\.+\s*${PFX_WARNING}
  ^Warning Only On Prefix Limit\s*\.+\s*${PFX_WARN_ONLY}
  ^MD5 Password\s*\.+\s*${MD5}
  ^Originate Default\s*\.+\s*${ORIG_DEFAULT}
  ^Last Error \(Sent\)\s*\.+\s*${ERROR_LAST}
  ^Last SubError\s*\.+\s*${SUBERROR_LAST}
  ^Time Since Last Error\s*\.+\s*${TIME_SINCE_ERROR}
  ^Established Transitions\s*\.+\s*${ESTAB_TRANS}
  ^Established Time\s*\.+\s*${ESTAB_TIME}
  ^Time Since Last Update\s*\.+\s*${UPD_TIME}
  ^IPv4 Outbound Update Group\s*\.+\s*${UPD_GROUP}
  ^\s+Open\s+Update\s+Keepalive\s+Notification\s+Refresh\s+Total
  ^Msgs Sent\s+${MSG_TX_OPEN}\s+${MSG_TX_UPD}\s+${MSG_TX_KEEPALIVE}\s+${MSG_TX_NOTIF}\s+${MSG_TX_REFRESH}\s+${MSG_TX_TOTAL}
  ^Msgs Rcvd\s+${MSG_RX_OPEN}\s+${MSG_RX_UPD}\s+${MSG_RX_KEEPALIVE}\s+${MSG_RX_NOTIF}\s+${MSG_RX_REFRESH}\s+${MSG_RX_TOTAL}
  ^Received UPDATE Queue Size\:\s+${QUEUE_SIZE}\s+bytes\.\s+High\:\s+${QUEUE_MAX}\s+Limit\:\s+${QUEUE_LIMIT}\s+Drops\:\s+${QUEUE_DROPS}
  ^IPv4 Prefix Statistics\: -> IPV4Prefixes
  ^IPv6 Prefix Statistics\: -> IPV6Prefixes
  ^. -> Error

IPV4Prefixes
  ^\s+Inbound\s+Outbound
  ^Prefixes Advertised\s+${IPV4_PFX_ADV_RX}\s+${IPV4_PFX_ADV_TX}
  ^Prefixes Withdrawn\s+${IPV4_PFX_WITHDRAWN_RX}\s+${IPV4_PFX_WITHDRAWN_TX}
  ^Prefixes Current\s+${IPV4_PFX_CURRENT_RX}\s+${IPV4_PFX_CURRENT_TX}
  ^Prefixes Accepted\s+${IPV4_PFX_ACCEPT_RX}\s+N\/A
  ^Prefixes Rejected\s+${IPV4_PFX_REJECT_RX}\s+N\/A
  ^Max NLRI per Update\s+${IPV4_NLRI_MAX_RX}\s+${IPV4_NLRI_MAX_TX}
  ^Min NLRI per Update\s+${IPV4_NLRI_MIN_RX}\s+${IPV4_NLRI_MIN_TX} -> Start
  ^. -> Error

IPV6Prefixes
  ^\s+Inbound\s+Outbound
  ^Prefixes Advertised\s+${IPV6_PFX_ADV_RX}\s+${IPV6_PFX_ADV_TX}
  ^Prefixes Withdrawn\s+${IPV6_PFX_WITHDRAWN_RX}\s+${IPV6_PFX_WITHDRAWN_TX}
  ^Prefixes Current\s+${IPV6_PFX_CURRENT_RX}\s+${IPV6_PFX_CURRENT_TX}
  ^Prefixes Accepted\s+${IPV6_PFX_ACCEPT_RX}\s+N\/A
  ^Prefixes Rejected\s+${IPV6_PFX_REJECT_RX}\s+N\/A
  ^Max NLRI per Update\s+${IPV6_NLRI_MAX_RX}\s+${IPV6_NLRI_MAX_TX}
  ^Min NLRI per Update\s+${IPV6_NLRI_MIN_RX}\s+${IPV6_NLRI_MIN_TX} -> Start
  ^. -> Error
