# Zabbix PostgreSQL HA Lab

## Patroni + etcd + HAProxy + Keepalived + TimescaleDB

This README documents a 3-node PostgreSQL HA lab for Zabbix.

> **Lab note:** This setup is intentionally simple. For production, use DNS/FQDNs, per-node TLS certificates, more restrictive firewall rules, secret management, monitoring, backups, and production-grade PostgreSQL tuning.

---

## 1. Environment

| Component | Version |
|---|---:|
| Zabbix Server | 7.0.30 |
| Rocky Linux | 9.7 |
| PostgreSQL | 18.6 |
| TimescaleDB | 2.29.x |
| Patroni | 4.1.5 |
| etcd | 3.7.x |
| HAProxy | 3.4.x |

### Topology

| Node | IP | Services |
|---|---|---|
| `pg-1` | `192.168.85.91` | PostgreSQL, Patroni, etcd0, HAProxy, Keepalived |
| `pg-2` | `192.168.85.92` | PostgreSQL, Patroni, etcd1, HAProxy, Keepalived |
| `pg-3` | `192.168.85.93` | PostgreSQL, Patroni, etcd2 |
| DB VIP | `192.168.85.95` | Floating VIP managed by Keepalived |

> Prefer DNS/FQDNs in production. `/etc/hosts` is fine for a lab.

```bash
cat >> /etc/hosts <<'EOF'
192.168.85.91 pg-1
192.168.85.92 pg-2
192.168.85.93 pg-3
EOF
```

---

## 2. Port Reference

| Port / Protocol | Purpose |
|---|---|
| `2379/tcp` | etcd Client API - used by Patroni and `etcdctl` |
| `2380/tcp` | etcd peer-to-peer / Raft traffic |
| `5432/tcp` | PostgreSQL and streaming replication |
| `8008/tcp` | Patroni REST API / HAProxy health checks |
| `5000/tcp` | HAProxy endpoint for PostgreSQL Primary |
| `5001/tcp` | HAProxy endpoint for PostgreSQL Replicas |
| `7000/tcp` | HAProxy statistics page |
| `VRRP / IP protocol 112` | Keepalived advertisements |

### Firewall - PostgreSQL / Patroni / etcd

```bash
# etcd Client API and peer communication
# PostgreSQL database/replication
# Patroni REST API
firewall-cmd --permanent \
  --add-port=2379/tcp \
  --add-port=2380/tcp \
  --add-port=5432/tcp \
  --add-port=8008/tcp

firewall-cmd --reload
```

### Firewall - HAProxy / Keepalived (`pg-1`, `pg-2`)

```bash
# HAProxy: Primary, Replica and Stats endpoints
firewall-cmd --permanent \
  --add-port=5000/tcp \
  --add-port=5001/tcp \
  --add-port=7000/tcp

# Keepalived uses VRRP (IP protocol 112), not TCP/UDP port 112
firewall-cmd --permanent --add-protocol=vrrp

firewall-cmd --reload
```

> In production, restrict these rules by source subnet/IP.

---

## 3. Install PostgreSQL 18

Run on all PostgreSQL nodes.

```bash
# Install PGDG repository
dnf install -y \
  https://download.postgresql.org/pub/repos/yum/reporpms/EL-9-x86_64/pgdg-redhat-repo-latest.noarch.rpm

# Install PostgreSQL 18
dnf install -y postgresql18-server

# Patroni must manage PostgreSQL
systemctl disable --now postgresql-18
```

> **Important:** Do **not** run `postgresql-18-setup initdb` for a new Patroni cluster. Patroni should bootstrap an empty `PGDATA` itself.

---

## 4. Install TimescaleDB

Run on all PostgreSQL nodes.

```bash
cat > /etc/yum.repos.d/timescale_timescaledb.repo <<'EOF'
[timescale_timescaledb]
name=timescale_timescaledb
baseurl=https://packagecloud.io/timescale/timescaledb/el/$releasever/$basearch
repo_gpgcheck=1
gpgcheck=0
enabled=1
gpgkey=https://packagecloud.io/timescale/timescaledb/gpgkey
sslverify=1
sslcacert=/etc/pki/tls/certs/ca-bundle.crt
metadata_expire=300
EOF

dnf clean all
dnf makecache
```

Check available versions:

```bash
dnf list timescaledb-2-postgresql-18 --showduplicates
dnf list timescaledb-2-loader-postgresql-18 --showduplicates
dnf list timescaledb-tools --showduplicates
```

