Prometheus Node Exporter is designed to expose system metrics, but it doesn't support custom metrics out of the box. However, you can use the Node Exporter's textfile collector to achieve this. The textfile collector reads metrics from files in a specified directory and exports them to Prometheus.

* Enable the Textfile Collector:
```
mkdir -p /tmp/node_exporter_custom_data/


cat > /usr/lib/systemd/system/node_exporter.service << EOF
[Unit]
Description=Node Exporter
Wants=network-online.target
After=network-online.target

[Service]
User=node_exporter
Group=node_exporter
Type=simple
ExecStart=/usr/local/bin/node_exporter --collector.textfile.directory=/tmp/node_exporter_custom_data/


SyslogIdentifier=node_exporter
Restart=on-failure
RestartSec=60s

[Install]
WantedBy=multi-user.target
EOF


cat > /tmp/node_exporter_custom_data/users.prom << EOF
active_users{remote="true"} 5
active_users{remote="false"} 1
EOF


# add below to crontab

* * * * * for i in {1..6}; do echo active_users{remote="true"} echo $RANDOM > /tmp/node_exporter_custom_data/users.prom ; echo active_users{remote="false"} echo $RANDOM >> /tmp/node_exporter_custom_data/users.prom ; sleep 10; done

```

