## enable snmp on cisco devices

```
ip access-list standard snmp-acl
permit 10.10.10.254
exit
snmp-server community iman ro snmp-acl

```

## snmp trap 
[ref](https://sbcode.net/zabbix/snmp-traps/)
```



vim /etc/zabbix/zabbix_server.conf
# add below 
--------------------
SNMPTrapperFile=/tmp/zabbix_traps.tmp
StartSNMPTrapper=1
-----------------

# install perl
apt-get install perl libxml-simple-perl libsnmp-perl


sudo wget https://git.zabbix.com/projects/ZBX/repos/zabbix/raw/misc/snmptrap/zabbix_trap_receiver.pl -O /usr/bin/zabbix_trap_receiver.pl
sudo chmod a+x /usr/bin/zabbix_trap_receiver.pl

sudo apt install snmp snmp-mibs-downloader snmptrapd

sudo nano /etc/snmp/snmptrapd.conf
-----------------------

authCommunity execute iman
perl do "/usr/bin/zabbix_trap_receiver.pl";


---------------------

sudo systemctl restart snmptrapd.service


netstat -ntlu
udp        0      0 0.0.0.0:162             0.0.0.0:*
udp        0      0 127.0.0.1:323           0.0.0.0:*
udp6       0      0 :::514                  :::*
udp6       0      0 ::1:161                 :::*
udp6       0      0 :::162                  :::*
udp6       0      0 ::1:323 




sudo nano /etc/snmp/snmp.conf
-----------
# mibs :
-----------

sudo systemctl restart snmptrapd.service
```


on cisco devices
```
ip access-list standard snmp-acl
permit 10.10.10.254
exit
snmp-server community iman ro snmp-acl


## trap
snmp-server host 192.168.40.10 version 2c iman
snmp-server enable trap


### trap inform
snmp-server host 192.168.40.10 informs version 2c iman
```
