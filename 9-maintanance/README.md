# reset zabbix password

```

htpasswd -bnBC 10 "" YourNewPassword | tr -d ':'
# copy the output

update users set passwd='<copied output>' where alias='Admin';          # zabbix 5
update users set passwd='<copied output>' where username='Admin';       # zabbix 6, 7

UPDATE users SET passwd = '$2a$10$ZXIvHAEP2ZM.dLXTm6uPHOMVlARXX7cqjbhM6Fn0cANzkCQBWpMrS' WHERE username = 'Admin';

```



### you can change the login type in database 
```
mariadb -u root -p
show databases;
use zabbix;

select authentication_type from config;

        0: Internal
        1: LDAP

update config set authentication_type=1;
select authentication_type from config;


```






# useful command

```

find / -size +10M
sed -i 's/find/pattern/g' /etc/zabbix/zabbix.conf

sudo -H -u zabbix bash -c 'tail -f /var/log/nginx/access.log'
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

# Performance Tuning
[ref](https://youtube.come)
![img](img/1.png)
![img](img/2.png)


### install ntop on debain 12
[ref](https://green.cloud/docs/how-to-install-ntopng-on-debian-12/)

```

apt update && apt install software-properties-common wget

source /etc/os-release
wget https://packages.ntop.org/apt/$VERSION_CODENAME/all/apt-ntop.deb
apt install ./apt-ntop.deb


apt update && apt install ntopng
netstat -ntlp


http://localhost:3000

user, pass: admin, admin


```


![img](img/3.png)
![img](img/4.png)
![img](img/5.png)
![img](img/6.png)
![img](img/7.png)

### proxy tunning

![img](img/8.png)
![img](img/9.png)


### database tunning

![img](img/10.png)
![img](img/11.png)


### unchanged items
![img](img/12.png)



### deploy on seprate machine
![img](img/13.png)


## Set https on zabbix when using nginx as a web server

```sh
cd /etc/zabbix
openssl req -newkey rsa:2048 -nodes -keyout key.pem -x509 -days 365 -out cert.pem

vim /etc/zabbix/nginx.conf
server {
    listen 80;
    server_name 192.168.56.90;

    location / {
        return 301 https://$host$request_uri;
    }
}

server {
       listen          443 ssl;
       server_name 192.168.56.90;
       ssl_certificate /etc/zabbix/cert.pem;
       ssl_certificate_key /etc/zabbix/key.pem;

       root    /usr/share/zabbix;

        index   index.php;

        location = /favicon.ico {
                log_not_found   off;
        }

        location / {
                try_files       $uri $uri/ =404;
        }

        location /assets {
                access_log      off;
                expires         10d;
        }

        location ~ /\.ht {
                deny            all;
        }

        location ~ /(api\/|conf[^\.]|include|locale) {
                deny            all;
                return          404;
        }

        location /vendor {
                deny            all;
                return          404;
        }

        location ~ [^/]\.php(/|$) {
                fastcgi_pass    unix:/var/run/php/zabbix.sock;
                fastcgi_split_path_info ^(.+\.php)(/.+)$;
                fastcgi_index   index.php;

                fastcgi_param   DOCUMENT_ROOT   /usr/share/zabbix;
                fastcgi_param   SCRIPT_FILENAME /usr/share/zabbix$fastcgi_script_name;
                fastcgi_param   PATH_TRANSLATED /usr/share/zabbix$fastcgi_script_name;

                include fastcgi_params;
                fastcgi_param   QUERY_STRING    $query_string;
                fastcgi_param   REQUEST_METHOD  $request_method;
                fastcgi_param   CONTENT_TYPE    $content_type;
                fastcgi_param   CONTENT_LENGTH  $content_length;

                fastcgi_intercept_errors        on;
                fastcgi_ignore_client_abort     off;
                fastcgi_connect_timeout         60;
                fastcgi_send_timeout            180;
                fastcgi_read_timeout            180;
                fastcgi_buffer_size             128k;
                fastcgi_buffers                 4 256k;
                fastcgi_busy_buffers_size       256k;
                fastcgi_temp_file_write_size    256k;
        }
}



nginx -t 
nginx -s reload
```



# enable psk between zabbix server and zabbix proxy

```

# generate a random number for using as a secret in zabbix

cd /etc/zabbix
openssl rand -hex 32 > secret.psk

chmod 640 secret.psk
chown zabbix: secret.psk


# add below config to you zabbix_proxy.conf or zabbix_agent.conf

TLSConnect=psk
TLSAccept=psk
TLSPSKIdentity=proxy
TLSPSKFile=/etc/zabbix/secret.psk



# next enable encryption in zabbix UI like below image
```
![img](img/14.png)




# context switching

![img](./9-maintanance/img/context-switching.png)

