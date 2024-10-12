## Zabbix-server installation


```
## install mariadb

sudo apt update
sudo apt install mariadb-server
sudo mysql_secure_installation




# install zabbix 

wget https://repo.zabbix.com/zabbix/7.0/ubuntu/pool/main/z/zabbix-release/zabbix-release_7.0-1+ubuntu22.04_all.deb
sudo dpkg -i zabbix-release_7.0-1+ubuntu22.04_all.deb
sudo apt update

sudo apt install zabbix-server-mysql zabbix-frontend-php zabbix-apache-conf zabbix-sql-scripts zabbix-agent



# configure database: 

mariadb -uroot -p
create database zabbix character set utf8mb4 collate utf8mb4_bin;
create user zabbix@localhost identified by 'password';
grant all privileges on zabbix.* to zabbix@localhost;
set global log_bin_trust_function_creators = 1;
quit;

zcat /usr/share/zabbix-sql-scripts/mysql/server.sql.gz | mysql --default-character-set=utf8mb4 -uzabbix -p zabbix




mariadb -uroot -p
set global log_bin_trust_function_creators = 0;
quit;


# then go to the zabbix configuration file and edit below: 
sudo vim /etc/zabbix/zabbix_server.conf
######
DBPassword=password
######

# save and exit 

sudo systemctl restart zabbix-server zabbix-agent apache2
sudo systemctl enable zabbix-server zabbix-agent apache2






# firewall configurations

sudo ufw allow 10051/tcp
# sudo ufw allow 10050/tcp
sudo ufw allow 80/tcp





# you can reset ufw with below command
sudo ufw reset




# if you are using RHEL

sudo firewall-cmd  --add-port=10051/tcp --permanent
sudo firewall-cmd  --add-port=10050/tcp --permanent
sudo firewall-cmd  --add-service=http --permanent
sudo firewall-cmd --reload
sudo firewall-cmd --list-all

```

