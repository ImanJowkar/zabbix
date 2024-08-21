from fastapi import FastAPI, HTTPException, Body, Path
from pydantic import BaseModel
from typing import List, Dict
from pyzabbix import ZabbixAPI
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()


zbx_url = os.getenv('zbx_url')
zbx_user = os.getenv('zbx_user')
zbx_pass =  os.getenv('zbx_pass')


app = FastAPI(
    title="My Zabbix API",
    description="This is a description of my API",
    version="1.0.0",
    docs_url="/api/docs",  # Path for Swagger UI
    redoc_url="/api/redoc",  # Optional: Path for ReDoc UI
    openapi_url="/api/openapi.json"  # Optional: Path for the OpenAPI JSON schema
)



@app.get('/api/list-hosts')
def list_hosts():
    zapi = ZabbixAPI(zbx_url)
    zapi.login(zbx_user, zbx_pass)
    hosts = zapi.host.get()
    zapi.user.logout()
    return hosts

@app.get('/api/list-hostgroup')
def list_hostgroup():
    zapi = ZabbixAPI(zbx_url)
    zapi.login(zbx_user, zbx_pass)
    host_groups = zapi.hostgroup.get(output=["groupid", "name"])
    zapi.user.logout()
    return host_groups



@app.get('/api/list-all-item')
def list_all_item(customer_id: int):
    zapi = ZabbixAPI(zbx_url)
    zapi.login(zbx_user, zbx_pass)
    items = zapi.item.get(output=["itemid", "name"],
                          tags=[{"tag": "customerid", "value": customer_id, "operator": "0"}])
    zapi.user.logout()
    return items


@app.post('/api/create-ssl-expirey-item', tags=["SSL Expiry Item"])
def create_item(customer_id: str, host_id: int, interval: str, name: str, destination: str, port: int):
    zapi = ZabbixAPI(zbx_url)
    zapi.login(zbx_user, zbx_pass)
    tags = [
    {"tag": "customerid", "value": customer_id}
    ]
    res = zapi.item.create(hostid=host_id, name=name, type=0, value_type=3, delay=interval,tags=tags,
                     key_=f"system.run[/zabbix-script/check-ssl.sh {destination} {port}]",
                     interfaceid=zapi.hostinterface.get(hostids=host_id)[0]['interfaceid'])
    zapi.user.logout()
    return res
    
@app.put('/api/update-item', tags=["SSL Expiry Item"])
def update_item(item_id: str, interval: str, name: str, destination: str, port: int):
    zapi = ZabbixAPI(zbx_url)
    zapi.login(zbx_user, zbx_pass)
    res = zapi.item.update(itemid=item_id, name=name, delay=interval,
                           key_=f"system.run[/zabbix-script/check-ssl.sh {destination} {port}]")
    zapi.user.logout()
    return res


@app.delete('/api/delete-item', tags=["SSL Expiry Item"])
def delete_item(item_id: str):
    zapi = ZabbixAPI(zbx_url)
    zapi.login(zbx_user, zbx_pass)
    response = zapi.item.delete(item_id)
    zapi.user.logout()
    return response



@app.get('/api/ssl-expiry-history', tags=["SSL Expiry Item"])
def get_ssl_history(start_time: str="2024-04-5 22:17:21", end_time: str="2024-04-5 21:42:31",  itemid: int = None, customerid: int = None):
    zapi = ZabbixAPI(zbx_url)
    zapi.login(zbx_user, zbx_pass)
    start_time = int(datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S").timestamp())
    end_time = int(datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S").timestamp())
    history = zapi.history.get(
        itemids=itemid,
        time_from=start_time,
        time_till=end_time,
        output='extend',
        limit=100)
    zapi.user.logout()
    # )2024-08-19 00:00:00
    return history

