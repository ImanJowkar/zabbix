from zabbix_utils import Sender
sender = Sender(server='192.168.56.221', port=10051)
resp = sender.send_value('rockey-1', 'mykey', 40)
print(resp)


### or you can use item value

from zabbix_utils import ItemValue, Sender


items = [
    ItemValue('host1', 'item.key1', 10),
    ItemValue('host1', 'item.key2', 'Test value'),
    ItemValue('host2', 'item.key1', -1, 1702511920),
    ItemValue('host3', 'item.key1', '{"msg":"Test value"}'),
    ItemValue('host2', 'item.key1', 0, 1702511920, 100)
]

sender = Sender('127.0.0.1', 10051)
response = sender.send(items)
