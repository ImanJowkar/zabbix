# config db - 85.123

```sh

sudo -u postgres createuser --pwprompt zabbix
echo $?
sudo -u postgres createdb -O zabbix zabbix
echo $?
zcat /usr/share/zabbix-sql-scripts/postgresql/server.sql.gz | sudo -u zabbix psql zabbix

vim /var/lib/pgsql/18/data/pg_hba.conf
----
host    zabbix             zabbix             192.168.85.123/32            scram-sha-256  # zbx srv
host    zabbix             zabbix             192.168.85.125/32            scram-sha-256  # zbx web
----
 
vim /var/lib/pgsql/18/data/postgresql.conf
-----
listen_addresses = '192.168.85.124'             # what IP address(es) to listen on;
-----

systemctl restart postgresql-18.service





```


# config srv - 85.124

```sh

vim /etc/zabbix/zabbix-server.conf
-----
DBHost=192.168.85.123
DBPassword=22222
DBName=zabbix
DBUser=zabbix
-----



systemctl start zabbix-agent2.service zabbix-proxy.service zabbix-server.service zabbix-web-service.service
systemctl enable zabbix-agent2.service zabbix-proxy.service zabbix-server.service zabbix-web-service.service



```


# cofig-web  - 85.125
```sh

vim /etc/nginx/conf.d/zabbix.conf
------
        listen          80;
        server_name     192.168.85.125;
------


vim /etc/zabbix/web/zabbix.conf.php
-------
$DB['TYPE']                     = 'POSTGRESQL';
$DB['SERVER']                   = '192.168.85.124';
$DB['PORT']                     = '0';
$DB['DATABASE']                 = 'zabbix';
$DB['USER']                     = 'zabbix';
$DB['PASSWORD']                 = 'iman';


$ZBX_SERVER                     = '192.168.85.123';
$ZBX_SERVER_PORT                = '10051';


-------

systemctl restart nginx

```

# config db timescale - 85.124

```sh
# Configure TimescaleDB
sudo timescaledb-tune --pg-config=/usr/pgsql-18/bin/pg_config

vim /var/lib/pgsql/18/data/postgresql.conf
-----
shared_preload_libraries = 'timescaledb'
-----
sudo systemctl restart postgresql-18.service











```


# Zbx-proxy
```sh

cat >> /etc/yum.repos.d/mariadb.repo <<EOF
# MariaDB 11.4 RedHatEnterpriseLinux repository list - created 2025-05-24 05:38 UTC
# https://mariadb.org/download/
[mariadb]
name = MariaDB
# rpm.mariadb.org is a dynamic mirror if your preferred mirror goes offline. See https://mariadb.org/mirrorbits/ for details.
# baseurl = https://rpm.mariadb.org/11.4/rhel/\$releasever/\$basearch
baseurl = https://mirror.parsvds.com/mariadb/yum/11.4/rhel/\$releasever/\$basearch
# gpgkey = https://rpm.mariadb.org/RPM-GPG-KEY-MariaDB
gpgkey = https://mirror.parsvds.com/mariadb/yum/RPM-GPG-KEY-MariaDB
gpgcheck = 1
EOF


dnf makecache
dnf list | grep MariaDB-server 
sudo dnf install MariaDB-server MariaDB-client
mariadb-secure-installation


mariadb -uroot -p
CREATE DATABASE zabbix_proxy CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;
CREATE USER 'zbxproxy'@'localhost' IDENTIFIED BY 'StrongPassword';

GRANT ALL PRIVILEGES ON zabbix_proxy.* TO 'zbxproxy'@'localhost';
FLUSH PRIVILEGES;

set global log_bin_trust_function_creators = 1;
quit;

cat /usr/share/zabbix-sql-scripts/mysql/server.sql.gz | mysql --default-character-set=utf8mb4 -uzabbix -p zabbix


mysql -u root -p
set global log_bin_trust_function_creators = 0;
quit;



vim /etc/zabbix/zabbix_proxy.conf

ProxyMode: 
    0 - proxy in the active mode
    1 - proxy in the passive mode

#### 
ProxyMode=0
Server=10.10.10.10  # zabbix server ip
Hostname=zbx-proxy
DBName=zabbix_proxy
DBHost=localhost
DBUser=zbxproxy
DBPassword=StrongPassword
####

systemctl restart zabbix-proxy
systemctl enable zabbix-proxy





# increate pollers
vim /etc/zabbix/zabbix_proxy.conf
-----------------
StartPollers=20
StartPollersUnreachable=10
StartSNMPPollers=10
StartPingers=10
StartTrappers=10


# increase cache size
CacheSize=256M
HistoryCacheSize=128M
HistoryIndexCacheSize=64M



----------------


vim /etc/mariadb/server.conf
-----
[mysqld]
innodb_buffer_pool_size=2G
innodb_log_file_size=512M
innodb_flush_log_at_trx_commit=2

-----

systemctl restart mariadb


```





# zabbix server and proxy configuration
```sh


vim /etc/zabbix/zabbix_server.conf
------
HousekeepingFrequency=1
MaxHouseKeeperDelete=10000


CacheSize=2G  # Rule: ~8–10% of RAM
HistoryCacheSize=1G
HistoryIndexCacheSize=512M
TrendCacheSize=512M
ValueCacheSize=2G  # Big impact on frontend speed
StartDBSyncers=4


------

zabbix_server -R housekeeper_execute   # manually execute housekeeping


vim /etc/zabbix/zabbix_proxy.conf
-------
ProxyMode=0   # active mode
ProxyLocalBuffer=24 # how many hours proxy keep data locally, even if the data have already been synced with the server
ProxyOfflineBuffer=72 # proxy will keep data for N hours in case if no connectivity with zabbix server.
CacheSize=2G   # Rule: 5–10% of proxy RAM

HistoryCacheSize=1G # Buffers history before DB write
HistoryIndexCacheSize=1G


-------

```