## Zabbix-server installation


```sh
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
firewall-cmd --state
firewall-cmd --get-default-zone
firewall-cmd --get-active-zones
firewall-cmd --list-all
firewall-cmd --get-zones
firewall-cmd --list-all --zone=home


firewall-cmd --list-all --zone=drop
firewall-cmd --list-all --permanent --zone=drop



firewall-cmd --zone=drop --change-interface=ens32 --permanent
firewall-cmd --reload
firewall-cmd --get-default-zone
firewall-cmd --get-active-zones
firewall-cmd --list-all --permanent --zone=drop

# firewall-cmd --zone=drop --add-service=zabbix-server --permanent
firewall-cmd  --add-port=10051/tcp --zone=drop --permanent
firewall-cmd  --add-port=10050/tcp --zone=drop --permanent

firewall-cmd --zone=drop --add-port=80/tcp --permanent
firewall-cmd --zone=drop --add-port=443/tcp --permanent

# firewall-cmd --zone=drop --add-port=3306/tcp --permanent

firewall-cmd --reload
firewall-cmd --zone=drop --list-all 

```

## if you get system-locale error when setting up zabbix install below package

```sh
# On RHEL/CentOS/Alma/Rocky
sudo dnf install glibc-langpack-en -y

# On Debian/Ubuntu
sudo apt install locales -y
sudo dpkg-reconfigure locales

```
