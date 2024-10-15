## enable snmp on cisco devices

```
ip access-list standard snmp-acl
permit 10.10.10.254
exit
snmp-server community iman ro snmp-acl

```