# R1

```
int eth 0/1
no sh
ip addr 10.10.13.1 255.255.255.0

int eth 0/0
no sh
ip addr 10.10.12.1 255.255.255.0



int seri 2/0
no sh
ip addr 1.1.14.1 255.255.255.0




router eigrp 1
network 10.10.13.1 0.0.0.0
network 10.10.12.1 0.0.0.0
network 1.1.14.1 0.0.0.0

```


# R2

```
int eth 0/2
no sh
ip addr 10.10.23.2 255.255.255.0

int eth 0/0
no sh
ip addr 10.10.12.2 255.255.255.0



router eigrp 1
network 10.10.12.2 0.0.0.0
network 10.10.23.2 0.0.0.0

```


# R3

```
int eth 0/1
no sh
ip addr 10.10.13.3 255.255.255.0

int eth 0/2
no sh
ip addr 10.10.23.3 255.255.255.0


int seri 2/0
no sh
ip addr 1.1.35.3 255.255.255.0



router eigrp 1
network 10.10.13.3 0.0.0.0
network 10.10.23.3 0.0.0.0
network 1.1.35.3 0.0.0.0
```

# R4

```
int seri 2/0
no sh
ip addr 1.1.14.4 255.255.255.0

ip route 0.0.0.0 0.0.0.0 1.1.14.1


int eth 0/0
no sh
ip addr 192.168.50.1 255.255.255.0

interface Tunnel0
 ip address 172.25.1.4 255.255.255.0
 tunnel source Serial2/0
 tunnel destination 1.1.35.5



router ospf 1
network 172.25.1.4 0.0.0.0 area 0
network 192.168.50.1 0.0.0.0 area 0
```

# R5

```
int seri 2/0
no sh
ip addr 1.1.35.5 255.255.255.0

ip route 0.0.0.0 0.0.0.0 1.1.35.3


int eth 0/0
no sh 
ip addr 192.168.60.1 255.255.255.0

interface Tunnel0
 ip address 172.25.1.5 255.255.255.0
 tunnel source Serial2/0
 tunnel destination 1.1.14.4



router ospf 1
network 172.25.1.5 0.0.0.0 area 0
network 192.168.60.1 0.0.0.0 area 0
```