Install selected versions:

```bash
dnf install -y \
  timescaledb-2-postgresql-18-2.29.2 \
  timescaledb-2-loader-postgresql-18-2.29.2 \
  timescaledb-tools-0.19.0
```

Optional version lock:

```bash
dnf install -y 'dnf-command(versionlock)'

dnf versionlock add timescaledb-2-postgresql-18
dnf versionlock add timescaledb-2-loader-postgresql-18
dnf versionlock add timescaledb-tools

dnf versionlock list
```

> Keep PostgreSQL and TimescaleDB versions aligned across all Patroni members.

---

## 5. Install and Secure etcd

Run on all three nodes:

```bash
dnf --enablerepo=pgdg-rhel9-extras install -y etcd
```

### 5.1 Create the Lab CA and etcd Certificate

Create the certificates once, for example on `pg-1`.

```bash
mkdir -p /root/etcd-cert
cd /root/etcd-cert
```

Create `cert.cnf`:

```ini
[req]
default_bits = 4096
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
countryName = IR
stateOrProvinceName = Tehran
localityName = Tehran
organizationName = ZabbixLab
commonName = etcd

[v3_req]
keyUsage = digitalSignature, keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth, clientAuth
subjectAltName = @alt_names

[alt_names]
IP.1 = 127.0.0.1
IP.2 = 192.168.85.91
IP.3 = 192.168.85.92
IP.4 = 192.168.85.93
DNS.1 = localhost
DNS.2 = pg-1
DNS.3 = pg-2
DNS.4 = pg-3
```

Create the CA:

```bash
# Root CA private key + self-signed CA certificate
openssl req -x509 -noenc -newkey rsa:4096 \
  -subj '/CN=Zabbix-Postgres-HA-CA' \
  -keyout ca_key.pem \
  -out ca_cert.pem \
  -days 36500
```

Create the etcd private key and CSR:

```bash
openssl req \
  -noenc \
  -newkey rsa:4096 \
  -keyout etcd_key.pem \
  -out etcd_cert.csr \
  -config cert.cnf
```

Sign the CSR:

```bash
openssl x509 \
  -req \
  -days 36500 \
  -in etcd_cert.csr \
  -CA ca_cert.pem \
  -CAkey ca_key.pem \
  -out etcd_cert.pem \
  -copy_extensions copy
```

Install runtime certificate files:

```bash
mkdir -p /etc/etcd/cert

cp ca_cert.pem cert.cnf etcd_cert.csr etcd_cert.pem etcd_key.pem \
  /etc/etcd/cert/

chown -R etcd:etcd /etc/etcd
chmod 0750 /etc/etcd /etc/etcd/cert
chmod 0600 /etc/etcd/cert/etcd_key.pem
chmod 0644 /etc/etcd/cert/ca_cert.pem /etc/etcd/cert/etcd_cert.pem
```

Copy runtime certs to the other nodes:

```bash
scp /etc/etcd/cert/{ca_cert.pem,etcd_cert.pem,etcd_key.pem} \
  root@192.168.85.92:/etc/etcd/cert/

scp /etc/etcd/cert/{ca_cert.pem,etcd_cert.pem,etcd_key.pem} \
  root@192.168.85.93:/etc/etcd/cert/
```

> Keep `ca_key.pem` private. The shared etcd certificate is acceptable for this lab; use per-node certificates in production.

---

### 5.2 etcd Configuration

Only the local node name/IP changes. The cluster definition remains identical.

#### `pg-1` - `/etc/etcd/etcd.conf`

```ini
[member]
ETCD_NAME=etcd0
ETCD_DATA_DIR="/var/lib/etcd/default.etcd"
ETCD_LISTEN_PEER_URLS="https://192.168.85.91:2380"
ETCD_LISTEN_CLIENT_URLS="https://localhost:2379,https://192.168.85.91:2379"

[cluster]
ETCD_INITIAL_ADVERTISE_PEER_URLS="https://192.168.85.91:2380"
ETCD_ADVERTISE_CLIENT_URLS="https://192.168.85.91:2379"
ETCD_INITIAL_CLUSTER="etcd0=https://192.168.85.91:2380,etcd1=https://192.168.85.92:2380,etcd2=https://192.168.85.93:2380"
ETCD_INITIAL_CLUSTER_STATE="new"
ETCD_INITIAL_CLUSTER_TOKEN="etcd-cluster-1"

ETCD_CERT_FILE="/etc/etcd/cert/etcd_cert.pem"
ETCD_KEY_FILE="/etc/etcd/cert/etcd_key.pem"
ETCD_PEER_TRUSTED_CA_FILE="/etc/etcd/cert/ca_cert.pem"
ETCD_PEER_CERT_FILE="/etc/etcd/cert/etcd_cert.pem"
ETCD_PEER_KEY_FILE="/etc/etcd/cert/etcd_key.pem"

[logging]
ETCD_DEBUG="false"
```

