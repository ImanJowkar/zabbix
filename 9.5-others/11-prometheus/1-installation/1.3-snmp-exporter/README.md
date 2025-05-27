# snmp exporter

```
wget https://github.com/prometheus/snmp_exporter/releases/download/v0.26.0/snmp_exporter-0.26.0.linux-amd64.tar.gz



tar xvf snmp_exporter-0.26.0.linux-amd64.tar.gz
cd snmp_exporter-0.26.0.linux-amd64
useradd snmp_exporter -r -s /sbin/nologin -c "snmp exporter user"
cp snmp_exporter /usr/local/bin/
chown snmp_exporter: /usr/local/bin/snmp_exporter
mkdir /etc/snmp-exporter
cp snmp.yml /etc/snmp-exporter/
chown -R snmp_exporter: /etc/snmp-exporter/



# Create Service

cat > /usr/lib/systemd/system/snmp-exporter.service << EOF

[Unit]
Description=Prometheus snmp exporter
After=network-online.target

[Service]
User=snmp_exporter
Group=snmp_exporter
Type=simple


ExecStart=/usr/local/bin/snmp_exporter --config.file=/etc/snmp_exporter/snmp.yml
SyslogIdentifier=snmp-exporter
Restart=on-failure
RestartSec=60s

[Install]
WantedBy=multi-user.target
EOF




sudo systemctl daemon-reload
sudo systemctl enable snmp-exporter.service
sudo systemctl start snmp-exporter.service



```