# Setup on issable server
```sh
asterisk -rx "core show version"
python3 --version
cat /etc/os-release


# check if we user pjsip or sip
asterisk -rx "pjsip show endpoint 201"
asterisk -rx "sip show peer 201"


asterisk -rx "manager show settings"

# you have to see something like below
----
Enabled: Yes
TCP Bindaddress: 127.0.0.1:5038
----

ss -lntp | grep 5038


# 
grep -n "manager_custom.conf" /etc/asterisk/manager.conf
# must contain #include manager_custom.conf

# create random password
openssl rand -hex 32

vim /etc/asterisk/manager_custom.conf
----
[call-api]
secret = 1f8b9c54exfghstraysgfdsvrbrhtgrjnyuikmuitynkyjtubdef0123456789abcd
deny = 0.0.0.0/0.0.0.0
permit = 127.0.0.1/255.255.255.255
read = call
write = originate
displayconnects = no
----

asterisk -rx "manager reload"
asterisk -rx "manager show user call-api"

# create dialplan
grep -n "extensions_custom.conf" /etc/asterisk/extensions.conf
# you have to see something like #include extensions_custom.conf

vim /etc/asterisk/extensions_custom.conf
-----
[api-playback]
exten => s,1,NoOp(API audio call started)
 same => n,NoOp(Audio file: ${AUDIO_FILE})
 same => n,Answer()
 same => n,Wait(1)
 same => n,Playback(${AUDIO_FILE})
 same => n,NoOp(Playback status: ${PLAYBACKSTATUS})
 same => n,Hangup()
-----


# reload dialplan
asterisk -rx "dialplan reload"
asterisk -rx "dialplan show api-playback"

# you have to see Answer, Wait, Playback, Hangup


# find asterisk data dir
grep -E '^[[:space:]]*astdatadir' /etc/asterisk/asterisk.conf   # something like astdatadir => /var/lib/asterisk


mkdir -p /var/lib/asterisk/sounds/custom
chown asterisk:asterisk /var/lib/asterisk/sounds/custom
chmod 755 /var/lib/asterisk/sounds/custom



ffmpeg -i /root/notification.mp3 -ar 8000 -ac 1  -c:a pcm_s16le /root/notification.wav

ffprobe -v error -show_entries stream=codec_name,sample_rate,channels -of default=noprint_wrappers=1 /root/notification.wav


install -o asterisk -g asterisk -m 0644 /root/notification0.wav /var/lib/asterisk/sounds/custom/notification.wav

install -o asterisk -g asterisk -m 0644 /root/notification1.wav /var/lib/asterisk/sounds/custom/critical.wav

install -o asterisk -g asterisk -m 0644 /root/notification1.wav /var/lib/asterisk/sounds/custom/disaster.wav



ls -lh /var/lib/asterisk/sounds/custom/notification.wav
file /var/lib/asterisk/sounds/custom/notification.wav

ls -lh /var/lib/asterisk/sounds/custom/critical.wav
file /var/lib/asterisk/sounds/custom/critical.wav

ls -lh /var/lib/asterisk/sounds/custom/disaster.wav
file /var/lib/asterisk/sounds/custom/disaster.wav



asterisk -rx "channel originate PJSIP/201 application Playback custom/notification"
asterisk -rx "channel originate SIP/201 application Playback custom/notification"
asterisk -rx "channel originate Local/09123456789@from-internal/n application Playback custom/notification"



asterisk -rx "channel originate PJSIP/201 application Playback custom/critical"
asterisk -rx "channel originate SIP/201 application Playback custom/critical"
asterisk -rx "channel originate Local/09123456789@from-internal/n application Playback custom/critical"


chown asterisk:asterisk /var/lib/asterisk/sounds/custom/*.wav
chmod 644 /var/lib/asterisk/sounds/custom/*.wav


mkdir -p /opt/issabel-call-api
vim /opt/issabel-call-api/app.py
-------

-------

chown root:root /opt/issabel-call-api/app.py
chmod 700 /opt/issabel-call-api/app.py


python3 -m py_compile /opt/issabel-call-api/app.py
echo $?

python3 /opt/issabel-call-api/app.py



# test api
curl -i http://127.0.0.1:8090/health

# internal call
curl -X POST \
  "http://127.0.0.1:8090/call" \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "internal",
    "destination": "298",
    "audio": "notification"
  }'

```

```sh

curl -X POST \
  "http://127.0.0.1:8090/call" \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "internal",
    "destination": "298",
    "audio": "critical"
  }'


# external call
curl -X POST \
  "http://127.0.0.1:8090/call" \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "external",
    "destination": "09123456789",
    "audio": "disaster"
  }'



curl -X POST \
  "http://127.0.0.1:8090/call" \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "external",
    "destination": "09123456789",
    "audio": "critical"
  }'

```


```sh
# create systemd unit file
vim /etc/systemd/system/issabel-call-api.service
----

[Unit]
Description=Issabel Call API
After=network.target asterisk.service
Wants=asterisk.service

[Service]
Type=simple
WorkingDirectory=/opt/issabel-call-api
ExecStart=/usr/bin/python /opt/issabel-call-api/app.py

User=root
Group=root

Environment=PYTHONUNBUFFERED=1

Restart=on-failure
RestartSec=3

NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
----

systemctl daemon-reload
systemctl enable --now issabel-call-api


systemctl status issabel-call-api
journalctl -u issabel-call-api -f




curl -i \
  -X POST \
  "http://127.0.0.1:8090/call" \
  -H "Authorization: Bearer YOUR-API-TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "external",
    "destination": "09123456789",
    "audio": "notification"
  }'



curl -X POST \
  "http://192.168.18.115:8090/call" \
  -H "Authorization: Bearer 82dfgthfsdhsty53d8a6" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "external",
    "destination": "09939547647",
    "audio": "critical"
  }'
  
  
curl -X POST \
  "http://192.168.18.115:8090/call" \
  -H "Authorization: Bearer 8asdfasdf28f8571d8a6" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "external",
    "destination": "09939547647",
    "audio": "disaster"
  }'
  

curl -X POST \
  "http://192.168.18.115:8090/call" \
  -H "Authorization: Bearer 828f85" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "external",
    "destination": "09939547647",
    "audio": "notification"
  }'


```

# create zabbix media type 

#### Media type 1
Name: Phone Call Webhook


# parameters
destination={ALERT.SENDTO}
token={$APITOKEN}
url=http://192.168.1.13:8090/call
severity={EVENT.SEVERITY}


![alt text](img/1.png)


then create user and fill the send to paramenter and then create trigger action for this 
![alt text](img/2.png)