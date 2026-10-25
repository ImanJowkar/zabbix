# monitor postgresql using zabbix agent 2 active
[ref](https://www.zabbix.com/integrations/postgresql#postgresql_agent2)


```sh

# install zabbix-agent2 on all nodes

# find leader node
patronictl -c /etc/patroni/patroni.yml list

# go to leader node and create monitoring user


CREATE USER zbx_monitor
WITH PASSWORD 'CHANGE_STRONG_PASSWORD'
INHERIT;

GRANT pg_monitor TO zbx_monitor;

GRANT EXECUTE ON FUNCTION pg_catalog.pg_ls_dir(text)
TO zbx_monitor;

GRANT EXECUTE ON FUNCTION pg_catalog.pg_stat_file(text)
TO zbx_monitor;

\du zbx_monitor

# Set the connection string for the PostgreSQL instance in the {$PG.CONNSTRING.AGENT2} macro as URI, such as <protocol(host:port)>, or specify the named session - <sessionname>.



cp  ca.crt /etc/zabbix/certs/postgresql-ca.crt


mkdir -p /etc/zabbix/certs

cp /var/lib/pgsql/cert/postgresql/ca.crt \
  /etc/zabbix/certs/postgresql-ca.crt

chown root:zabbix /etc/zabbix/certs/postgresql-ca.crt
chmod 640 /etc/zabbix/certs/postgresql-ca.crt

# config agent on all node
vim /etc/zabbix/zabbix_agent2.d/plugins.d/postgresql.conf
----
Plugins.PostgreSQL.Default.TLSConnect=verify_full
Plugins.PostgreSQL.Default.TLSCAFile=/etc/zabbix/certs/postgresql-ca.crt
----

systemctl enable --now zabbix-agent2
systemctl restart zabbix-agent2

systemctl status zabbix-agent2

firewall-cmd --add-port=10050/tcp --permanent
firewall-cmd --reload



# add template `postgresql by zabbix-agent 2`
# change below macro
{$PG.CONNSTRING.AGENT2}: tcp://192.168.85.91:5432
{$PG.PASSWORD}: CHANGE_STRONG_PASSWORD
{$PG.USER}: zbx_monitor






```

# monitor ETCD
```sh

# use etcd by http template and set below macro on each host
# {$ETCD.HOST}: 192.168.85.91
# {$ETCD.SCHEME}: https
# 



```


# monitoring haproxy

```sh

# use template: HAProxy by HTTP

{$HAPROXY.STATS.HOST}   = 192.168.85.95


{$HAPROXY.STATS.PORT}   = 7000
{$HAPROXY.STATS.SCHEME} = http
{$HAPROXY.STATS.PATH}   = /
{$HAPROXY.USERNAME}     = admin
{$HAPROXY.PASSWORD}     = StrongPassword
```


# patroni

```sh






```

