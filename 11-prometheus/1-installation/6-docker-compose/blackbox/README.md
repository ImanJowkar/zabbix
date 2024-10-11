# Blackbox 
```
curl 'http://localhost:9115/probe?module=icmp&target=8.8.8.8'
curl 'http://localhost:9115/probe?module=icmp&target=8.8.8.8&debug=true'


curl 'http://localhost:9115/probe?module=tcp_connect&target=8.8.8.8:54&debug=true'

curl 'http://localhost:9115/probe?module=tcp_connect&target=192.168.56.90:9101&debug=true'

curl 'http://localhost:9115/probe?module=tcp_connect&target=faradars.org:441&debug=true'
```