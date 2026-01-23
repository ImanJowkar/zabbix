# database

```sh

vim /var/lib/pgsql/18/data/pg_hba.conf
----
host    zabbix             zabbix             192.168.85.91/32            scram-sha-256
host    zabbix             zabbix             192.168.85.92/32            scram-sha-256
----

listen_addresses = '192.168.85.90'              # what IP address(es) to listen on;

sudo -u postgres createuser --pwprompt zabbix
echo $?
sudo -u postgres createdb -O zabbix zabbix
echo $?
zcat /usr/share/zabbix-sql-scripts/postgresql/server.sql.gz | sudo -u zabbix psql zabbix


```


# zbx-srv1
```sh
vim /etc/zabbix/zabbix-server.conf
-----
DBHost=192.168.85.90
DBPassword=iman
DBName=zabbix
DBUser=zabbix


HANodeName=zbx-srv1
NodeAddress=192.168.85.91:10051
-----





```


# zbx-srv2
```sh

vim /etc/zabbix/zabbix-server.conf
-----
DBHost=192.168.85.90
DBPassword=iman
DBName=zabbix
DBUser=zabbix


HANodeName=zbx-srv2
NodeAddress=192.168.85.92:10051
-----


```