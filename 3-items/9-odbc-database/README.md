# database

## pgsql
```sh
psql -U postgres

CREATE DATABASE mydb;

\l


# CREATE USER myuser WITH PASSWORD 'strong_password';

CREATE ROLE myuser WITH LOGIN PASSWORD 'test';
GRANT ALL PRIVILEGES ON DATABASE mydb TO myuser;



# install postgresql client on rocky linux
sudo dnf install -y postgresql

psql -h 192.168.85.71 -p 5432 -U myuser -d mydb 



# or you can install pgcli
mkdir python-pgcli && cd python-pgcli

python -m venv venv
source venv/bin/activate

pip install -U pgcli

pgcli postgres://postgres:test222@192.168.96.141:5432/

pgcli -h 192.168.85.71 -p 5432 -d mydb -U myuser  -W

select version();









```

## mariadb
```sh
mysql
CREATE USER 'iman'@'192.168.85.79' IDENTIFIED BY 'iman';
GRANT ALL ON *.* TO 'iman'@'192.168.85.79';
flush privileges;


exit


pip install mysql-connector-python


# create systemd unit file
vim /usr/lib/systemd/system/app.service
----------------
[Unit]
Description=an application which write data to DataBase.
After=network.target

[Service]
ExecStart=/root/python/venv/bin/python /root/python/app.py
StandardOutput=journal
StandardError=journal
# Environment=DB_HOST=192.168.229.167
# Environment=DB_PORT=3307
# Environment=DB_USER=app
# Environment=DB_PASSWORD=apppassword

[Install]
WantedBy=multi-user.target
----------

systemctl daemon-reload 
systemctl start app.service



## install odbc-connector on zabbix server or zabbix proxy
dnf install mariadb-connector-odbc

vim /etc/odbc.ini
----
[myapp]
Description=my application
Driver=MariaDB
Server=192.168.85.140
Port=3306
User=iman
Password=iman
Database=OrdersDB
----


isql myapp

```

# some query

```sql
select count(*) from Orders;
select * from Orders where shop_name="digikala";
select * from Orders where shop_name="digikala" and product_name="Smartphone";
select count(*) from Orders where shop_name="digikala" and product_name="Smartphone";
select count(*) from Orders where product_name="Smartphone" and order_date > date_add(now(), interval - 1 minute);

select count(*) as total,shop_name from Orders where product_name="Smartphone" and order_date > date_add(now(), interval - 1 minute) group by shop_name;

select count(*) as total ,shop_name,product_name from Orders where order_date > date_add(now(), interval - 1 minute) group by shop_name,product_name;



```