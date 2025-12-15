# Setup Zabbix using postgresql and timescaledb on AlmaLinux

#### postgresql : postgresql-17
#### zabbix: zabbix-server-pgsql-7.0.14
#### timescaledb: 2.19

[time-scale-support-version](https://www.tigerdata.com/docs/self-hosted/latest/upgrades/upgrade-pg)

## install glibc-lanpack-en
```sh
dnf install glibc-langpack-en net-tools python3-dnf-plugin-versionlock


```
### Setup Postgresql

```sh

sudo dnf install -y https://download.postgresql.org/pub/repos/yum/reporpms/EL-9-x86_64/pgdg-redhat-repo-latest.noarch.rpm
sudo dnf -qy module disable postgresql


dnf list postgresql17-server --showduplicates

sudo dnf install -y postgresql17-server
sudo /usr/pgsql-17/bin/postgresql-17-setup initdb
sudo systemctl enable postgresql-17 --now

```



# Setup zabbix

```sh

# exclude zabbix in epel
[epel]
...
excludepkgs=zabbix*


rpm -Uvh https://repo.zabbix.com/zabbix/7.0/rocky/9/x86_64/zabbix-release-latest-7.0.el9.noarch.rpm

dnf clean all


dnf makecache


dnf list zabbix-server-pgsql --showduplicates
dnf list zabbix-web-pgsql --showduplicates
dnf list zabbix-nginx-conf --showduplicates
dnf list zabbix-sql-scripts --showduplicates
dnf list zabbix-selinux-policy --showduplicates
dnf list zabbix-agent2 --showduplicates

# 7.0.14-release1

dnf install -y zabbix-server-pgsql-7.0.14
dnf install -y zabbix-web-pgsql-7.0.14
dnf install -y zabbix-nginx-conf-7.0.14
dnf install -y zabbix-sql-scripts-7.0.14
dnf install -y zabbix-selinux-policy-7.0.14
dnf install -y zabbix-agent2-7.0.14 



# zabbix agent extensions

dnf list zabbix-agent2-plugin-mongodb --showduplicates
dnf install -y zabbix-agent2-plugin-mongodb-7.0.14
dnf install -y zabbix-agent2-plugin-mssql-7.0.14 
dnf install -y zabbix-agent2-plugin-postgresql-7.0.14





# create database
sudo -u postgres createuser --pwprompt zabbix
sudo -u postgres createdb -O zabbix zabbix

# create schema 
zcat /usr/share/zabbix-sql-scripts/postgresql/server.sql.gz | sudo -u zabbix psql zabbix


# set DBPassword in /etc/zabbix/zabbix_server.conf
vim /etc/zabbix/zabbix_server.conf
------
DBPassword=123456
-----
# change nginx config
vim /etc/nginx/conf.d/zabbix.conf
------
listen 80;
server_name 192.168.85.28;

-----



systemctl restart zabbix-server zabbix-agent2 nginx php-fpm
systemctl enable zabbix-server zabbix-agent2 nginx php-fpm --now





# setup timescaledb
sudo tee /etc/yum.repos.d/timescale_timescaledb.repo <<EOL
[timescale_timescaledb]
name=timescale_timescaledb
baseurl=https://packagecloud.io/timescale/timescaledb/el/$(rpm -E %{rhel})/\$basearch
repo_gpgcheck=1
gpgcheck=0
enabled=1
gpgkey=https://packagecloud.io/timescale/timescaledb/gpgkey
sslverify=1
sslcacert=/etc/pki/tls/certs/ca-bundle.crt
metadata_expire=300
EOL


dnf clean all
dnf makecache


# show and select specific version of timescaledb

dnf list timescaledb-2-postgresql-17 --showduplicates
dnf list timescaledb-2-loader-postgresql-17 --showduplicates
dnf list timescaledb-tools --showduplicates



# 2.19.3-0.el9

dnf install timescaledb-2-postgresql-17-2.19.3 timescaledb-2-loader-postgresql-17-2.19.3 timescaledb-tools-0.17.0



sudo dnf versionlock add timescaledb-2-postgresql-17 
sudo dnf versionlock timescaledb-2-loader-postgresql-17 
sudo dnf versionlock timescaledb-tools 

sudo dnf versionlock list


# Configure TimescaleDB
sudo timescaledb-tune --pg-config=/usr/pgsql-17/bin/pg_config


vim /var/lib/pgsql/17/data/postgresql.conf
-----
shared_preload_libraries = 'timescaledb'
-----

sudo systemctl restart postgresql-17.service



# Configure Zabbix for timescaledb

sudo systemctl stop zabbix-server.service

# Create timescaledb extension
sudo su - postgres
psql  zabbix
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;
\dx

# Patch Zabbix database
\i /usr/share/zabbix-sql-scripts/postgresql/timescaledb/schema.sql
exit
exit


sudo systemctl start zabbix-server


```