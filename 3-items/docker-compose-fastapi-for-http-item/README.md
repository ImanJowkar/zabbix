## how to run 

```
cd app
docker build -t app:ver1
cd ..

sudo apt-get install apache2-utils
cd nginx
htpasswd -c .htpasswd username
openssl req -newkey rsa:2048 -nodes -keyout key.pem -x509 -days 365 -out cert.pem




cd ..
docker compose up

```