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

# web1
```sh
dnf install -y keepalived



vim /etc/keepalived/keepalived.conf
-----
vrrp_track_process chk_nginx {
      process nginx
      weight 10
}
vrrp_instance ZBX_1 {
        state BACKUP
        interface ens160
        virtual_router_id 51
        priority 243
        advert_int 1
        authentication {
                auth_type PASS
                auth_pass password
        }
        track_process {
                chk_nginx
        }
        virtual_ipaddress {
                192.168.85.100/24
        }
}


-----




firewall-cmd --zone=drop --add-protocol=vrrp --permanent
firewall-cmd --reload


```


# web2
```sh
dnf install -y keepalived


vim /etc/keepalived/keepalived.conf
-----
vrrp_track_process chk_nginx {
      process nginx
      weight 10
}
vrrp_instance ZBX_1 {
        state MASTER
        interface ens160
        virtual_router_id 51
        priority 244
        advert_int 1
        authentication {
                auth_type PASS
                auth_pass password
        }
        track_process {
                chk_nginx
        }
        virtual_ipaddress {
                192.168.85.100/24
        }
}
-----


firewall-cmd --zone=drop --add-protocol=vrrp --permanent
firewall-cmd --reload
```