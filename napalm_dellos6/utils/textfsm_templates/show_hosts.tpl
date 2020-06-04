Value HOST_NAME (\S+)
Value DOMAIN (\S+)

Start
  ^Host name\: ${HOST_NAME}
  ^Default domain\: ${DOMAIN}