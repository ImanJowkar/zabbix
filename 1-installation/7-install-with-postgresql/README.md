# Database

## install postgresql on ubuntu from postgresql repositroy

### initialize the server
```sh
hostnamectl set-hostname zbx-db # change in /etc/hosts too


```

[version-EOL](https://endoflife.date/postgresql)

[installation](https://www.postgresql.org/download/)



```sh

apt install iotop sysstat lsof dstat bash-completion vim nano tar zip unzip wget

sudo apt install -y postgresql-common
sudo /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh


sudo apt install postgresql-18

sudo su - postgres
psql -c "alter user postgres with password 'test'"
psql

select version();
select current_user;
\du # list of roles


vim /etc/postgresql/18/main/postgresql.conf
-------
# listen_addresses = 'localhost'
listen_addresses = '0.0.0.0'
-------


vim /etc/postgresql/18/main/pg_hba.conf
------
# Accept from anywhare
#host    all     all             0.0.0.0/0                 md5

# Accept from trusted subnets
host    all     all             192.168.96.0/24                 md5
------

systemctl restart postgresql


psql -h 192.168.96.141 -p 5432 -U postgres

psql -h 192.168.96.141 -p 5432 -d database-name -U username  -W
psql -h 192.168.96.141 -p 5432 -d postgres -U postgres  -W  -c "select current_time"



# increase postgres security by forcing anyone to provide password when login
vim /etc/postgresql/18/main/pg_hba.conf
# comment the peer and change to md5 like below
------
# local   all             postgres                                peer
local   all             postgres                                md5
------

sudo -u postgres createuser --pwprompt zabbix
sudo -u postgres createdb -O zabbix zabbix


wget https://repo.zabbix.com/zabbix/7.0/debian/pool/main/z/zabbix-release/zabbix-release_latest_7.0+debian12_all.deb
dpkg -i zabbix-release_latest_7.0+debian12_all.deb
apt update


apt install zabbix-server-pgsql zabbix-frontend-php php8.2-pgsql zabbix-nginx-conf zabbix-sql-scripts zabbix-agent


zcat /usr/share/zabbix-sql-scripts/postgresql/server.sql.gz | sudo -u zabbix psql zabbix


vim /etc/zabbix/zabbix_server.conf
------
DBName=zabbix
DBUser=zabbix
DBPassword=test
DBHost=localhost
------


# install timescaledb


```