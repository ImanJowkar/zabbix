## Mariadb Installation


```bash

sudo apt update
sudo apt install mariadb-server mariadb-client
sudo systemctl status mariadb.service
sudo systemctl enable mariadb.service
sudo mysql_secure_installation


# create user
CREATE USER 'iman1'@'localhost' IDENTIFIED BY 'test';
GRANT ALL ON *.* TO 'iman1'@'localhost';
FLUSH PRIVILEGES;


CREATE USER 'iman1'@'%' IDENTIFIED BY 'test';
GRANT ALL ON zabbix.* TO 'iman1'@'%';
FLUSH PRIVILEGES;

# change root password
alter user 'root'@'localhost' identified by 'root';




 mariadb -u root -p
 use mysql;
 select host,user,password from user;


```

## backup and resotre zabbix database

```bash
# take a backup
mysqldump --single-transaction  --no-tablespaces -u root -p  zabbix > zabbix.sql

# make a damage
mysql -u root -p
show databases;
drop zabbix;
show databases;



# restore the database
mysql -u root -p
create database zabbix character set utf8mb4 collate utf8mb4_bin;
set global log_bin_trust_function_creators = 1;
quit;

mariadb -u root -p zabbix < zabbix.sql

mysql -uroot -p
 set global log_bin_trust_function_creators = 0;
 quit;
```









## zabbix administartion

```bash

[mysqld]
# General Settings
user = mysql
pid-file = /var/run/mysqld/mysqld.pid
socket = /var/run/mysqld/mysqld.sock
datadir = /var/lib/mysql
log_error = /var/log/mysql/error.log

# Performance Settings
max_connections = 1000
innodb_buffer_pool_size = 1G
innodb_log_file_size = 256M
innodb_flush_log_at_trx_commit = 1
sync_binlog = 1

# Query Cache (Optional)
query_cache_size = 0
query_cache_type = 0

# Binary Logging (Optional)
log_bin = /var/log/mysql/mysql-bin.log
server_id = 1


```


## Change datadir to another location

```sh
systemctl stop mariadb.service

mkdir /mariadbdata
chown -R mysql:mysql /mariadbdata


cp -R -p /var/lib/mysql/* /mariadbdata


vim /etc/mysql/mariadb.conf.d/50-server.cnf
----
datadir                 = /mariadbdata
----

```






## Optimize mysql for zabbix

```sh
vim /etc/mysql/mariadb.conf.d/50-server.cnf
-----
innodb_buffer_pool_size = 8G   # 50-75% available memory
-----

```


## backup and resotre zabbix database

```sh
# take a backup
mysqldump --single-transaction  --no-tablespaces -u root -p  zabbix > zabbix.sql

# make a damage
mysql -u root -p
show databases;
drop zabbix;
show databases;



# restore the database
mysql -u root -p
create database zabbix character set utf8mb4 collate utf8mb4_bin;
set global log_bin_trust_function_creators = 1;
quit;

mariadb -u root -p zabbix < zabbix.sql

mysql -uroot -p
 set global log_bin_trust_function_creators = 0;
 quit;

```



## some query
```sql


--- create user
CREATE USER 'iman1'@'localhost' IDENTIFIED BY 'test';
GRANT ALL ON *.* TO 'iman1'@'localhost';
FLUSH PRIVILEGES;


CREATE USER 'iman1'@'%' IDENTIFIED BY 'test';
GRANT ALL ON zabbix.* TO 'iman1'@'%';
FLUSH PRIVILEGES;

--- change root password
alter user 'root'@'localhost' identified by 'root';


```


```sh
mariadb -u root -p
```

```sql
use mysql;
select host,user,password from user;

show variables like 'datadir';
SHOW VARIABLES LIKE 'innodb_buffer_pool%';
show variables like '%log_bin%';

```