#### `pg-2`

```ini
[member]
ETCD_NAME=etcd1
ETCD_DATA_DIR="/var/lib/etcd/default.etcd"
ETCD_LISTEN_PEER_URLS="https://192.168.85.92:2380"
ETCD_LISTEN_CLIENT_URLS="https://localhost:2379,https://192.168.85.92:2379"

[cluster]
ETCD_INITIAL_ADVERTISE_PEER_URLS="https://192.168.85.92:2380"
ETCD_ADVERTISE_CLIENT_URLS="https://192.168.85.92:2379"
ETCD_INITIAL_CLUSTER="etcd0=https://192.168.85.91:2380,etcd1=https://192.168.85.92:2380,etcd2=https://192.168.85.93:2380"
ETCD_INITIAL_CLUSTER_STATE="new"
ETCD_INITIAL_CLUSTER_TOKEN="etcd-cluster-1"

ETCD_CERT_FILE="/etc/etcd/cert/etcd_cert.pem"
ETCD_KEY_FILE="/etc/etcd/cert/etcd_key.pem"
ETCD_PEER_TRUSTED_CA_FILE="/etc/etcd/cert/ca_cert.pem"
ETCD_PEER_CERT_FILE="/etc/etcd/cert/etcd_cert.pem"
ETCD_PEER_KEY_FILE="/etc/etcd/cert/etcd_key.pem"

[logging]
ETCD_DEBUG="false"
```

#### `pg-3`

```ini
[member]
ETCD_NAME=etcd2
ETCD_DATA_DIR="/var/lib/etcd/default.etcd"
ETCD_LISTEN_PEER_URLS="https://192.168.85.93:2380"
ETCD_LISTEN_CLIENT_URLS="https://localhost:2379,https://192.168.85.93:2379"

[cluster]
ETCD_INITIAL_ADVERTISE_PEER_URLS="https://192.168.85.93:2380"
ETCD_ADVERTISE_CLIENT_URLS="https://192.168.85.93:2379"
ETCD_INITIAL_CLUSTER="etcd0=https://192.168.85.91:2380,etcd1=https://192.168.85.92:2380,etcd2=https://192.168.85.93:2380"
ETCD_INITIAL_CLUSTER_STATE="new"
ETCD_INITIAL_CLUSTER_TOKEN="etcd-cluster-1"

ETCD_CERT_FILE="/etc/etcd/cert/etcd_cert.pem"
ETCD_KEY_FILE="/etc/etcd/cert/etcd_key.pem"
ETCD_PEER_TRUSTED_CA_FILE="/etc/etcd/cert/ca_cert.pem"
ETCD_PEER_CERT_FILE="/etc/etcd/cert/etcd_cert.pem"
ETCD_PEER_KEY_FILE="/etc/etcd/cert/etcd_key.pem"

[logging]
ETCD_DEBUG="false"
```

Start etcd:

```bash
chown -R etcd:etcd /etc/etcd
chmod 0750 /etc/etcd /etc/etcd/cert

systemctl enable --now etcd
journalctl -u etcd -f
```

---

### 5.3 Verify etcd

```bash
export ENDPOINTS="https://192.168.85.91:2379,https://192.168.85.92:2379,https://192.168.85.93:2379"
export CACERT="/etc/etcd/cert/ca_cert.pem"
export CERT="/etc/etcd/cert/etcd_cert.pem"
export KEY="/etc/etcd/cert/etcd_key.pem"

alias etcdctlp='etcdctl --endpoints="$ENDPOINTS" --cacert="$CACERT" --cert="$CERT" --key="$KEY"'
```

```bash
# All endpoints should be healthy
etcdctlp endpoint health

# Check etcd leader and Raft state
etcdctlp endpoint status -w table

# Verify all members
etcdctlp member list -w table
```

