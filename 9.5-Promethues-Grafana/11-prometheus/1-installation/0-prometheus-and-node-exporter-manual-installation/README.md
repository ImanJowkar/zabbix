# Prometheus





[Installation refrence](https://www.cherryservers.com/blog/install-prometheus-ubuntu)

go to the promethues website and download the promethues

[download-prometheus](https://github.com/prometheus/prometheus/releases)



#### basic system configurations
```

hostnamectl set-hostname prometheus-srv

dnf install epel-release

dnf install mtr tcpdump net-snmp-utils bind-utils sysstat  htop screen wget curl vim bash-completion traceroute telnet net-tools btop





```

#### Add a disk and set up LVM on it.
I added two disk `sdc` and `sdd`

```
fdisk /dev/sdc
fdisk /dev/sdd
lsblk

pvcreate /dev/sd[cd][1]
vgcreate prometheus-vg /dev/sd[cd][1]
echo $? ; pvs; vgs

lvcreate -n prometheus-lv -l 100%FREE prometheus-vg
echo $?; sync; lvs


mkfs.ext4 /dev/prometheus-vg/prometheus-lv
echo $?

# open fstab and insert below to end of the file 

vim /etc/fstab
/dev/prometheus-vg/prometheus-lv   /prom-data   ext4    defaults        0       1


mount -a
systemctl daemon-reload




```
If the `/prom-data/` directory becomes full in the future, we can expand it using LVM.


##### what is `sync` command: 

The `sync` command in Linux is used to flush the file system buffers. When you modify files, these changes are often stored in memory and periodically written to disk to improve performance. The `sync` command ensures that all modified data in memory is written to the storage devices, making sure that the file system's state is consistent and all changes are saved.


#### installation
```


wget https://github.com/prometheus/prometheus/releases/download/v2.48.0-rc.0/prometheus-2.48.0-rc.0.linux-amd64.tar.gz

tar xvf prometheus-2.48.0-rc.0.linux-amd64.tar.gz



sudo mkdir -p /etc/prometheus



# create prometheus user

useradd prometheus -r -s /sbin/nologin -d /prom-data/


sudo cp -r consoles /etc/prometheus/
sudo cp -r console_libraries/ /etc/prometheus/
sudo cp prometheus.yml /etc/prometheus/prometheus.yml
sudo cp prometheus /usr/local/bin/
sudo cp promtool /usr/local/bin/



sudo chown -R prometheus: /prom-data/
sudo chown -R prometheus: /etc/prometheus/


cat > /etc/prometheus/prometheus.yml << EOF
# this is prom basic configuration
global:
  scrape_interval: 15s # Set the scrape interval to every 15 seconds. Default is every 1 minute.

scrape_configs:
  - job_name: "prometheus-srv"
    static_configs:
      - targets: ["localhost:9090"]

EOF





# Create Service

cat > /usr/lib/systemd/system/prometheus.service << EOF

[Unit]
Description=Prometheus
Wants=network-online.target
After=network-online.target

[Service]
User=prometheus
Group=prometheus
Type=simple
ExecReload=/usr/bin/kill -HUP $MAINPID

ExecStart=/usr/local/bin/prometheus \
--config.file=/etc/prometheus/prometheus.yml \
--storage.tsdb.path=/prom-data/ \
--web.console.templates=/etc/prometheus/consoles \
--web.console.libraries=/etc/prometheus/console_libraries \
--web.listen-address=0.0.0.0:9090
--query.max-concurrency=100


SyslogIdentifier=prometheus
Restart=on-failure
RestartSec=60s

[Install]
WantedBy=multi-user.target
EOF





sudo systemctl daemon-reload
sudo systemctl enable prometheus
sudo systemctl start prometheus

```

`Prometheus itself does not have a setting to change the time zone because it stores all data in UTC.`

#### configure firewalld

```
firewall-cmd --add-port=9090/tcp --permanent
firewall-cmd --reload
firewall-cmd --list-all


```


# Install Node-Exporter

A Node Exporter is a small application that runs on the system you want to monitor and collects various metrics and information about the system's hardware and operating system. These metrics include details about CPU usage, memory usage, disk I/O, network statistics, and more. The Node Exporter then makes this information available to Prometheus for collection and analysis.




```
wget https://github.com/prometheus/node_exporter/releases/download/v1.6.1/node_exporter-1.6.1.linux-amd64.tar.gz

tar xvf node_exporter-1.6.1.linux-amd64.tar.gz
cd node_exporter-1.6.1.linux-amd64

cp node_exporter /usr/local/bin/

useradd node_exporter -r -s /sbin/nologin -c "node exporter user"



# Create Service

cat > /usr/lib/systemd/system/node-exporter.service << EOF

[Unit]
Description=Prometheus
After=network-online.target

[Service]
User=node_exporter
Group=node_exporter
Type=simple


ExecStart=/usr/local/bin/node_exporter 
SyslogIdentifier=node_exporter
Restart=on-failure
RestartSec=60s

[Install]
WantedBy=multi-user.target
EOF




sudo systemctl daemon-reload
sudo systemctl enable node-exporter.service
sudo systemctl start node-exporter.service



```
