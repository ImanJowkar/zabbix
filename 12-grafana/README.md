##  Run grafana as a container

```

# generate public and private key for grafana
openssl req -new -newkey rsa:2048 -days 30 -nodes -x509 -keyout ./grafana/file.key -out ./grafana/file.crt

chmod go+r grafana/file.key

```