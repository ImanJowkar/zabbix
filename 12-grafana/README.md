##  Run grafana as a container

```

# generate public and private key for grafana
openssl req -new -newkey rsa:2048 -days 30 -nodes -x509 -keyout ./grafana/file.key -out ./grafana/file.crt

chmod go+r grafana/file.key

```


# add plugins offline
```
wget https://grafana.com/api/plugins/yesoreyeram-infinity-datasource/versions/2.11.2/download?os=linux&arch=amd64

wget https://grafana.com/api/plugins/alexanderzobnin-zabbix-app/versions/4.5.7/download?os=linux&arch=amd64

unzip file.zip

cp -r alexanderzobnin-zabbix-app /var/lib/grafana/plugins

```