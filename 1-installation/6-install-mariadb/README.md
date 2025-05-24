# Setup mariadb on ubuntu 

## Install the LTS version of that

[MariaDB Lifecycle: End Of Life And Support Status](https://www.itechtics.com/eol/mariadb/)

[ref](https://mariadb.org/download/?t=mariadb&o=true&p=mariadb&r=11.4.4&os=windows&cpu=x86_64&pkg=msi&mirror=archive)

#### installation on RHEL
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

```
![alt text](img/1.png)



#### installation on ubuntu 
```sh
apt-cache policy mariadb-server

apt install mariadb-server

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

