# Grafana with sqlite

```sh

openssl rand -base64 48   > secrets/grafana_admin_password
chmod 600 secrets/grafana_admin_password

openssl rand -hex 32 > secrets/grafana_secret_key
chmod 600 secrets/grafana_secret_key





docker compose -f docker-compose-sqlite.yaml up -d




docker compose exec grafana grafana cli admin reset-admin-password 'NewStrongPassword'
docker compose exec grafana grafana-cli admin reset-admin-password 'NewStrongPassword'














```



# Grafana with pgsql

```sh

docker compose -f docker-compose-pgsql.yaml up -d


docker compose -f docker-compose-pgsql.yaml exec postgres psql -U grafana -d grafana
select * from data_source;



# add plugin manually

cp /home/iman/alexanderzobnin-zabbix-app-6.6.0.linux-amd64.zip /var/lib/docker/volumes/grafana_data/_data/plugins/
docker compose -f docker-compose-pgsql.yaml exec -ti grafana bash
cd /var/lib/grafana/plugins

exit

docker compose -f docker-compose-pgsql.yaml restart grafana





```