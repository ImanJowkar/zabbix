# setup zabbix with postgresql and timescale db
# os: ubuntu 24.04
# zbx server version: 7.0.29
# postgresql: 18
# timescaledb: 2.28

# zbx-srv: 192.168.85.120
# zbx-db: 192.168.85.121

[time-scale-support-version](https://www.tigerdata.com/docs/deploy/self-hosted/upgrades/upgrade-pg)
[install-postgresql](https://www.postgresql.org/download/)

# setup db 85.121
```sh
apt update
apt upgrade


# add postgresql repo
sudo apt install curl ca-certificates
sudo install -d /usr/share/postgresql-common/pgdg
sudo curl -o /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc --fail https://www.postgresql.org/media/keys/ACCC4CF8.asc


sudo tee /etc/apt/sources.list.d/pgdg.sources > /dev/null <<'EOF'
Types: deb deb-src
URIs: https://apt.postgresql.org/pub/repos/apt
Suites: noble-pgdg
Architectures: amd64
Components: main
Signed-By: /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc
EOF



apt update
sudo apt install postgresql-18

wget https://repo.zabbix.com/zabbix/7.0/ubuntu/pool/main/z/zabbix-release/zabbix-release_latest_7.0+ubuntu24.04_all.deb
dpkg -i zabbix-release_latest_7.0+ubuntu24.04_all.deb
apt update

dpkg -s postgresql-18 | grep '^Version:' 

apt-cache madison zabbix-sql-scripts
apt-cache madison zabbix-agent2
apt-cache madison zabbix-selinux-policy

apt-cache madison zabbix-agent2-plugin-mongodb
apt-cache madison zabbix-agent2-plugin-mssql
apt-cache madison zabbix-agent2-plugin-postgresql



sudo apt install zabbix-sql-scripts='1:7.0.29-1+ubuntu24.04'
sudo apt install zabbix-agent2='1:7.0.29-1+ubuntu24.04'


sudo apt install zabbix-agent2-plugin-mongodb='1:7.0.29-1+ubuntu24.04'
sudo apt install zabbix-agent2-plugin-mssql='1:7.0.29-1+ubuntu24.04'
sudo apt install zabbix-agent2-plugin-postgresql='1:7.0.29-1+ubuntu24.04'


sudo -u postgres createuser --pwprompt zabbix
sudo -u postgres createdb -O zabbix zabbix

# create schema 
zcat /usr/share/zabbix-sql-scripts/postgresql/server.sql.gz | sudo -u zabbix psql zabbix


vim /etc/postgresql/18/main/postgresql.conf
-----
listen_addresses = '192.168.85.121'
max_connections = 1000                  # (change requires restart)

-----

vim /etc/postgresql/18/main/pg_hba.conf
-----
host    zabbix             zabbix             192.168.85.120/32            scram-sha-256
-----

systemctl restart postgresql


```

# setup zabbix-server
```sh
apt update
apt upgrade

wget https://repo.zabbix.com/zabbix/7.0/ubuntu/pool/main/z/zabbix-release/zabbix-release_latest_7.0+ubuntu24.04_all.deb
dpkg -i zabbix-release_latest_7.0+ubuntu24.04_all.deb
apt update



apt-cache madison zabbix-server-pgsql


sudo apt install zabbix-server-pgsql='1:7.0.29-1+ubuntu24.04'
sudo apt install zabbix-frontend-php='1:7.0.29-1+ubuntu24.04'
sudo apt install php8.3-pgsql
sudo apt install zabbix-nginx-conf='1:7.0.29-1+ubuntu24.04' 
sudo apt install zabbix-sql-scripts='1:7.0.29-1+ubuntu24.04'
sudo apt install zabbix-agent2='1:7.0.29-1+ubuntu24.04'

sudo apt install zabbix-agent2-plugin-mongodb='1:7.0.29-1+ubuntu24.04'
sudo apt install zabbix-agent2-plugin-mssql='1:7.0.29-1+ubuntu24.04'
sudo apt install zabbix-agent2-plugin-postgresql='1:7.0.29-1+ubuntu24.04'





# set DBPassword in /etc/zabbix/zabbix_server.conf
vim /etc/zabbix/zabbix_server.conf
------
DBHost=192.168.85.121
DBPassword=123456
DBName=zabbix
DBUser=zabbix
-----
# change nginx config
vim /etc/nginx/conf.d/zabbix.conf
------
listen 80;
server_name 192.168.85.120;

-----


systemctl restart zabbix-server zabbix-agent2 nginx php8.3-fpm
systemctl enable zabbix-server zabbix-agent2 nginx php8.3-fpm

```

# setup timescale db

```sh

systemctl stop zabbix-server

# go on the db server

sudo apt install gnupg postgresql-common apt-transport-https lsb-release wget
echo "deb https://packagecloud.io/timescale/timescaledb/ubuntu/ $(lsb_release -c -s) main" | sudo tee /etc/apt/sources.list.d/timescaledb.list

wget --quiet -O - https://packagecloud.io/timescale/timescaledb/gpgkey | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/timescaledb.gpg

sudo apt update



apt-cache madison postgresql-client-18
apt-cache madison timescaledb-2-postgresql-18
apt-cache madison timescaledb-2-loader-postgresql-18



dpkg -s timescaledb-2-loader-postgresql-18 | grep '^Version:'
dpkg -s postgresql-18 | grep '^Version:' 


sudo apt install  postgresql-client-18='18.6-1.pgdg24.04+2'

apt install timescaledb-2-postgresql-18='2.28.3~ubuntu24.04-1804' timescaledb-2-loader-postgresql-18='2.28.3~ubuntu24.04-1804'
 


timescaledb-tune --quiet --yes


vim /etc/postgresql/18/main/postgresql.conf
-----
shared_preload_libraries = 'timescaledb'
-----


sudo systemctl restart postgresql

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