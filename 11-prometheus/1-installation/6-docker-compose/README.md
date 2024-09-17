### How to run

```
# generate public and private key for prometheus
openssl req -new -newkey rsa:2048 -days 30 -nodes -x509 -keyout ./prometheus-config/host.key -out ./prometheus-config/host.crt
chmod go+r host.key



# generate public and private key for grafana
openssl req -new -newkey rsa:2048 -days 30 -nodes -x509 -keyout ./grafana/file.key -out ./grafana/file.crt

chmod go+r file.key

docker compose up -d

```


# Install promtail on linux 

[ref](https://sbcode.net/grafana/install-promtail-service/)

```

curl -O -L "https://github.com/grafana/loki/releases/download/v2.4.1/promtail-linux-amd64.zip"

unzip "promtail-linux-amd64.zip"

apt install zip unzip

mv promtail-linux-amd64 /usr/local/bin/promtail


 vim /etc/promtail/config-promtail.yml

# add below config to it 
----------------------------

server:
  http_listen_port: 9080
  grpc_listen_port: 9878

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://localhost:3100/loki/api/v1/push

scrape_configs:
  - job_name: system
    static_configs:
    - targets:
        - localhost
      labels:
        job: varlogs
        __path__: /var/log/*log

-----------------------------



sudo useradd --system promtail

sudo nano /etc/systemd/system/promtail.service

------------

[Unit]
Description=Promtail service
After=network.target

[Service]
Type=simple
User=promtail
ExecStart=/usr/local/bin/promtail -config.file /etc/promtail/config-promtail.yml

[Install]
WantedBy=multi-user.target
----------------


chown -R promtail: /etc/promtail/

chown promtail: /usr/local/bin/promtail

sudo service promtail start
sudo service promtail status


```