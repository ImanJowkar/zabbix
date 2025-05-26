# Read from mysql

```
pip install zabbix_utils


```

# json path finder online
[ref](https://jsonpathfinder.com/)
```
{"Coffee_Maker": 72, "Headphones": 76, "Laptop": 84, "Smartphone": 67, "T-shirt": 59}

$.Coffee_Maker
$.Headphones
$.Laptop
$.Smartphone
$.T-shirt


```






# Create Systemd unit file
```
sudo vim /usr/lib/systemd/system/zbx_sender.service
---------------------------------------------------------------
[Unit]
Description=Zabbix Sender Service
After=network.target

[Service]
ExecStart=/home/iman/python-app-zabbix-sender/venv/bin/python /home/iman/python-app-zabbix-sender/read.py
StandardOutput=journal
StandardError=journal
Environment=DB_HOST=192.168.229.167
Environment=DB_PORT=3307
Environment=DB_USER=app
Environment=DB_PASSWORD=apppassword

[Install]
WantedBy=multi-user.target
---------------------------------------------------------------




# create a time for running systemd service

sudo vim /usr/lib/systemd/system/zbx_sender.timer
--------------------------------------------------------------
[Unit]
Description=Run zabbix_sender.service every 5 minutes

[Timer]
OnActiveSec=5min
OnUnitActiveSec=5min
Unit=zbx_sender.service

[Install]
WantedBy=timers.target
---------------------------------------------------------------

```