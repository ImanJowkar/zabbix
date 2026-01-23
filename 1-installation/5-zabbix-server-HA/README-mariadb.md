# Setup zabbix server HA

`all of below server is ubuntu 22 LTS`
* zbx-srv1    192.168.229.171
* zbx-srv2    192.168.229.172
* zbx-db     192.168.229.173
* zbx-web      192.168.229.174


## zbx-srv1
```

apt install zabbix-server-mysql zabbix-agent




```




## zbx-srv2
```

apt install zabbix-server-mysql  zabbix-agent




```






## zbx-web
```sh

apt install  zabbix-frontend-php zabbix-nginx-conf

sudo vim /etc/zabbix/nginx.conf
---------------------------
# listen 8080;
# server_name example.com;
----------------------------

sudo nginx -t
sudo nginx -s reload

```

## zbx-db
[ref](https://www.digitalocean.com/community/tutorials/how-to-install-mariadb-on-ubuntu-22-04)
```sh
apt install zabbix-sql-scripts


sudo apt install mariadb-server
sudo mysql_secure_installation


# change list address to `0.0.0.0` in /etc/mysql/mariadb.conf.d/50-server.cnf

mysql -uroot -p

create database zabbix character set utf8mb4 collate utf8mb4_bin;

# for zbx-srv1
create user zabbix@'192.168.229.171' identified by 'password';
grant all privileges on zabbix.* to zabbix@'192.168.229.171';

# for zbx-srv2
create user zabbix@'192.168.229.172' identified by 'password';
grant all privileges on zabbix.* to zabbix@'192.168.229.172';

# for web
create user zabbix@'192.168.229.174' identified by 'password';
grant all privileges on zabbix.* to zabbix@'192.168.229.174';


create user zabbix@localhost identified by 'password';
grant all privileges on zabbix.* to zabbix@localhost;




set global log_bin_trust_function_creators = 1;
quit;


zcat /usr/share/zabbix-sql-scripts/mysql/server.sql.gz | mysql --default-character-set=utf8mb4 -uzabbix -p zabbix



mysql -uroot -p

set global log_bin_trust_function_creators = 0;
quit;




select * from ha_node;

```




## zbx-srv1

```sh
vim /etc/zabbix/zabbix_server.conf
--------------
DBHost=192.168.229.173
DBName=zabbix
DBUser=zabbix
DBPassword=password


HANodeName=zbx-srv1
NodeAddress=192.168.229.171:10051
---------------


systemctl restart zabbix-server.service

```


## zbx-srv2

```sh
vim /etc/zabbix/zabbix_server.conf
--------------
DBHost=192.168.229.173
DBName=zabbix
DBUser=zabbix
DBPassword=password


HANodeName=zbx-srv2
NodeAddress=192.168.229.172:10051
---------------


systemctl restart zabbix-server.service

```


