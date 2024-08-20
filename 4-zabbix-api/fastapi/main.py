from fastapi import FastAPI, HTTPException, Body, Path
from pydantic import BaseModel
from typing import List, Dict
from pyzabbix import ZabbixAPI


app = FastAPI(
    title="My Zabbix API",
    description="This is a description of my API",
    version="1.0.0",
    docs_url="/api/docs",  # Path for Swagger UI
    redoc_url="/api/redoc",  # Optional: Path for ReDoc UI
    openapi_url="/api/openapi.json"  # Optional: Path for the OpenAPI JSON schema
)



# class Item(BaseModel):
#     hostid: int = Path()
#     description: str = None
#     price: float
#     tax: float = None

# @app.post('/api/create')
# def create(items: Item):
#     return items




@app.get('/list-hosts')
def list_hosts(hostgroup_id: int):
    zapi = ZabbixAPI("http://192.168.56.200/zabbix")
    zapi.login("Admin", "zabbix")
    # hosts = zapi.host.get(output=["hostid", "host"], groupids=hostgroup_id)
    hosts = zapi.host.get()
    zapi.user.logout()
    return hosts

@app.get('/list-hostgroup')
def list_hostgroup():
    zapi = ZabbixAPI("http://192.168.56.200/zabbix")
    zapi.login("Admin", "zabbix")
    host_groups = zapi.hostgroup.get(output=["groupid", "name"])
    zapi.user.logout()
    return host_groups



