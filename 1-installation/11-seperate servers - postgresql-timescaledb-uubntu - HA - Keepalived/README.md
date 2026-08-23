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

chmod 644 /etc/apt/trusted.gpg.d/timescaledb.gpg
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




# zbx-node1

```sh
vim /etc/zabbix/zabbix_server.conf
----
HANodeName=zbx-srv1
NodeAddress=192.168.85.151:10051
----

vim /etc/keepalived/keepalived.conf
----
global_defs {
    router_id ZBX_SRV1

    enable_script_security
    script_user root

    vrrp_garp_master_delay 1
    vrrp_garp_master_repeat 5
    vrrp_garp_master_refresh 60
    vrrp_garp_master_refresh_repeat 2
}

vrrp_script chk_nginx {
    script "/etc/keepalived/check_nginx.sh"
    interval 2
    timeout 2
    fall 3
    rise 2
    weight -60
}

vrrp_instance ZBX_WEB {
    state MASTER

    interface ens33

    virtual_router_id 51
    priority 150
    advert_int 1

    unicast_src_ip 192.168.85.151

    unicast_peer {
        192.168.85.152
    }

    virtual_ipaddress {
        192.168.85.153/24 dev ens33
    }

    track_script {
        chk_nginx
    }
}

----


cat > /etc/keepalived/check_nginx.sh <<'EOF'
#!/bin/bash

curl -fsS \
    --connect-timeout 1 \
    --max-time 2 \
    http://127.0.0.1/ >/dev/null 2>&1

exit $?
EOF


chmod 700 /etc/keepalived/check_nginx.sh
chown root:root /etc/keepalived/check_nginx.sh



vim /etc/ufw/before.rules
----
-A ufw-before-input -i ens33 -p 112 -s 192.168.85.152 -d 192.168.85.151 -j ACCEPT
-A ufw-before-output -o ens33 -p 112 -s 192.168.85.151 -d 192.168.85.152 -j ACCEPT
----


ufw reload


```



# zbx-node2

```sh
vim /etc/zabbix/zabbix_server.conf
----
HANodeName=zbx-srv2
NodeAddress=192.168.85.152:10051
----


vim /etc/keepalived/keepalived.conf
----
global_defs {
    router_id ZBX_SRV2

    enable_script_security
    script_user root

    vrrp_garp_master_delay 1
    vrrp_garp_master_repeat 5
    vrrp_garp_master_refresh 60
    vrrp_garp_master_refresh_repeat 2
}

vrrp_script chk_nginx {
    script "/etc/keepalived/check_nginx.sh"
    interval 2
    timeout 2
    fall 3
    rise 2
    weight -60
}

vrrp_instance ZBX_WEB {
    state BACKUP

    interface ens33

    virtual_router_id 51
    priority 100
    advert_int 1

    unicast_src_ip 192.168.85.152

    unicast_peer {
        192.168.85.151
    }

    virtual_ipaddress {
        192.168.85.153/24 dev ens33
    }

    track_script {
        chk_nginx
    }
}

----



cat > /etc/keepalived/check_nginx.sh <<'EOF'
#!/bin/bash

curl -fsS \
    --connect-timeout 1 \
    --max-time 2 \
    http://127.0.0.1/ >/dev/null 2>&1

exit $?
EOF


chmod 700 /etc/keepalived/check_nginx.sh
chown root:root /etc/keepalived/check_nginx.sh



vim /etc/ufw/before.rules
----

-A ufw-before-input -i ens33 -p 112 -s 192.168.85.151 -d 192.168.85.152 -j ACCEPT
-A ufw-before-output -o ens33 -p 112 -s 192.168.85.152 -d 192.168.85.151 -j ACCEPT
----

ufw reload

```



# delete pgsql zbx database

```sh

su - postgres
psql zabbix


# see the active connection to zabbix db
SELECT pid, usename, datname, client_addr, state
FROM pg_stat_activity
WHERE datname = 'zabbix';


SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'zabbix'
  AND pid <> pg_backend_pid();

exit


----------------
su - postgres
dropdb zabbix

psql -c '\l'
psql -c '\du'




```