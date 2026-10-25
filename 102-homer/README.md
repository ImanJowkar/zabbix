## command

```sh

asterisk -rx "module show like chan_sip"
asterisk -rx "module show like res_pjsip"



asterisk -rx "sip show peers"
asterisk -rx "pjsip show endpoints"


asterisk -rx "core show version"

ip -br addr
asterisk -rx "sip show settings" | grep -i "bind"




```