# Setup zabbix on Rocky linux 9.6 with mariadb and httpd

first of all go the blow website and find the most mariadb LTS version support
[ref](https://endoflife.date/mariadb)  # I use the version 11.4

```sh
vim /etc/yum.repos.d/mariadb.repo
------
# MariaDB 11.4 RedHatEnterpriseLinux repository list - created 2025-11-28 07:50 UTC
# https://mariadb.org/download/
[mariadb]
name = MariaDB
# rpm.mariadb.org is a dynamic mirror if your preferred mirror goes offline. See https://mariadb.org/mirrorbits/ for details.
# baseurl = https://rpm.mariadb.org/11.4/rhel/$releasever/$basearch
baseurl = https://mirror.parsvds.com/mariadb/yum/11.4/rhel/$releasever/$basearch
# gpgkey = https://rpm.mariadb.org/RPM-GPG-KEY-MariaDB
gpgkey = https://mirror.parsvds.com/mariadb/yum/RPM-GPG-KEY-MariaDB
gpgcheck = 1
------

dnf clean all
dnf makecache
sudo dnf install MariaDB-server MariaDB-client
mariadb-secure-installation

# then go to the zabbix website and install the zabbix stack using the guide

```
[ref](https://www.zabbix.com/download?zabbix=7.0&os_distribution=rocky_linux&os_version=9&components=server_frontend_agent&db=mysql&ws=apache)


## create Self-Signed certs
```sh
openssl req -x509 -nodes -days 365 -newkey rsa:2048   -keyout /etc/pki/tls/private/zabbix.key  -out /etc/pki/tls/certs/zabbix.crt

sudo chmod 600 /etc/pki/tls/private/zabbix.key
sudo chmod 644 /etc/pki/tls/certs/zabbix.crt


vim /etc/httpd/conf.d/ssl.conf
---
SSLEngine on
SSLCertificateFile /etc/pki/tls/certs/zabbix.crt
SSLCertificateKeyFile /etc/pki/tls/private/zabbix.key
---


```



## if you want to redirect http -> https
```sh
## only zabbix

-----
# add at the top
RewriteEngine On
RewriteCond %{HTTPS} off
RewriteRule ^/zabbix/(.*) https://192.168.85.180/zabbix/$1 [R=301,L]
------






# globally 
vim /etc/httpd/conf/httpd.conf
-----
# add at the end
RewriteEngine On
RewriteCond %{SERVER_PORT} !=443
RewriteRule ^/(.*)$ https://192.168.85.180/$1 [R=301,L]
-----

```