Important `endpoint status` columns:

- `IS LEADER` - exactly one etcd leader
- `ERRORS` - should be empty
- `RAFT TERM` - normally equal across members
- `RAFT INDEX` - equal or very close
- `RAFT APPLIED INDEX` - should track `RAFT INDEX`
- `IS LEARNER` - normal voting members should be `false`

> The etcd leader and PostgreSQL/Patroni leader are independent.

---

## 6. Install Patroni

Run on all PostgreSQL nodes.

```bash
dnf install -y patroni patroni-etcd
systemctl disable --now postgresql-18
```

### 6.1 Make etcd TLS Files Available to Patroni

```bash
mkdir -p /var/lib/pgsql/cert/etcd

cp /etc/etcd/cert/ca_cert.pem /var/lib/pgsql/cert/etcd/
cp /etc/etcd/cert/etcd_cert.pem /var/lib/pgsql/cert/etcd/
cp /etc/etcd/cert/etcd_key.pem /var/lib/pgsql/cert/etcd/

chown -R postgres:postgres /var/lib/pgsql/cert

chmod 700 /var/lib/pgsql/cert /var/lib/pgsql/cert/etcd
chmod 600 /var/lib/pgsql/cert/etcd/etcd_key.pem
chmod 644 /var/lib/pgsql/cert/etcd/ca_cert.pem
chmod 644 /var/lib/pgsql/cert/etcd/etcd_cert.pem

restorecon -Rv /var/lib/pgsql/cert
```

---

### 6.2 Patroni Configuration

Cluster-wide values should be identical on all members:

- `scope`
- `namespace`
- `etcd3`
- `bootstrap`
- authentication credentials

Node-specific values:

- `name`
- `restapi.connect_address`
- `postgresql.connect_address`

#### Base configuration - example for `pg-1`

```yaml
scope: zabbix-postgres
namespace: /service/
name: pg-1

restapi:
  listen: 0.0.0.0:8008
  connect_address: 192.168.85.91:8008

etcd3:
  protocol: https
  hosts:
    - 192.168.85.91:2379
    - 192.168.85.92:2379
    - 192.168.85.93:2379

  cacert: /var/lib/pgsql/cert/etcd/ca_cert.pem
  cert: /var/lib/pgsql/cert/etcd/etcd_cert.pem
  key: /var/lib/pgsql/cert/etcd/etcd_key.pem

bootstrap:
  dcs:
    ttl: 30
    loop_wait: 10
    retry_timeout: 10
    maximum_lag_on_failover: 1048576

    postgresql:
      # Rejoin an old Primary efficiently after failover
      use_pg_rewind: true

      # Patroni manages physical replication slots
      use_slots: true

      parameters:
        wal_level: replica
        hot_standby: "on"
        max_wal_senders: 10
        max_replication_slots: 10
        wal_keep_size: 1GB
        wal_log_hints: "on"

        max_connections: 200

        # Required for TimescaleDB
        shared_preload_libraries: "timescaledb"
        timescaledb.telemetry_level: "off"

        password_encryption: "scram-sha-256"

  initdb:
    - encoding: UTF8
    - data-checksums
    - auth-host: scram-sha-256
    - auth-local: peer

  pg_hba:
    - local all all peer
    - host replication replicator 127.0.0.1/32 scram-sha-256
    - host replication replicator 192.168.85.0/24 scram-sha-256
    - host all all 127.0.0.1/32 scram-sha-256
    - host all all 192.168.85.0/24 scram-sha-256

postgresql:
  listen: 0.0.0.0:5432
  connect_address: 192.168.85.91:5432

  data_dir: /var/lib/pgsql/18/data
  bin_dir: /usr/pgsql-18/bin
  pgpass: /var/lib/pgsql/.pgpass_patroni

  authentication:
    superuser:
      username: postgres
      password: "CHANGE_POSTGRES_PASSWORD"

    replication:
      username: replicator
      password: "CHANGE_REPLICATION_PASSWORD"

    rewind:
      username: rewind_user
      password: "CHANGE_REWIND_PASSWORD"

  parameters:
    unix_socket_directories: "/var/run/postgresql"

tags:
  noloadbalance: false
  clonefrom: false
  nostream: false
```

#### Node-specific values for `pg-2`

