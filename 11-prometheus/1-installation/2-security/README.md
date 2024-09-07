## Security in Prometheus


### Basic Authentication
```
dnf install httpd-tools
sudo apt-get install apache2-utils


# run below command to generate a username and encrypted password 
htpasswd -nBC 10 "username"
# this is the output
username:$2y$10$94Xxw5G7JT.siRBD1LrtleN9iGd.xFYN9jP2Ravq.RHLK9KKH/t6a

# you can create mor user and password 



cat > /etc/prometheus/web.yaml << EOF
basic_auth_users:
  username: $2y$10$94Xxw5G7JT.siRBD1LrtleN9iGd.xFYN9jP2Ravq.RHLK9KKH/t6a
EOF

sudo chown -R prometheus: /etc/prometheus/

# now you can change the prometheus service file and add this configuration when running the prometheus binary

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
--storage.tsdb.path=/var/lib/prometheus/ \
--web.console.templates=/etc/prometheus/consoles \
--web.console.libraries=/etc/prometheus/console_libraries \
--web.listen-address=0.0.0.0:9090 \
--web.config.file=/etc/prometheus/web.yaml


SyslogIdentifier=prometheus
Restart=on-failure
RestartSec=60s

[Install]
WantedBy=multi-user.target
EOF


sudo systemctl daemon-reload
sudo systemctl restart prometheus

# you have to get password to the promethues to monitor itself
cat > /etc/prometheus/prometheus.yml << EOF
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'prom-srv'
    static_configs:
      - targets: ["192.168.56.220:9090"]
    basic_auth:
      username: 'username'
      password: 'pass'
  - job_name: 'promtheus-exporters'
    static_configs:
      - targets: ['192.168.56.220:9100', '192.168.56.221:9100']
EOF


```





### you can set basic auth for node exporter like above

```

mkdir /etc/node_exporter/
cat > /etc/node_exporter/web.yaml << EOF
basic_auth_users:
  username: $2y$10$94Xxw5G7JT.siRBD1LrtleN9iGd.xFYN9jP2Ravq.RHLK9KKH/t6a

EOF


sudo chown -R node_exporter: /etc/node_exporter/


# now change the node_exporter service file

cat > /usr/lib/systemd/system/node_exporter.service << EOF
[Unit]
Description=Node Exporter
Wants=network-online.target
After=network-online.target

[Service]
User=node_exporter
Group=node_exporter
Type=simple
ExecStart=/usr/local/bin/node_exporter --web.config.file=/etc/node_exporter/web.yaml
SyslogIdentifier=node_exporter
Restart=on-failure
RestartSec=60s



[Install]
WantedBy=multi-user.target
EOF


sudo systemctl daemon-reload
sudo systemctl restart node_exporter.service



# remember to add credential in /etc/prometheus/prometheus.yaml file for node exporters



```






## Enable https for prometheus srv

```
# generate a self-sgin certificate
cd /etc/prometheus/
openssl req -new -newkey rsa:2048 -days 30 -nodes -x509 -keyout host.key -out host.crt

sudo chown -R prometheus: /etc/prometheus/

cat > /etc/prometheus/web.yaml << EOF
tls_server_config:
  cert_file: /etc/prometheus/host.crt
  key_file: /etc/prometheus/host.key

basic_auth_users:
  username: $2y$10$94Xxw5G7JT.siRBD1LrtleN9iGd.xFYN9jP2Ravq.RHLK9KKH/t6a
EOF


# now you have to set below config to the /etc/prometheus/promethues.yaml

cat > /etc/prometheus/prometheus.yml << EOF

global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'prom-srv'
    static_configs:
      - targets: ["192.168.56.220:9090"]
    basic_auth:
      username: 'username'
      password: 'test'
    scheme: https
    tls_config:
      insecure_skip_verify: true

  - job_name: 'prom-srv-node-exporter'
    static_configs:
      - targets: ['192.168.56.220:9100']
    basic_auth:
      username: 'username'
      password: 'test'

  - job_name: 'debain-node-exporter'
    static_configs:
      - targets: ['192.168.56.221:9100']

EOF

```

## Enable https for node exporters

```

openssl req -new -newkey rsa:2048 -days 30 -nodes -x509 -keyout host.key -out host.crt

sudo chown -R node_exporter: /etc/node_exporter/

cat > /etc/node_exporter/web.yaml << EOF
tls_server_config:
  cert_file: /etc/node_exporter/host.crt
  key_file: /etc/node_exporter/host.key

basic_auth_users:
  username: $2y$10$94Xxw5G7JT.siRBD1LrtleN9iGd.xFYN9jP2Ravq.RHLK9KKH/t6a
EOF


# now add credential in prometheus.yaml

cat > /etc/prometheus/prometheus.yml << EOF

global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'prom-srv'
    static_configs:
      - targets: ["192.168.56.220:9090"]
    basic_auth:
      username: 'username'
      password: 'test'
    scheme: https
    tls_config:
      insecure_skip_verify: true

  - job_name: 'prom-srv-node-exporter'
    static_configs:
      - targets: ['192.168.56.220:9100']
    basic_auth:
      username: 'username'
      password: 'test'
    scheme: https
    tls_config:
      insecure_skip_verify: true

  - job_name: 'debain-node-exporter'
    static_configs:
      - targets: ['192.168.56.221:9100']

EOF



```