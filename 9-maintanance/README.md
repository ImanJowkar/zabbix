# reset zabbix password

```
UPDATE users SET passwd = '$2a$10$ZXIvHAEP2ZM.dLXTm6uPHOMVlARXX7cqjbhM6Fn0cANzkCQBWpMrS' WHERE username = 'Admin';

```


# Disk 

```

find / -size +10M


```


# Backup and restore from mysql 
```
# backup
mysqldump --single-transaction  --no-tablespaces -u zabbix -p zabbix > zbx-backup.sql

# now delete the zabbix database for test(note that, its only for test)

mariadb -u root -p
drop database zabbix;

set global log_bin_trust_function_creators = 1;
quit

mariadb -u zabbix -p zabbix < zbx-backup.sql
mariadb -u root -p
set global log_bin_trust_function_creators = 0;


```

# Backup configuration file.

```
rsync -avP /etc/zabbix/ /zabbix-bak

rsync -avP /etc/zabbix/* -e "ssh -p 22" root@10.10.56.20:/zbx-bak



# only for test
rm -rf /etc/zabbix/
chmod 755 /etc/zabbix/
chmod 644 /etc/zabbix/web/zabbix.conf.php




```
