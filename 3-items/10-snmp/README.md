# SNMP
[mib-browser-site](https://mibbrowser.online/mibdb_search.php)

```sh
# you can install snmp-walk for testing and getting your snmp OID information from devices

dnf install net-snmp-libs net-snmp-utils

dnf install nmap

# check udp port
nc -uz 10.10.10.1 161
echo $? # if 0 port open, if 1 port closed

snmpwalk -v 2c -c iman 10.10.10.1:161
snmpwalk -On -v 2c -c iman 10.10.10.1:161  # don't translate with mib

snmpwalk -v 2c -c iman 192.168.85.6:161  1.3.6.1.2.1.2 

snmpwalk -v 2c -c iman 192.168.85.6:161 > file.txt
snmpwalk -v 2c -c iman 192.168.85.6:161 DISMAN-EVENT-MIB::sysUpTimeInstance -On










# monitor cisco device
# read-only
snmp-server community iman ro

# if you want to restrict the ip
ip access-list standard snmp-acl
permit 192.168.85.170
exit
snmp-server community iman ro snmp-acl

# you can define multiple community-string , one of them is readonly and another is read-write
snmp-server community iman-readonly ro
snmp-server community iman-readwrite rw




```
