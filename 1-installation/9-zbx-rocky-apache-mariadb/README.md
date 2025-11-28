# Installation

## local rocky linux repo 
```sh
vim /etc/yum.repos.d/rocky.repo
--------
[baseos]
name=Rocky Linux $releasever - BaseOS
#mirrorlist=https://mirrors.rockylinux.org/mirrorlist?arch=$basearch&repo=BaseOS-$releasever$rltype
#baseurl=http://dl.rockylinux.org/$contentdir/$releasever/BaseOS/$basearch/os/
baseurl=https://repo.iut.ac.ir/repo/rocky-linux/$releasever/BaseOS/$basearch/os/
gpgcheck=1
enabled=1
countme=1
metadata_expire=6h
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-Rocky-9


[appstream]
name=Rocky Linux $releasever - AppStream
#mirrorlist=https://mirrors.rockylinux.org/mirrorlist?arch=$basearch&repo=AppStream-$releasever$rltype
baseurl=https://repo.iut.ac.ir/repo/rocky-linux/$releasever/AppStream/$basearch/os/
gpgcheck=1
enabled=1
countme=1
metadata_expire=6h
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-Rocky-9



[extras]
name=Rocky Linux $releasever - Extras
#mirrorlist=https://mirrors.rockylinux.org/mirrorlist?arch=$basearch&repo=extras-$releasever$rltype
#baseurl=http://dl.rockylinux.org/$contentdir/$releasever/extras/$basearch/os/
baseurl=https://repo.iut.ac.ir/repo/rocky-linux/$releasever/extras/$basearch/os/
gpgcheck=1
enabled=1
countme=1
metadata_expire=6h
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-Rocky-9


```


```sh
vim /etc/yum.repos.d/mariadb.repo
-------

# MariaDB 11.4 RedHatEnterpriseLinux repository list - created 2025-11-17 04:50 UTC
# https://mariadb.org/download/
[mariadb]
name = MariaDB
# rpm.mariadb.org is a dynamic mirror if your preferred mirror goes offline. See https://mariadb.org/mirrorbits/ for details.
# baseurl = https://rpm.mariadb.org/11.4/rhel/$releasever/$basearch
baseurl = https://ir.mariadb.sindad.cloud/yum/11.4/rhel/$releasever/$basearch
# gpgkey = https://rpm.mariadb.org/RPM-GPG-KEY-MariaDB
gpgkey = https://ir.mariadb.sindad.cloud/yum/RPM-GPG-KEY-MariaDB
gpgcheck = 1


-------

sudo dnf makecache
sudo dnf install MariaDB-server MariaDB-client



```


## setup self-sgin cert
```sh
mkdir -p /etc/ssl/zabbix
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/zabbix/zabbix.key \
  -out /etc/ssl/zabbix/zabbix.crt


sudo chmod 600 /etc/ssl/zabbix/zabbix.key
sudo chown root:root /etc/ssl/zabbix/zabbix.*


sudo vim /etc/httpd/conf.d/zabbix-ssl.conf

---------
<VirtualHost *:443>
    ServerName your-zabbix-domain-or-ip

    DocumentRoot /usr/share/zabbix

    SSLEngine on
    SSLCertificateFile /etc/ssl/zabbix/zabbix.crt
    SSLCertificateKeyFile /etc/ssl/zabbix/zabbix.key

    <Directory "/usr/share/zabbix">
        Require all granted
    </Directory>

    php_value date.timezone Europe/London
</VirtualHost>


---------
sudo systemctl restart httpd



```