from zabbix_utils import ZabbixAPI

api = ZabbixAPI(url="192.168.56.221/zabbix")
api.login(user="Admin", password="zabbix")

hosts = api.host.get()
print(hosts)


api.logout()