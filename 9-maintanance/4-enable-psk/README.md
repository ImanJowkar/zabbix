# enable psk between zabbix server and zabbix proxy

```sh

# generate a random number for using as a secret in zabbix

cd /etc/zabbix
openssl rand -hex 32 > secret.psk

chmod 640 secret.psk
chown zabbix: secret.psk


# add below config to you zabbix_proxy.conf or zabbix_agent.conf

TLSConnect=psk
TLSAccept=psk
TLSPSKIdentity=proxy
TLSPSKFile=/etc/zabbix/secret.psk



# next enable encryption in zabbix UI like below image
```
![img](../img/14.png)