```yaml
name: pg-2

restapi:
  listen: 0.0.0.0:8008
  connect_address: 192.168.85.92:8008

postgresql:
  listen: 0.0.0.0:5432
  connect_address: 192.168.85.92:5432
```

#### Node-specific values for `pg-3`

```yaml
name: pg-3

restapi:
  listen: 0.0.0.0:8008
  connect_address: 192.168.85.93:8008

postgresql:
  listen: 0.0.0.0:5432
  connect_address: 192.168.85.93:5432
```

Start `pg-1` first for a clean lab bootstrap:

```bash
systemctl enable --now patroni
journalctl -u patroni -f
```

After `pg-1` becomes Leader, start Patroni on `pg-2` and `pg-3`.

```bash
systemctl enable --now patroni
```

Verify:

```bash
patronictl -c /etc/patroni/patroni.yml list
```

Expected:

```text
1 x Leader / Primary
2 x streaming Replica
Replication lag close to zero
```

---

### 6.3 Patroni REST API

```bash
# /primary returns HTTP 200 only on the current Primary
curl -i http://192.168.85.91:8008/primary
curl -i http://192.168.85.92:8008/primary
curl -i http://192.168.85.93:8008/primary

# /replica returns HTTP 200 on Replica nodes
curl -i http://192.168.85.91:8008/replica
curl -i http://192.168.85.92:8008/replica
curl -i http://192.168.85.93:8008/replica
```

---

## 7. Install HAProxy and Keepalived

Run on `pg-1` and `pg-2`.

```bash
dnf --enablerepo=pgdg-rhel9-extras install -y haproxy keepalived
```

### 7.1 HAProxy Restart Policy

Do not edit the packaged unit file directly:

```bash
systemctl edit haproxy
```

Add:

```ini
[Service]
RestartSec=5s
```

Apply:

```bash
systemctl daemon-reload
systemctl show haproxy -p Restart -p RestartUSec -p Type
```

---

### 7.2 HAProxy Configuration

Create `/etc/haproxy/haproxy.cfg` on both HAProxy nodes.

```haproxy
global
    maxconn 100

defaults
    log global
    mode tcp
    retries 2
    timeout client 30m
    timeout connect 4s
    timeout server 30m
    timeout check 5s

# HAProxy statistics page
listen stats
    mode http
    bind *:7000
    stats enable
    stats uri /
    stats realm HAProxy\ Statistics
    stats auth admin:CHANGE_THIS_PASSWORD

# Read-write traffic: only the current Patroni Primary is UP
listen production
    bind *:5000
    option httpchk OPTIONS /primary
    http-check expect status 200
    default-server inter 3s fall 3 rise 2 on-marked-down shutdown-sessions

    server pg-1 192.168.85.91:5432 maxconn 100 check port 8008
    server pg-2 192.168.85.92:5432 maxconn 100 check port 8008
    server pg-3 192.168.85.93:5432 maxconn 100 check port 8008

# Read-only traffic: Patroni Replicas are UP
listen standby
    bind *:5001
    option httpchk OPTIONS /replica
    http-check expect status 200
    default-server inter 3s fall 3 rise 2 on-marked-down shutdown-sessions

    server pg-1 192.168.85.91:5432 maxconn 100 check port 8008
    server pg-2 192.168.85.92:5432 maxconn 100 check port 8008
    server pg-3 192.168.85.93:5432 maxconn 100 check port 8008
```

Health-check logic:

```text
server pg-1 192.168.85.91:5432 check port 8008

PostgreSQL traffic -> 192.168.85.91:5432
Health check       -> 192.168.85.91:8008
```

```text
OPTIONS /primary -> HTTP 200 = current Primary
OPTIONS /replica -> HTTP 200 = Replica
```

```text
inter 3s = check every 3 seconds
fall 3   = DOWN after 3 consecutive failures
rise 2   = UP after 2 consecutive successes
```

Validate and start:

```bash
haproxy -c -f /etc/haproxy/haproxy.cfg
systemctl enable --now haproxy
systemctl status haproxy
```

---

## 8. Configure Keepalived

This lab uses two HAProxy/Keepalived nodes and unicast VRRP.

### `pg-1` - MASTER

`/etc/keepalived/keepalived.conf`

