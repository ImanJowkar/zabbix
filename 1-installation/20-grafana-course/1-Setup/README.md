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

