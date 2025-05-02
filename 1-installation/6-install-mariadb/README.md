# Setup mariadb on ubuntu 


### add mariadb-repo
[MariaDB Lifecycle: End Of Life And Support Status](https://www.itechtics.com/eol/mariadb/)

[ref](https://mariadb.org/download/?t=mariadb&o=true&p=mariadb&r=11.4.4&os=windows&cpu=x86_64&pkg=msi&mirror=archive)



```
apt-cache policy mariadb-server

apt install mariadb-server



```


# some query

```


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




show variables like 'datadir';
SHOW VARIABLES LIKE 'innodb_buffer_pool%';
show variables like '%log_bin%';


```


## backup and resotre zabbix database

```
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


## Change datadir to another location

```
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

```
vim /etc/mysql/mariadb.conf.d/50-server.cnf

    innodb_buffer_pool_size = 8G   # 50-75% available memory
 
 








```