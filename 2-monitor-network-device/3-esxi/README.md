## how to monitor esxi with zabbix


```sh

# vim /etc/zabbix/zabbix_server.conf # or zabbix proxy
vim /etc/zabbix/zabbix_proxy.conf
-----

StartVMwareCollectors=5
VMwareCacheSize=256M
VMwarePerfFrequency=60
VMwareFrequency=60
VMwareTimeout=10

-----






```