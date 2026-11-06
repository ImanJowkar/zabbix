# install grafana on ubuntu (Open Source Software)
```sh

sudo apt-get install -y apt-transport-https wget gnupg

sudo mkdir -p /etc/apt/keyrings
sudo wget -O /etc/apt/keyrings/grafana.asc https://apt.grafana.com/gpg-full.key
sudo chmod 644 /etc/apt/keyrings/grafana.asc

echo "deb [signed-by=/etc/apt/keyrings/grafana.asc] https://apt.grafana.com stable main" | sudo tee -a /etc/apt/sources.list.d/grafana.list

# Updates the list of available packages
sudo apt-get update

# Installs the latest OSS release:
sudo apt-get install grafana



```


# download deb and rpm package directly
```sh
sudo apt-get install -y adduser libfontconfig1 musl
wget https://dl.grafana.com/grafana/release/13.3.0/grafana_13.3.0_40412481033_linux_amd64.deb
sudo dpkg -i grafana_13.3.0_40412481033_linux_amd64.deb


sudo yum install -y https://dl.grafana.com/grafana/release/13.3.0/grafana_13.3.0_40412481033_linux_amd64.rpm


cp yesoreyeram-infinity-datasource-4.0.0.linux-amd64.zip /var/lib/grafana/
cp alexanderzobnin-zabbix-app-6.6.0.linux-amd64.zip /var/lib/grafana/plugins-bundled/

unzip yesoreyeram-infinity-datasource-4.0.0.linux-amd64.zip
systemctl restart grafana-server.service


unzip alexanderzobnin-zabbix-app-6.6.0.linux-amd64.zip
systemctl restart grafana-server.service

```

# Grafana with sqlite

```sh

openssl req -x509 -newkey rsa:4096 -sha256 -nodes \
  -keyout privkey.pem \
  -out fullchain.pem \
  -days 3650 \
  -subj "/CN=192.168.85.74" \
  -addext "subjectAltName=IP:192.168.85.74"



docker compose -f docker-compose-sqlite.yaml up -d



# reset admin password
docker compose exec grafana grafana cli admin reset-admin-password 'NewStrongPassword'

docker compose exec grafana grafana-cli admin reset-admin-password 'NewStrongPassword'














```

## Get wild-card certificate
```sh
sudo certbot certonly --manual --preferred-challenges dns -d "*.mydomain.com" -d mydomain.com



```


# Grafana with pgsql

```sh

docker compose -f docker-compose-pgsql.yaml up -d


docker compose -f docker-compose-pgsql.yaml exec postgres psql -U grafana -d grafana
select * from data_source;

```

# add plugin manually

```sh
cp /home/iman/alexanderzobnin-zabbix-app-6.6.0.linux-amd64.zip /var/lib/docker/volumes/grafana_data/_data/plugins/
docker compose -f docker-compose-pgsql.yaml exec -ti grafana bash
cd /var/lib/grafana/plugins
unzip alexanderzobnin-zabbix-app-6.6.0.linux-amd64.zip

exit

docker compose -f docker-compose-pgsql.yaml restart grafana


```

