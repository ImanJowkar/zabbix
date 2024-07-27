## install zabbix proxy

```
sudo apt install sqlite3


```


```
# wget https://repo.zabbix.com/zabbix/7.0/ubuntu/pool/main/z/zabbix-release/zabbix-release_7.0-1+ubuntu20.04_all.deb
# dpkg -i zabbix-release_7.0-1+ubuntu20.04_all.deb
# apt update



apt install zabbix-proxy-sqlite3




vim /etc/zabbix/zabbix_proxy.conf

ProxyMode: 
    0 - proxy in the active mode
    1 - proxy in the passive mode

#### 
# ProxyMode=0
Server=10.10.10.10  # zabbix server ip
Hostname=zbx-proxy
DBName=/tmp/zabbix_proxy.db
####

systemctl restart zabbix-proxy
systemctl enable zabbix-proxy
```