### How to run

```
openssl req -new -newkey rsa:2048 -days 30 -nodes -x509 -keyout ./prometheus-config/host.key -out ./prometheus-config/host.crt


docker compose up -d

```
