![repository for download zabbix](https://repo.zabbix.com)


# if you got `System locale` error install the folowing pakages:

```sh

dnf install glibc-langpack-en

```
[ref](https://www.tecmint.com/fix-failed-to-set-locale-defaulting-to-c-utf-8-in-centos/)



# security
```sh

# hide nginx version
vim /etc/nginx/nginx.conf
-----
server_tokens       off;
-----

nginx -s reload





# hide php version 
vim /etc/php.ini
-----
expose_php = Off
-----
systemctl restart php-fpm








```