```conf
global_defs {
}

vrrp_script chk_haproxy {
    # Exit code 0 means the HAProxy process exists
    script "/usr/bin/killall -0 haproxy"
    interval 2
    weight 2
}

vrrp_instance VI_1 {
    interface ens160
    state MASTER
    priority 101
    virtual_router_id 51

    authentication {
        auth_type PASS
        auth_pass CHANGE_ME
    }

    virtual_ipaddress {
        192.168.85.95/24
    }

    unicast_src_ip 192.168.85.91

    unicast_peer {
        192.168.85.92
    }

    track_script {
        chk_haproxy
    }
}
```

### `pg-2` - BACKUP

```conf
global_defs {
}

vrrp_script chk_haproxy {
    script "/usr/bin/killall -0 haproxy"
    interval 2
    weight 2
}

vrrp_instance VI_1 {
    interface ens160
    state BACKUP
    priority 100
    virtual_router_id 51

    authentication {
        auth_type PASS
        auth_pass CHANGE_ME
    }

    virtual_ipaddress {
        192.168.85.95/24
    }

    unicast_src_ip 192.168.85.92

    unicast_peer {
        192.168.85.91
    }

    track_script {
        chk_haproxy
    }
}
```

Start:

```bash
systemctl enable --now keepalived
```

Verify VIP ownership:

```bash
ip addr | grep 192.168.85.95
```

Watch VRRP:

```bash
tcpdump -ni any proto 112
```

> Both HAProxy services should normally be running. `MASTER/BACKUP` refers to Keepalived/VIP ownership, not HAProxy process state.

---

## 9. Inspect Patroni Data Inside etcd

```bash
# Patroni DCS keys
etcdctlp get /service/zabbix-postgres/ --prefix --keys-only

# All Patroni DCS keys and values
etcdctlp get /service/zabbix-postgres/ --prefix

# Registered Patroni members
etcdctlp get /service/zabbix-postgres/members/ --prefix

# Current Patroni leader
etcdctlp get /service/zabbix-postgres/leader

# One member record
etcdctlp get /service/zabbix-postgres/members/pg-1
```

Pretty-print member JSON:

```bash
dnf install -y jq

etcdctlp get \
  /service/zabbix-postgres/members/pg-1 \
  --print-value-only | jq
```

Watch Patroni changes in real time:

```bash
etcdctlp watch /service/zabbix-postgres/ --prefix
```

> Avoid manual `put` or `del` operations on Patroni DCS keys unless you fully understand the impact.

---

## 10. Test Primary and Replica Connections

```text
192.168.85.95:5000 -> Primary / read-write
192.168.85.95:5001 -> Replicas / read-only
```

Run:

```sql
SELECT
    inet_server_addr(),
    pg_is_in_recovery();
```

Interpretation:

```text
false -> Primary
true  -> Replica
```

A write should succeed through port `5000` and fail on a Replica through port `5001`.

---

## 11. Patroni Dynamic Configuration

After bootstrap, cluster-wide settings should be changed through Patroni/DCS instead of editing `bootstrap.dcs`.

```bash
# Edit cluster-wide dynamic configuration in etcd
patronictl -c /etc/patroni/patroni.yml edit-config
```

Example failover timing:

```yaml
ttl: 20
loop_wait: 5
retry_timeout: 5
```

Verify:

```bash
patronictl -c /etc/patroni/patroni.yml show-config
```

Check for pending PostgreSQL restarts:

```bash
patronictl -c /etc/patroni/patroni.yml list
```

Restart only members that require it:

```bash
patronictl -c /etc/patroni/patroni.yml restart zabbix-postgres --pending
```

### Notes

- Change dynamic cluster configuration once from any Patroni node.
- All members read the new configuration from etcd.
- Reload-only PostgreSQL parameters do not require a restart.
- Parameters such as `max_connections`, `shared_buffers`, or `shared_preload_libraries` can require a PostgreSQL restart.
- Patroni reports those members as `Pending restart`.
- Patroni does not normally restart PostgreSQL automatically just because a parameter requires restart.

---

## 12. Create the Zabbix Database

Find the current Primary:

```bash
patronictl -c /etc/patroni/patroni.yml list
```

On the current Primary:

```bash
# Create Zabbix database role
sudo -u postgres createuser --pwprompt zabbix

# Create Zabbix database
sudo -u postgres createdb -O zabbix zabbix
```

Enable TimescaleDB:

```bash
sudo -u postgres psql -d zabbix
```

```sql
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;
\dx
\q
```

These changes replicate to the other PostgreSQL nodes through streaming replication.

---

## 13. Install PostgreSQL Client on the Zabbix Server

