# config


port: 
8081/tcp webui
2055/udp netflow

161/udp snmp




```sh

sudo mkdir -p /opt/akvorado
cd /opt/akvorado

sudo curl -fL \
  https://github.com/akvorado/akvorado/releases/latest/download/docker-compose-quickstart.tar.gz \
  -o akvorado.tar.gz

sudo tar -xzf akvorado.tar.gz





sudo docker compose config --quiet
sudo docker compose pull
sudo docker compose up -d --wait
sudo docker compose ps



http://SERVER-IP:8081





# check netflow traffic recived or not
sudo tcpdump -ni any 'udp port 2055'



sudo docker compose logs --tail=100 akvorado-inlet
sudo docker compose logs --tail=100 akvorado-outlet


curl -s http://127.0.0.1:8080/api/v0/inlet/metrics | grep 'akvorado_inlet_flow_input_udp_packets_total'

curl -s http://127.0.0.1:8080/api/v0/outlet/metrics \
| grep -E 'akvorado_outlet_core_(received|forwarded)_flows_total|akvorado_outlet_flow.*errors'



# check snmp works on remote device

sudo apt install -y snmp

snmpget -v2c -c 'AKVORADO-SNMP' 192.168.85.154 1.3.6.1.2.1.1.5.0


cd /opt/akvorado
sudo nano config/outlet.yaml
----
metadata:
  providers:
    - type: snmp
      credentials:
        "192.168.232.244/32":
          communities:
            - "public"
----


cd /opt/akvorado

sudo docker compose run --rm --no-deps \
  akvorado-orchestrator orchestrator \
  --check /etc/akvorado/akvorado.yaml

sudo docker compose restart akvorado-orchestrator akvorado-outlet


cd ~/akvorado
nano config/outlet.yaml
----
core:
  default-sampling-rate: 1

----

sudo docker compose restart akvorado-orchestrator akvorado-outlet

cd ~/akvorado
nano config/outlet.yaml

----
core:
  default-sampling-rate: 10

  exporter-classifiers:
    - ClassifyExporterRegex(Exporter.Name, "^([^-]+)-", "$1")
    - ClassifyRegion("europe")
    - ClassifyTenant("acme")
    - ClassifyRole("edge")

  interface-classifiers:
    - |
      ClassifyConnectivityRegex(Interface.Description, "^(?i)(transit|pni|ppni|ix):?", "$1") &&
      ClassifyProviderRegex(Interface.Description, "^\\S+?\\s(\\S+)", "$1") &&
      ClassifyExternal()
    - ClassifyExternal()
----

sudo docker compose restart akvorado-orchestrator akvorado-outlet




vim config/console.yaml
---

---
http:
  cache:
    type: redis
    server: redis:6379
database:
  saved-filters:
    # These are prepopulated filters you can select in a drop-down
    # menu. Users can add more filters interactively.
    - description: "From Netflix"
      content: >-
        InIfBoundary = external AND SrcAS = AS2906
    - description: "From GAFAM"
      content: >-
        InIfBoundary = external AND
        SrcAS IN (AS15169, AS16509, AS32934, AS6185, AS8075)
homepage-top-widgets:
  - exporter
  - src-port
  - dst-port
  - protocol
  - src-as
  - etype

homepage-graph-timerange: 24h


---

cd ~/akvorado
sudo docker compose restart akvorado-orchestrator akvorado-console


```



## config cisco devices

```sh

ip access-list standard AKVORADO-SNMP
 permit 192.168.85.74
snmp-server community public RO AKVORADO-SNMP




conf t

flow exporter AKV-EXPORT
 destination 192.168.85.74
 source Ethernet0/0
 transport udp 2055
 export-protocol netflow-v9
 template data timeout 60
 option sampler-table timeout 10
 exit

flow record AKV-RECORD
 match ipv4 source address
 match ipv4 destination address
 match ipv4 protocol
 match transport source-port
 match transport destination-port
 match interface input
 collect interface output
 collect counter bytes long
 collect counter packets long
 exit

flow monitor AKV-MONITOR
 record AKV-RECORD
 exporter AKV-EXPORT
 cache timeout active 10
 cache timeout inactive 10
 exit

interface GigabitEthernet0/0/0
 ip flow monitor AKV-MONITOR input
 exit

end


```


## config mikrotik 
```sh

web.page.get[https://sep.shaparak.ir,,443]
web.page.perf[https://sep.shaparak.ir,,443]


web.page.get[https://service.tci.ir/api/crm/pstn/v3.4/ftth/sip-phones/feasibility?nationalCode=14007071840&phoneNumber=2636520291,,443]

^HTTP/\d+(?:\.\d+)?\s+(\d{3})


min(/WEBGUI01/web.page.get[https://sep.shaparak.ir,,443],#3)<>200



{$MYSQL.DSN}   tcp://localhost:3306  
{$MYSQL.PASSWORD}   P@ssw0rd
{$MYSQL.USER}    zbx_monitor


10.2.1.57
255.255.255.240
10.2.1.49


flow exporter AKV-EXPORT
 destination 192.168.85.74
 source Ethernet0/0
 transport udp 2055
 export-protocol netflow-v9
 template data timeout 60
 exit
 
interface Ethernet0/0
 ip flow monitor AKV-MONITOR input
 exit
 
 
 
/interface wireless security-profiles
set [ find default=yes ] supplicant-identity=MikroTik
/port
set 0 name=serial0

/snmp community
add addresses=192.168.85.74/32 name=iman

/ip address
add address=192.168.85.155/24 interface=ether2 network=192.168.85.0
add address=192.168.2.1/24 interface=ether3 network=192.168.2.0
/ip dhcp-client
add interface=ether1
/ip dns
set servers=1.1.1.1
/ip firewall nat
add action=masquerade chain=srcnat
/ip route
add dst-address=0.0.0.0/0 gateway=192.168.85.2
/ip traffic-flow
set active-flow-timeout=1m enabled=yes
/ip traffic-flow target
add dst-address=192.168.85.74 src-address=192.168.85.155
/snmp
set enabled=yes
/system identity
set name=R-mik

```



# grafana dashboard

```sh


install Sankey plugin



```

