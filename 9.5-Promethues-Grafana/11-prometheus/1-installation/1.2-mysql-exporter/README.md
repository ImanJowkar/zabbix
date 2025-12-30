MySQL exporter (mysqld_exporter) is compatible with MariaDB. Both MySQL and MariaDB share a common ancestry and have a high degree of compatibility, especially when it comes to monitoring and metrics.

```

wget https://github.com/prometheus/mysqld_exporter/releases/download/v0.15.1/mysqld_exporter-0.15.1.linux-amd64.tar.gz


 tar xvf mysqld_exporter-0.15.1.linux-amd64.tar.gz

mv mysqld_exporter /usr/local/bin/


# connect to the mariadb or mysql engine and create a user and password for exporter to connect 

CREATE USER 'exporter'@'localhost' IDENTIFIED BY 'yourpassword';
GRANT PROCESS, REPLICATION CLIENT, SELECT ON *.* TO 'exporter'@'localhost';
FLUSH PRIVILEGES;


# now create a file and store user and password for node exporter

sudo cat > /etc/mysqld_exporter.cnf << EOF
[client]
user=exporter
password=yourpassword
EOF

# now crate a service unit for it

cat > /usr/lib/systemd/system/mysqld_exporter.service << EOF

[Unit]
Description=Prometheus MySQL Exporter
Wants=network-online.target
After=network-online.target

[Service]
User=node_exporter
Group=node_exporter
ExecStart=/usr/local/bin/mysqld_exporter --config.my-cnf=/etc/mysqld_exporter.cnf --web.listen-address=:9204
Restart=always

[Install]
WantedBy=multi-user.target
EOF


chown node_exporter: /etc/mysqld_exporter.cnf


sudo systemctl daemon-reload
sudo systemctl restart prometheus



```