### Rocky / RHEL

```bash
dnf install -y postgresql18
```

### Debian / Ubuntu

```bash
sudo apt update
sudo apt install -y postgresql-client
```

Test the Primary endpoint:

```bash
psql \
  -h 192.168.85.95 \
  -p 5000 \
  -U zabbix \
  -d zabbix
```

---

## 14. Import the Zabbix Schema

Run from the Zabbix Server through HAProxy port `5000`.

```bash
# Import the main Zabbix PostgreSQL schema
zcat /usr/share/zabbix-sql-scripts/postgresql/server.sql.gz | \
  psql \
    -h 192.168.85.95 \
    -p 5000 \
    -U zabbix \
    -d zabbix \
    -W
```

Apply the TimescaleDB schema:

```bash
cat /usr/share/zabbix-sql-scripts/postgresql/timescaledb/schema.sql | \
  psql \
    -h 192.168.85.95 \
    -p 5000 \
    -U zabbix \
    -d zabbix \
    -W
```

---

## 15. Useful Operational Commands

### Patroni

```bash
patronictl -c /etc/patroni/patroni.yml list
patronictl -c /etc/patroni/patroni.yml show-config
journalctl -u patroni -f
```

### etcd

```bash
etcdctlp endpoint health
etcdctlp endpoint status -w table
etcdctlp member list -w table
```

### HAProxy

```bash
haproxy -c -f /etc/haproxy/haproxy.cfg
systemctl status haproxy
```

Stats:

```text
http://<HAProxy-IP>:7000/
```

### Keepalived

```bash
journalctl -u keepalived -f
ip addr | grep 192.168.85.95
tcpdump -ni any proto 112
```

### PostgreSQL Role Check

```sql
SELECT
    inet_server_addr(),
    pg_is_in_recovery();
```

---

## 16. HA Test Checklist

- [ ] `etcdctlp endpoint health` reports all 3 members healthy.
- [ ] Exactly one etcd member reports `IS LEADER=true`.
- [ ] `patronictl list` shows one PostgreSQL Leader and two streaming Replicas.
- [ ] Port `5000` reaches only the PostgreSQL Primary.
- [ ] Port `5001` reaches PostgreSQL Replicas.
- [ ] Keepalived VIP exists on only one HAProxy node.
- [ ] Stopping the PostgreSQL Primary triggers Patroni failover.
- [ ] HAProxy detects the new Primary through Patroni `/primary`.
- [ ] Existing clients can reconnect through the same VIP.
- [ ] Stopping HAProxy on the VIP owner causes Keepalived to move the VIP.
- [ ] Starting the failed PostgreSQL node again allows it to rejoin as a Replica.
- [ ] TimescaleDB extension exists in the Zabbix database.

---

## 17. Component Responsibilities

```text
PostgreSQL
  -> Stores data and performs streaming replication

Patroni
  -> Manages PostgreSQL lifecycle, leader election and failover

etcd
  -> Provides distributed consensus, cluster state and leader lock

HAProxy
  -> Routes clients to the current Primary or Replicas

Keepalived
  -> Provides a floating VIP for the HAProxy layer
```

Traffic path:

```text
                       Zabbix
                          |
                          v
                  192.168.85.95 VIP
                          |
                      Keepalived
                          |
                       HAProxy
                    /             \
             :5000 Primary      :5001 Replica
                    |             |
              Patroni REST API :8008
                    |             |
        +-----------+-------------+-----------+
        |                         |           |
      pg-1                      pg-2        pg-3
    Patroni                   Patroni     Patroni
       |                         |           |
   PostgreSQL                PostgreSQL  PostgreSQL
        \                        |          /
         \_______________________|_________/
                         |
                       etcd
                  quorum = 2 of 3
```

---

## 18. Production Follow-Up

Before using this design in production, review:

- PostgreSQL TLS between Zabbix and PostgreSQL.
- Per-node etcd certificates instead of a shared private key.
- Restricted firewall rules and a management-only HAProxy stats endpoint.
- PostgreSQL / TimescaleDB tuning based on RAM, CPU, IOPS and Zabbix NVPS.
- Backup and PITR with a tool such as pgBackRest.
- Monitoring and alerting for PostgreSQL, Patroni, etcd, HAProxy and Keepalived.
- Secret management instead of plaintext passwords.
- Ansible automation for repeatable and idempotent deployment.
