## Mariadb Installation


```

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


## resotre sakila-db

```
tar -xvf sakila-db.tar.gz

cd sakila-db
mariadb -u root -p < sakila-schema.sql
mariadb -u root -p < sakila-data.sql




```















# old

```
# resoter data: 
mariadb -u root -p < Chinook.sql



# afew query
SELECT * from Track WHERE Bytes > (SELECT AVG(Bytes) from Track ) ;

SELECT  * from Invoice as t1
WHERE t1.Total  > 9;




```


