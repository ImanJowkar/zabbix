#!/bin/bash

echo "delete all rules in DOCKER-USER chain"
iptables -F DOCKER-USER


# restrict port 9100 for node-exporter
iptables -A DOCKER-USER -p tcp --dport 9100 -s 192.168.56.220 -j ACCEPT
iptables -A DOCKER-USER -p tcp --dport 9100 -s 0/0 -j DROP





# restrict port 9090 for prometheus itself
iptables -A DOCKER-USER -p tcp --dport 9090 -s 192.168.56.220 -j ACCEPT
iptables -A DOCKER-USER -p tcp --dport 9090 -s 0/0 -j DROP




# restric grafana port for only authorized ip address can access to the grafana web ui

iptables -A DOCKER-USER -p tcp --dport 3000 -s 192.168.56.220 -j ACCEPT
iptables -A DOCKER-USER -p tcp --dport 3000 -s 192.168.56.1 -j ACCEPT
iptables -A DOCKER-USER -p tcp --dport 3000 -s 0/0 -j DROP




echo "restart docker for build the rules again, because we remove the DOCKER-USER chain with above command"
systemctl restart docker
sleep 1

echo "here is the DOCKER-USER chain in iptables"
iptables -nvL DOCKER-USER
